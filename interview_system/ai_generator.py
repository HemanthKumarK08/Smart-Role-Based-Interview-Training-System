"""
AI Question Generator — Google Gemini via REST (HTTPS).
Avoids gRPC SSL issues on Windows / Python 3.14.
"""

import json
import os
import ssl
import time
import urllib.error
import urllib.request
from dotenv import load_dotenv

try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_SCRIPT_DIR, ".env")

load_dotenv(_ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
USE_AI = os.getenv("USE_AI", "true").strip().lower() in ("1", "true", "yes")

_api_checked = False
_api_works = False


def _api_url():
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={API_KEY}"
    )


def _extract_text(data):
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")
    parts = candidates[0].get("content", {}).get("parts") or []
    if not parts or "text" not in parts[0]:
        raise RuntimeError("Gemini returned empty text.")
    return parts[0]["text"].strip()


def _rest_call(prompt, timeout=20):
    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Add it to interview_system/.env"
        )

    payload = json.dumps(
        {"contents": [{"parts": [{"text": prompt}]}]}
    ).encode("utf-8")

    request = urllib.request.Request(
        _api_url(),
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(
        request, timeout=timeout, context=SSL_CONTEXT
    ) as response:
        return json.loads(response.read().decode("utf-8"))


def _non_retryable_error(exc):
    msg = str(exc).lower()
    markers = (
        "certificate",
        "ssl",
        "handshake",
        "certificate_verify_failed",
        "api key",
        "permission",
        "403",
        "401",
        "404",
        "not found",
        "invalid",
        "quota",
        "resource_exhausted",
    )
    return any(m in msg for m in markers)


def ai_available(force_check=False):
    """Quick check: can we reach Gemini? Cached after first call."""
    global _api_checked, _api_works

    if not USE_AI or not API_KEY:
        return False

    if _api_checked and not force_check:
        return _api_works

    try:
        data = _rest_call(
            'Reply with JSON only: {"status":"ok"}',
            timeout=12,
        )
        text = _extract_text(data)
        _api_works = "ok" in text.lower() or "status" in text.lower()
    except Exception as exc:
        print(f"[AI] API unavailable: {exc}")
        _api_works = False

    _api_checked = True
    return _api_works


def check_api():
    """Verify Gemini API. Returns (ok: bool, message: str)."""
    if not API_KEY:
        return False, (
            "GEMINI_API_KEY is missing.\n"
            "Create interview_system/.env with:\n"
            "GEMINI_API_KEY=your_key_from_aistudio.google.com"
        )
    if not USE_AI:
        return False, (
            "AI is disabled (USE_AI=false in .env).\n"
            "Interviews use saved questions from the database."
        )

    try:
        data = _rest_call(
            'Reply with JSON only: {"status":"ok"}',
            timeout=15,
        )
        text = _extract_text(data)
        if not text:
            return False, f"Gemini ({GEMINI_MODEL}) returned an empty response."
        return True, f"Gemini API OK (model: {GEMINI_MODEL}, REST/HTTPS)."
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, _format_http_error(exc.code, body)
    except Exception as exc:
        return False, _format_error(exc)


def _format_http_error(code, body):
    if code == 429:
        hint = "Quota exceeded — wait or use USE_AI=false to use saved questions."
    elif code in (401, 403):
        hint = "Invalid API key — get a new one at https://aistudio.google.com/apikey"
    elif code == 404:
        hint = f"Model '{GEMINI_MODEL}' not found. Set GEMINI_MODEL=gemini-1.5-flash"
    else:
        hint = body[:200] if body else "Check your API key and internet."
    return False, f"Gemini HTTP {code}: {hint}"


def _format_error(exc):
    msg = str(exc).lower()
    if "certificate" in msg or "ssl" in msg or "handshake" in msg:
        hint = (
            "SSL certificate error on this PC.\n"
            "Run: pip install certifi\n"
            "Or set USE_AI=false in .env to use saved questions (no Google API)."
        )
    elif "429" in msg or "quota" in msg:
        hint = "API quota exceeded. Set USE_AI=false or wait and retry."
    elif "timed out" in msg or "timeout" in msg:
        hint = "Connection timed out. Check internet or set USE_AI=false."
    else:
        hint = "Set USE_AI=false in .env to start interviews without Google API."
    return False, f"Gemini API failed: {exc}\n\n{hint}"


def _safe_json_parse(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No valid JSON found in Gemini response.")
    return json.loads(text[start : end + 1])


def _generate(prompt, retries=2):
    last_error = None
    max_attempts = 1 if not ai_available() else retries

    for attempt in range(max_attempts):
        try:
            data = _rest_call(prompt, timeout=25)
            raw_text = _extract_text(data)
            if not raw_text:
                raise RuntimeError("Gemini response is blank.")
            result = _safe_json_parse(raw_text)
            if isinstance(result, dict):
                return result
            raise RuntimeError("Gemini returned malformed JSON.")
        except Exception as exc:
            last_error = exc
            print(f"[AI Retry {attempt + 1}/{max_attempts}] {exc}")
            if _non_retryable_error(exc):
                break
            time.sleep(1)

    raise RuntimeError(
        f"AI generation failed after {max_attempts} attempt(s): {last_error}"
    )


def generate_mcq(role, difficulty):
    prompt = f"""
Generate ONE unique multiple-choice interview question.

Role: {role}
Difficulty: {difficulty}

Rules:
- Practical and technical, role-specific
- 4 options, one correct answer
- Return ONLY valid JSON

JSON format:
{{
    "question": "",
    "option_a": "",
    "option_b": "",
    "option_c": "",
    "option_d": "",
    "correct_answer": "A"
}}
"""
    result = _generate(prompt)
    required = [
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
    ]
    for key in required:
        if key not in result:
            raise ValueError(f"Missing field in MCQ response: {key}")
    if result["correct_answer"] not in ("A", "B", "C", "D"):
        raise ValueError("Invalid correct answer.")
    return result


def generate_technical(role, difficulty):
    prompt = f"""
Generate ONE unique technical interview question.

Role: {role}
Difficulty: {difficulty}

Rules:
- Typed answer, practical, role-specific, not MCQ
- Minimum 3 keywords in comma-separated list
- Return ONLY valid JSON

JSON format:
{{
    "question": "",
    "keywords": "keyword1, keyword2, keyword3"
}}
"""
    result = _generate(prompt)
    for key in ("question", "keywords"):
        if key not in result:
            raise ValueError(f"Missing field in Technical response: {key}")
    return result


def generate_hr(role):
    prompt = f"""
Generate ONE unique HR interview question.

Role: {role}

Rules:
- Soft skills, teamwork, behavior — not technical
- Return ONLY valid JSON

JSON format:
{{
    "question": "",
    "keywords": "confidence, teamwork, communication"
}}
"""
    result = _generate(prompt)
    for key in ("question", "keywords"):
        if key not in result:
            raise ValueError(f"Missing field in HR response: {key}")
    return result


def generate_mcq_set(role, difficulty, count=5):
    return [generate_mcq(role, difficulty) for _ in range(count)]


def generate_technical_set(role, difficulty, count=3):
    return [generate_technical(role, difficulty) for _ in range(count)]


def generate_hr_set(role, count=2):
    return [generate_hr(role) for _ in range(count)]


if __name__ == "__main__":
    ok, msg = check_api()
    print(msg)
    if ok:
        print(generate_mcq("Data Analyst", "Easy"))
