"""Utility functions for validation, text processing, and scoring."""

import hashlib
import re
from collections import Counter

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PUNCTUATION_PATTERN = re.compile(r"[^\w\s]")

POSITIVE_WORDS = [
    "teamwork",
    "leadership",
    "learning",
    "growth",
    "challenge",
    "collaboration",
    "initiative",
    "dedication",
    "motivation",
    "passion",
]


def hash_password(password):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    """Validate email format using regex."""
    return bool(EMAIL_PATTERN.match(email.strip()))


def clean_text(text):
    """Convert to lowercase and remove punctuation."""
    if not text:
        return ""
    text = text.lower()
    text = PUNCTUATION_PATTERN.sub(" ", text)
    return " ".join(text.split())


def parse_keywords(keywords_str):
    """Parse comma-separated keywords into a list."""
    if not keywords_str:
        return []
    return [k.strip().lower() for k in keywords_str.split(",") if k.strip()]


def evaluate_keywords(student_answer, admin_keywords):
    """
    Count matched keywords in student answer.
    Returns (matched_count, total_keywords, score_percentage).
    """
    keywords = parse_keywords(admin_keywords)
    if not keywords:
        return 0, 0, 0.0

    cleaned = clean_text(student_answer)
    matched = sum(1 for kw in keywords if kw in cleaned)
    score = (matched / len(keywords)) * 100
    return matched, len(keywords), round(score, 2)


def get_technical_feedback(score):
    """Return feedback label for technical round score."""
    if score <= 30:
        return "Poor"
    if score <= 60:
        return "Average"
    return "Good"


def count_words(text):
    """Count words in text."""
    if not text or not text.strip():
        return 0
    return len(text.strip().split())


def evaluate_hr_response(student_answer, expected_keywords):
    """
    Evaluate HR response using keyword matching, word count, and confidence scoring.
    Returns dict with scores and feedback.
    """
    keyword_score = 0.0
    keywords = parse_keywords(expected_keywords)
    if keywords:
        _, _, keyword_score = evaluate_keywords(student_answer, expected_keywords)

    word_count = count_words(student_answer)
    word_count_ok = word_count >= 20
    word_score = min(100, (word_count / 20) * 100) if word_count > 0 else 0

    cleaned = clean_text(student_answer)
    positive_found = sum(1 for w in POSITIVE_WORDS if w in cleaned)
    length_bonus = min(30, len(student_answer) / 10)
    confidence_score = min(
        100, (positive_found * 15) + length_bonus + (20 if word_count_ok else 0)
    )

    final_score = round((keyword_score * 0.5) + (word_score * 0.25) + (confidence_score * 0.25), 2)

    feedback_parts = []
    if keyword_score >= 61:
        feedback_parts.append("Strong keyword coverage.")
    elif keyword_score >= 31:
        feedback_parts.append("Moderate keyword coverage.")
    else:
        feedback_parts.append("Try to include role-relevant themes in your answer.")

    if not word_count_ok:
        feedback_parts.append(f"Answer too short ({word_count}/20 words minimum).")
    else:
        feedback_parts.append("Good answer length.")

    if confidence_score >= 61:
        feedback_parts.append("Confident and positive tone.")
    else:
        feedback_parts.append("Add more positive, professional language.")

    return {
        "keyword_score": keyword_score,
        "word_count": word_count,
        "word_count_ok": word_count_ok,
        "confidence_score": round(confidence_score, 2),
        "final_score": final_score,
        "feedback": " ".join(feedback_parts),
    }
