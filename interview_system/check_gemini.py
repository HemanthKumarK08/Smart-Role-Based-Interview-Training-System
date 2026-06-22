"""Quick Gemini API diagnostic. Run from interview_system folder."""

from ai_generator import check_api

if __name__ == "__main__":
    ok, message = check_api()
    print(message)
    raise SystemExit(0 if ok else 1)
