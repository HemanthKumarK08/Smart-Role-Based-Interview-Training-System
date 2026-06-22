"""Feedback engine: scoring, strengths, weaknesses, suggestions."""

import csv
import json
import os
from datetime import datetime

from database import get_connection
import interview_engine


def calculate_final_score(mcq_score, technical_score, hr_score, coding_score=None):
    """Calculate overall score: average of active rounds."""
    if coding_score is not None:
        return round((mcq_score + technical_score + coding_score + hr_score) / 4, 2)
    return round((mcq_score + technical_score + hr_score) / 3, 2)


def find_strengths(mcq_score, technical_score, hr_score, coding_score=None):
    """Identify high-scoring areas."""
    strengths = []
    scores = {
        "MCQ Round": mcq_score,
        "Technical Round": technical_score,
        "HR Round": hr_score,
    }
    if coding_score is not None:
        scores["Coding Output Round"] = coding_score

    for name, score in scores.items():
        if score >= 70:
            strengths.append(f"{name}: Excellent performance ({score}%)")
        elif score >= 50:
            strengths.append(f"{name}: Good performance ({score}%)")
    if not strengths:
        strengths.append("Keep practicing — improvement is possible in all areas.")
    return strengths


def find_weaknesses(mcq_score, technical_score, hr_score, coding_score=None):
    """Identify low-scoring areas."""
    weaknesses = []
    scores = {
        "MCQ Round": mcq_score,
        "Technical Round": technical_score,
        "HR Round": hr_score,
    }
    if coding_score is not None:
        scores["Coding Output Round"] = coding_score

    for name, score in scores.items():
        if score < 50:
            weaknesses.append(f"{name}: Needs improvement ({score}%)")
    if not weaknesses:
        weaknesses.append("No major weaknesses detected.")
    return weaknesses


def generate_suggestions(mcq_score, technical_score, hr_score, role_name="", coding_score=None):
    """Generate personalized study suggestions."""
    suggestions = []

    if mcq_score < 50:
        suggestions.append(
            f"Review core concepts for {role_name or 'your target role'} — focus on fundamentals."
        )
        suggestions.append("Practice more MCQ-style aptitude and domain questions.")

    if technical_score < 50:
        suggestions.append("Practice explaining technical concepts in your own words.")
        suggestions.append("Study key terms: OOP, data structures, APIs, databases.")
        if "data" in role_name.lower() or "analyst" in role_name.lower():
            suggestions.append("Practice SQL joins, aggregations, and data visualization.")
        if "web" in role_name.lower() or "developer" in role_name.lower():
            suggestions.append("Review HTML, CSS, JavaScript, and framework basics.")
        if "android" in role_name.lower():
            suggestions.append("Study Activities, Intents, and Android lifecycle.")

    if coding_score is not None and coding_score < 50:
        suggestions.append("Practice reading code snippets and predicting their output.")
        suggestions.append("Understand loops, lists, logic operators, and function scope in Python/JS.")

    if hr_score < 50:
        suggestions.append("Prepare STAR-format answers for behavioral questions.")
        suggestions.append(
            "Practice answers with at least 20 words covering teamwork and goals."
        )

    all_scores = [mcq_score, technical_score, hr_score]
    if coding_score is not None:
        all_scores.append(coding_score)
    if all(s >= 70 for s in all_scores):
        suggestions.append("Outstanding performance! Try harder difficulty levels.")

    if not suggestions:
        suggestions.append("Maintain consistent practice across all rounds.")

    return suggestions


def build_feedback_text(mcq_score, technical_score, hr_score, role_name="", coding_score=None):
    """Build complete feedback string."""
    strengths = find_strengths(mcq_score, technical_score, hr_score, coding_score)
    weaknesses = find_weaknesses(mcq_score, technical_score, hr_score, coding_score)
    suggestions = generate_suggestions(mcq_score, technical_score, hr_score, role_name, coding_score)

    lines = [
        "=== INTERVIEW FEEDBACK REPORT ===",
        "",
        "STRENGTHS:",
    ]
    lines.extend(f"  • {s}" for s in strengths)
    lines.append("")
    lines.append("AREAS TO IMPROVE:")
    lines.extend(f"  • {w}" for w in weaknesses)
    lines.append("")
    lines.append("SUGGESTIONS:")
    lines.extend(f"  • {s}" for s in suggestions)

    return "\n".join(lines)


def save_results(
    student_id,
    role_id,
    mcq_score,
    technical_score,
    hr_score,
    feedback,
    session_data=None,
    difficulty=None,
    coding_score=0.0,
    has_coding=False,
):
    """Save interview results to database."""
    overall = calculate_final_score(mcq_score, technical_score, hr_score, coding_score if has_coding else None)
    status = "PASS" if overall >= 60 else "FAIL"

    # Fetch strength/weakness analysis
    import interview_engine
    session = interview_engine.get_active_session()
    
    strong_str = "None"
    weak_str = "None"
    if session:
        strong_list = [f"{k} Round ({v} good answers)" for k, v in session.strong_areas.items()]
        if strong_list:
            strong_str = ", ".join(strong_list)
        weak_list = [f"{k} Round ({v} needs improvement)" for k, v in session.weak_areas.items()]
        if weak_list:
            weak_str = ", ".join(weak_list)
    else:
        # Fallback based on raw scores
        strengths = find_strengths(mcq_score, technical_score, hr_score, coding_score if has_coding else None)
        weaknesses = find_weaknesses(mcq_score, technical_score, hr_score, coding_score if has_coding else None)
        strong_str = ", ".join(strengths)
        weak_str = ", ".join(weaknesses)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO results (
            student_id, role_id, mcq_score, technical_score, coding_score,
            hr_score, overall_score, percentage, status, feedback, created_at,
            session_data, difficulty, strong_areas, weak_areas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            role_id,
            mcq_score,
            technical_score,
            coding_score,
            hr_score,
            overall,
            overall,
            status,
            feedback,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session_data,
            difficulty,
            strong_str,
            weak_str,
        ),
    )
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return result_id, overall


def finalize_interview():
    """Complete interview: calculate scores, save results, return report."""
    session = interview_engine.get_active_session()
    if not session:
        return None

    mcq = interview_engine.calculate_mcq_score()
    technical = interview_engine.calculate_technical_score()
    has_coding = getattr(session, "has_coding_round", False)
    coding = interview_engine.calculate_coding_score() if has_coding else 0.0
    hr = interview_engine.calculate_hr_score()
    feedback = build_feedback_text(
        mcq, technical, hr, session.role_name, coding_score=coding if has_coding else None
    )
    session_data = interview_engine.build_session_snapshot()

    result_id, overall = save_results(
        session.student_id,
        session.role_id,
        mcq,
        technical,
        hr,
        feedback,
        session_data=session_data,
        difficulty=session.difficulty,
        coding_score=coding,
        has_coding=has_coding,
    )

    # Fetch student name to log activity
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE id = ?", (session.student_id,))
        row = cursor.fetchone()
        student_name = row["name"] if row else "Student"
        conn.close()
        
        from database import log_activity
        log_activity(f"Student {student_name} completed {session.role_name} interview")
    except Exception as e:
        print(f"Error logging activity: {e}")

    return {
        "result_id": result_id,
        "mcq_score": mcq,
        "technical_score": technical,
        "coding_score": coding,
        "hr_score": hr,
        "overall_score": overall,
        "feedback": feedback,
        "role_name": session.role_name,
        "difficulty": session.difficulty,
        "session_data": session_data,
    }


def get_session_review(result_id, student_id):
    """Load saved Q&A review for a completed interview."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT session_data, role_id
        FROM results
        WHERE id = ? AND student_id = ?
        """,
        (result_id, student_id),
    )
    row = cursor.fetchone()
    conn.close()

    if not row or not row["session_data"]:
        return None

    try:
        return json.loads(row["session_data"])
    except json.JSONDecodeError:
        return None


def format_session_review_text(review):
    """Turn session review dict into readable text for the UI."""
    if not review:
        return "No answer review saved for this session."

    lines = [
        f"Role: {review.get('role_name', '—')}",
        f"Difficulty: {review.get('difficulty', '—')}",
        "",
    ]

    if review.get("mcq"):
        lines.append("=== MCQ — Correct answers ===")
        for i, item in enumerate(review["mcq"], 1):
            lines.append(f"\n{i}. {item.get('question', '')}")
            lines.append(
                f"   A) {item.get('option_a', '')}  B) {item.get('option_b', '')}"
            )
            lines.append(
                f"   C) {item.get('option_c', '')}  D) {item.get('option_d', '')}"
            )
            lines.append(f"   Your answer: {item.get('your_answer', '—')}")
            mark = "✓" if item.get("was_correct") else "✗"
            lines.append(
                f"   {mark} Correct: {item.get('ideal_answer', '')}"
            )

    if review.get("technical"):
        lines.append("\n=== Technical — Model answers ===")
        for i, item in enumerate(review["technical"], 1):
            lines.append(f"\n{i}. {item.get('question', '')}")
            lines.append(f"   Your answer: {item.get('your_answer', '—')}")
            if item.get("score") is not None:
                lines.append(f"   Score: {item.get('score')}%")
            lines.append(f"   Perfect answer: {item.get('ideal_answer', '')}")

    if review.get("coding"):
        lines.append("\n=== Coding Output Round — Correct answers ===")
        for i, item in enumerate(review["coding"], 1):
            lines.append(f"\n{i}. {item.get('question', '')}")
            snippet = (item.get("code_snippet") or "").strip()
            if snippet:
                lines.append("   ── Code snippet ──────────────────────")
                for code_line in snippet.splitlines():
                    lines.append(f"   {code_line}")
                lines.append("   ───────────────────────────────────────")
            lines.append(
                f"   A) {item.get('option_a', '')}  B) {item.get('option_b', '')}"
            )
            lines.append(
                f"   C) {item.get('option_c', '')}  D) {item.get('option_d', '')}"
            )
            lines.append(f"   Your answer: {item.get('your_answer', '—')}")
            mark = "✓" if item.get("was_correct") else "✗"
            lines.append(
                f"   {mark} Correct: {item.get('ideal_answer', '')}"
            )

    if review.get("hr"):
        lines.append("\n=== HR — Model answers ===")
        for i, item in enumerate(review["hr"], 1):
            lines.append(f"\n{i}. {item.get('question', '')}")
            lines.append(f"   Your answer: {item.get('your_answer', '—')}")
            if item.get("score") is not None:
                lines.append(f"   Score: {item.get('score')}%")
            lines.append(f"   Perfect answer: {item.get('ideal_answer', '')}")

    return "\n".join(lines)


def view_history(student_id):
    """View previous interview reports for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT res.*, r.role_name
        FROM results res
        JOIN roles r ON res.role_id = r.id
        WHERE res.student_id = ?
        ORDER BY res.created_at DESC
        """,
        (student_id,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def export_report(result_id, filepath=None):
    """Export a single result report to CSV."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT res.*, s.name, s.email, r.role_name
        FROM results res
        JOIN students s ON res.student_id = s.id
        JOIN roles r ON res.role_id = r.id
        WHERE res.id = ?
        """,
        (result_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "Result not found."

    if not filepath:
        reports_dir = os.path.join(os.path.dirname(__file__), "assets")
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(
            reports_dir,
            f"report_{result_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Student",
                "Email",
                "Role",
                "MCQ Score",
                "Technical Score",
                "HR Score",
                "Overall Score",
                "Date",
            ]
        )
        writer.writerow(
            [
                row["name"],
                row["email"],
                row["role_name"],
                row["mcq_score"],
                row["technical_score"],
                row["hr_score"],
                row["overall_score"],
                row["created_at"],
            ]
        )
        writer.writerow([])
        writer.writerow(["Feedback"])
        for line in row["feedback"].split("\n"):
            writer.writerow([line])

    return True, filepath
