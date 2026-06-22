# """Interview engine: MCQ, Technical, and HR rounds."""

# import random
# from datetime import datetime

# from database import get_connection
# from utils import evaluate_keywords, get_technical_feedback, evaluate_hr_response


# class InterviewSession:
#     """Holds state for an active interview."""

#     def __init__(self, student_id, role_id, role_name, difficulty):
#         self.student_id = student_id
#         self.role_id = role_id
#         self.role_name = role_name
#         self.difficulty = difficulty
#         self.mcq_questions = []
#         self.mcq_answers = []
#         self.mcq_score = 0.0
#         self.technical_questions = []
#         self.technical_answers = []
#         self.technical_scores = []
#         self.technical_score = 0.0
#         self.hr_questions = []
#         self.hr_answers = []
#         self.hr_scores = []
#         self.hr_score = 0.0
#         self.current_round = 0
#         self.current_index = 0


# _active_session = None


# def get_active_session():
#     return _active_session


# def start_interview(student_id, role_id, role_name, difficulty):
#     """Initialize a new interview session."""
#     global _active_session
#     _active_session = InterviewSession(student_id, role_id, role_name, difficulty)
#     _active_session.mcq_questions = get_mcq_questions(role_id, difficulty, count=5)
#     _active_session.technical_questions = get_technical_questions(
#         role_id, difficulty, count=3
#     )
#     _active_session.hr_questions = get_hr_questions(role_id, count=2)

#     if not _active_session.mcq_questions:
#         return False, "No MCQ questions available for this role and difficulty."
#     if not _active_session.technical_questions:
#         return False, "No technical questions available."
#     if not _active_session.hr_questions:
#         return False, "No HR questions available."

#     _active_session.current_round = 1
#     _active_session.current_index = 0
#     return True, "Interview started."


# def get_mcq_questions(role_id, difficulty, count=5):
#     """Fetch random MCQ questions."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT * FROM questions
#         WHERE role_id = ? AND question_type = 'mcq' AND difficulty = ?
#         """,
#         (role_id, difficulty),
#     )
#     rows = [dict(r) for r in cursor.fetchall()]
#     conn.close()

#     if len(rows) <= count:
#         random.shuffle(rows)
#         return rows
#     return random.sample(rows, count)


# def submit_mcq_answer(question_id, user_answer):
#     """Submit and validate MCQ answer."""
#     session = _active_session
#     if not session:
#         return False, 0

#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT correct_answer FROM questions WHERE id = ?", (question_id,)
#     )
#     row = cursor.fetchone()
#     conn.close()

#     if not row:
#         return False, 0

#     correct = row["correct_answer"].upper()
#     user = user_answer.strip().upper()
#     is_correct = user == correct

#     session.mcq_answers.append(
#         {"question_id": question_id, "user_answer": user, "correct": is_correct}
#     )
#     return is_correct, 1 if is_correct else 0


# def calculate_mcq_score():
#     """Calculate MCQ round percentage score."""
#     session = _active_session
#     if not session or not session.mcq_questions:
#         return 0.0

#     correct = sum(1 for a in session.mcq_answers if a["correct"])
#     total = len(session.mcq_questions)
#     session.mcq_score = round((correct / total) * 100, 2) if total else 0.0
#     return session.mcq_score


# def get_technical_questions(role_id, difficulty, count=3):
#     """Fetch random technical questions."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT * FROM questions
#         WHERE role_id = ? AND question_type = 'technical' AND difficulty = ?
#         """,
#         (role_id, difficulty),
#     )
#     rows = [dict(r) for r in cursor.fetchall()]
#     conn.close()

#     if len(rows) <= count:
#         random.shuffle(rows)
#         return rows
#     return random.sample(rows, count)


# def submit_technical_answer(question_id, student_answer, keywords):
#     """Evaluate technical answer using keyword matching."""
#     matched, total, score = evaluate_keywords(student_answer, keywords)
#     feedback = get_technical_feedback(score)

#     session = _active_session
#     if session:
#         session.technical_answers.append(
#             {
#                 "question_id": question_id,
#                 "answer": student_answer,
#                 "score": score,
#                 "matched": matched,
#                 "total": total,
#                 "feedback": feedback,
#             }
#         )
#         session.technical_scores.append(score)

#     return {
#         "score": score,
#         "matched_keywords": matched,
#         "total_keywords": total,
#         "feedback": feedback,
#     }


# def calculate_technical_score():
#     """Average technical round scores."""
#     session = _active_session
#     if not session or not session.technical_scores:
#         session.technical_score = 0.0
#         return 0.0
#     session.technical_score = round(
#         sum(session.technical_scores) / len(session.technical_scores), 2
#     )
#     return session.technical_score


# def get_hr_questions(role_id, count=2):
#     """Fetch random HR questions."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT * FROM questions
#         WHERE role_id = ? AND question_type = 'hr'
#         """,
#         (role_id,),
#     )
#     rows = [dict(r) for r in cursor.fetchall()]
#     conn.close()

#     if len(rows) <= count:
#         random.shuffle(rows)
#         return rows
#     return random.sample(rows, count)


# def submit_hr_answer(question_id, student_answer, expected_keywords):
#     """Evaluate HR answer."""
#     result = evaluate_hr_response(student_answer, expected_keywords)

#     session = _active_session
#     if session:
#         session.hr_answers.append(
#             {
#                 "question_id": question_id,
#                 "answer": student_answer,
#                 "evaluation": result,
#             }
#         )
#         session.hr_scores.append(result["final_score"])

#     return result


# def calculate_hr_score():
#     """Average HR round scores."""
#     session = _active_session
#     if not session or not session.hr_scores:
#         session.hr_score = 0.0
#         return 0.0
#     session.hr_score = round(sum(session.hr_scores) / len(session.hr_scores), 2)
#     return session.hr_score


# def advance_round():
#     """Move to next interview round."""
#     session = _active_session
#     if not session:
#         return None

#     session.current_round += 1
#     session.current_index = 0
#     return session.current_round


# def get_current_question():
#     """Get current question based on round and index."""
#     session = _active_session
#     if not session:
#         return None

#     if session.current_round == 1:
#         questions = session.mcq_questions
#     elif session.current_round == 2:
#         questions = session.technical_questions
#     elif session.current_round == 3:
#         questions = session.hr_questions
#     else:
#         return None

#     if session.current_index < len(questions):
#         return questions[session.current_index]
#     return None


# def next_question():
#     """Advance to next question in current round."""
#     session = _active_session
#     if not session:
#         return False

#     session.current_index += 1

#     if session.current_round == 1:
#         total = len(session.mcq_questions)
#     elif session.current_round == 2:
#         total = len(session.technical_questions)
#     else:
#         total = len(session.hr_questions)

#     return session.current_index < total


##Updated interview_engine.py to use new AI generator and feedback functions.
"""Interview engine: MCQ, Technical, and HR rounds."""

# import json
# import random
# from datetime import datetime

# from database import get_connection
# from utils import evaluate_keywords, get_technical_feedback, evaluate_hr_response
# from ai_generator import (
#     ai_available,
#     generate_mcq_set,
#     generate_technical_set,
#     generate_hr_set,
# )


# class InterviewSession:
#     """Holds state for an active interview."""

#     def __init__(self, student_id, role_id, role_name, difficulty):
#         self.student_id = student_id
#         self.role_id = role_id
#         self.role_name = role_name
#         self.difficulty = difficulty
#         self.mcq_questions = []
#         self.mcq_answers = []
#         self.mcq_score = 0.0
#         self.technical_questions = []
#         self.technical_answers = []
#         self.technical_scores = []
#         self.technical_score = 0.0
#         self.hr_questions = []
#         self.hr_answers = []
#         self.hr_scores = []
#         self.hr_score = 0.0
#         self.current_round = 0
#         self.current_index = 0


# _active_session = None


# def get_active_session():
#     return _active_session


# # def start_interview(student_id, role_id, role_name, difficulty):
# #     """Initialize a new interview session."""
# #     global _active_session
# #     _active_session = InterviewSession(student_id, role_id, role_name, difficulty)

# #     # --- AI generation (with DB fallback on failure) ---
# #     try:
# #         _active_session.mcq_questions = generate_mcq_set(
# #             role_name,
# #             difficulty,
# #             count=5,
# #         )
# #     except Exception as exc:
# #         print(f"AI MCQ generation failed: {exc}")
# #         _active_session.mcq_questions = get_mcq_questions(role_id, difficulty, count=5)

# #     try:
# #         _active_session.technical_questions = generate_technical_set(
# #             role_name,
# #             difficulty,
# #             count=3,
# #         )
# #     except Exception as exc:
# #         print(f"AI technical generation failed: {exc}")
# #         _active_session.technical_questions = get_technical_questions(
# #             role_id, difficulty, count=3
# #         )

# #     try:
# #         _active_session.hr_questions = generate_hr_set(
# #             role_name,
# #             count=2,
# #         )
# #     except Exception as exc:
# #         print(f"AI HR generation failed: {exc}")
# #         _active_session.hr_questions = get_hr_questions(role_id, count=2)

# #     # Assign synthetic IDs so the UI can reference questions by q["id"]
# #     for i, q in enumerate(_active_session.mcq_questions, start=1):
# #         q["id"] = i

# #     for i, q in enumerate(_active_session.technical_questions, start=100):
# #         q["id"] = i

# #     for i, q in enumerate(_active_session.hr_questions, start=200):
# #         q["id"] = i

# #     if not _active_session.mcq_questions:
# #         return False, "No MCQ questions available for this role and difficulty."
# #     if not _active_session.technical_questions:
# #         return False, "No technical questions available."
# #     if not _active_session.hr_questions:
# #         return False, "No HR questions available."

# #     _active_session.current_round = 1
# #     _active_session.current_index = 0
# #     return True, "Interview started."

# def start_interview(student_id, role_id, role_name, difficulty):
#     """Initialize a new interview session."""
#     global _active_session
#     _active_session = InterviewSession(
#         student_id,
#         role_id,
#         role_name,
#         difficulty
#     )

#     used_fallback = False
#     use_ai = ai_available()

#     if use_ai:
#         try:
#             print("Generating AI MCQ...")
#             _active_session.mcq_questions = generate_mcq_set(
#                 role_name, difficulty, count=5
#             )
#         except Exception as exc:
#             print(f"AI MCQ generation failed: {exc}")
#             _active_session.mcq_questions = get_mcq_questions(
#                 role_id, difficulty, count=5
#             )
#             used_fallback = True
#     else:
#         print("Using saved MCQ questions (AI off or unavailable).")
#         _active_session.mcq_questions = get_mcq_questions(
#             role_id, difficulty, count=5
#         )
#         used_fallback = True

#     if use_ai and not used_fallback:
#         try:
#             print("Generating AI Technical...")
#             _active_session.technical_questions = generate_technical_set(
#                 role_name, difficulty, count=5
#             )
#         except Exception as exc:
#             print(f"AI technical generation failed: {exc}")
#             _active_session.technical_questions = get_technical_questions(
#                 role_id, difficulty, count=5
#             )
#             used_fallback = True
#     else:
#         print("Using saved technical questions.")
#         _active_session.technical_questions = get_technical_questions(
#             role_id, difficulty, count=5
#         )
#         if use_ai:
#             used_fallback = True

#     if use_ai and not used_fallback:
#         try:
#             print("Generating AI HR...")
#             _active_session.hr_questions = generate_hr_set(role_name, count=5)
#         except Exception as exc:
#             print(f"AI HR generation failed: {exc}")
#             _active_session.hr_questions = get_hr_questions(role_id, count=5)
#             used_fallback = True
#     else:
#         print("Using saved HR questions.")
#         _active_session.hr_questions = get_hr_questions(role_id, count=5)
#         if use_ai:
#             used_fallback = True

#     # Synthetic IDs
#     for i, q in enumerate(_active_session.mcq_questions, start=1):
#         q["id"] = i

#     for i, q in enumerate(_active_session.technical_questions, start=100):
#         q["id"] = i

#     for i, q in enumerate(_active_session.hr_questions, start=200):
#         q["id"] = i

#     if not _active_session.mcq_questions:
#         return False, (
#             f"No MCQ questions available.\n\n"
#             f"Please contact admin to add MCQ questions for "
#             f"{role_name} ({difficulty})."
#         )

#     if not _active_session.technical_questions:
#        return False, (
#             f"No technical questions available.\n\n"
#             f"Please contact admin to add technical questions for "
#             f"{role_name} ({difficulty})."
#         )

#     if not _active_session.hr_questions:
#        return False, (
#         f"No HR questions available.\n\n"
#         f"Please contact admin to add HR questions for "
#         f"{role_name} ({difficulty})."
#     )

#     _active_session.current_round = 1
#     _active_session.current_index = 0

#     if used_fallback:
#         return True, (
#             "Interview started using saved questions "
#             "(Gemini API unavailable)."
#         )
#     return True, "Interview started."

# def get_mcq_questions(role_id, difficulty, count=5):
#     """Fetch random MCQ questions from DB (used as fallback)."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT * FROM questions
#         WHERE role_id = ? AND question_type = 'mcq' AND difficulty = ?
#         """,
#         (role_id, difficulty),
#     )
#     rows = [dict(r) for r in cursor.fetchall()]
#     conn.close()

#     if len(rows) <= count:
#         random.shuffle(rows)
#         return rows
#     return random.sample(rows, count)


# def submit_mcq_answer(question_id, user_answer):
#     """Submit and validate MCQ answer using the active session (no DB lookup)."""
#     session = _active_session
#     if not session:
#         return False, 0

#     # Find the question in the session instead of querying the DB
#     question = next(
#         (q for q in session.mcq_questions if q.get("id") == question_id), None
#     )
#     if not question:
#         return False, 0

#     correct = question["correct_answer"].strip().upper()
#     user = user_answer.strip().upper()
#     is_correct = user == correct

#     session.mcq_answers.append(
#         {"question_id": question_id, "user_answer": user, "correct": is_correct}
#     )
#     return is_correct, 1 if is_correct else 0


# def calculate_mcq_score():
#     """Calculate MCQ round percentage score."""
#     session = _active_session
#     if not session or not session.mcq_questions:
#         return 0.0

#     correct = sum(1 for a in session.mcq_answers if a["correct"])
#     total = len(session.mcq_questions)
#     session.mcq_score = round((correct / total) * 100, 2) if total else 0.0
#     return session.mcq_score


# def get_technical_questions(role_id, difficulty, count=5):
#     """Fetch random technical questions from DB (used as fallback)."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT * FROM questions
#         WHERE role_id = ? AND question_type = 'technical' AND difficulty = ?
#         """,
#         (role_id, difficulty),
#     )
#     rows = [dict(r) for r in cursor.fetchall()]
#     conn.close()

#     if len(rows) <= count:
#         random.shuffle(rows)
#         return rows
#     return random.sample(rows, count)


# def submit_technical_answer(question_id, student_answer, keywords):
#     """Evaluate technical answer using keyword matching."""
#     matched, total, score = evaluate_keywords(student_answer, keywords)
#     feedback = get_technical_feedback(score)

#     session = _active_session
#     if session:
#         session.technical_answers.append(
#             {
#                 "question_id": question_id,
#                 "answer": student_answer,
#                 "score": score,
#                 "matched": matched,
#                 "total": total,
#                 "feedback": feedback,
#             }
#         )
#         session.technical_scores.append(score)

#     return {
#         "score": score,
#         "matched_keywords": matched,
#         "total_keywords": total,
#         "feedback": feedback,
#     }


# def calculate_technical_score():
#     """Average technical round scores."""
#     session = _active_session
#     if not session or not session.technical_scores:
#         session.technical_score = 0.0
#         return 0.0
#     session.technical_score = round(
#         sum(session.technical_scores) / len(session.technical_scores), 2
#     )
#     return session.technical_score


# def get_hr_questions(role_id, count=5):
#     """Fetch random HR questions from DB (used as fallback)."""
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT * FROM questions
#         WHERE role_id = ? AND question_type = 'hr'
#         """,
#         (role_id,),
#     )
#     rows = [dict(r) for r in cursor.fetchall()]
#     conn.close()

#     if len(rows) <= count:
#         random.shuffle(rows)
#         return rows
#     return random.sample(rows, count)


# def submit_hr_answer(question_id, student_answer, expected_keywords):
#     """Evaluate HR answer."""
#     result = evaluate_hr_response(student_answer, expected_keywords)

#     session = _active_session
#     if session:
#         session.hr_answers.append(
#             {
#                 "question_id": question_id,
#                 "answer": student_answer,
#                 "evaluation": result,
#             }
#         )
#         session.hr_scores.append(result["final_score"])

#     return result


# def calculate_hr_score():
#     """Average HR round scores."""
#     session = _active_session
#     if not session or not session.hr_scores:
#         session.hr_score = 0.0
#         return 0.0
#     session.hr_score = round(sum(session.hr_scores) / len(session.hr_scores), 2)
#     return session.hr_score


# def advance_round():
#     """Move to next interview round."""
#     session = _active_session
#     if not session:
#         return None

#     session.current_round += 1
#     session.current_index = 0
#     return session.current_round


# def get_current_question():
#     """Get current question based on round and index."""
#     session = _active_session
#     if not session:
#         return None

#     if session.current_round == 1:
#         questions = session.mcq_questions
#     elif session.current_round == 2:
#         questions = session.technical_questions
#     elif session.current_round == 3:
#         questions = session.hr_questions
#     else:
#         return None

#     if session.current_index < len(questions):
#         return questions[session.current_index]
#     return None


# def next_question():
#     """Advance to next question in current round."""
#     session = _active_session
#     if not session:
#         return False

#     session.current_index += 1

#     if session.current_round == 1:
#         total = len(session.mcq_questions)
#     elif session.current_round == 2:
#         total = len(session.technical_questions)
#     else:
#         total = len(session.hr_questions)

#     return session.current_index < total


# def _mcq_option_text(question, letter):
#     key = f"option_{letter.lower()}"
#     return (question.get(key) or "").strip()


# def build_session_snapshot():
#     """JSON snapshot of questions, student answers, and ideal answers."""
#     session = _active_session
#     if not session:
#         return None

#     def _find_mcq_answer(qid):
#         for a in session.mcq_answers:
#             if a.get("question_id") == qid:
#                 return a
#         return None

#     def _find_tech_answer(qid):
#         for a in session.technical_answers:
#             if a.get("question_id") == qid:
#                 return a
#         return None

#     def _find_hr_answer(qid):
#         for a in session.hr_answers:
#             if a.get("question_id") == qid:
#                 return a
#         return None

#     mcq_items = []
#     for q in session.mcq_questions:
#         correct = (q.get("correct_answer") or "A").strip().upper()
#         ans = _find_mcq_answer(q.get("id"))
#         user = (ans.get("user_answer") if ans else "") or "—"
#         ideal = (q.get("ideal_answer") or "").strip()
#         if not ideal:
#             opt_text = _mcq_option_text(q, correct)
#             ideal = f"{correct}) {opt_text}" if opt_text else correct

#         mcq_items.append(
#             {
#                 "question": q.get("question", ""),
#                 "option_a": q.get("option_a", ""),
#                 "option_b": q.get("option_b", ""),
#                 "option_c": q.get("option_c", ""),
#                 "option_d": q.get("option_d", ""),
#                 "correct_answer": correct,
#                 "your_answer": user,
#                 "was_correct": bool(ans and ans.get("correct")),
#                 "ideal_answer": ideal,
#             }
#         )

#     tech_items = []
#     for q in session.technical_questions:
#         ans = _find_tech_answer(q.get("id"))
#         keywords = (q.get("keywords") or "").strip()
#         ideal = (q.get("ideal_answer") or "").strip()
#         if not ideal:
#             ideal = f"Include these key points: {keywords}"

#         tech_items.append(
#             {
#                 "question": q.get("question", ""),
#                 "keywords": keywords,
#                 "your_answer": (ans.get("answer") if ans else "") or "—",
#                 "score": ans.get("score") if ans else None,
#                 "ideal_answer": ideal,
#             }
#         )

#     hr_items = []
#     for q in session.hr_questions:
#         ans = _find_hr_answer(q.get("id"))
#         keywords = (q.get("keywords") or "").strip()
#         ideal = (q.get("ideal_answer") or "").strip()
#         if not ideal:
#             ideal = f"Cover these themes: {keywords}"

#         hr_items.append(
#             {
#                 "question": q.get("question", ""),
#                 "keywords": keywords,
#                 "your_answer": (ans.get("answer") if ans else "") or "—",
#                 "score": ans.get("score") if ans else None,
#                 "ideal_answer": ideal,
#             }
#         )

#     payload = {
#         "role_name": session.role_name,
#         "difficulty": session.difficulty,
#         "mcq": mcq_items,
#         "technical": tech_items,
#         "hr": hr_items,
#     }
#     return json.dumps(payload, ensure_ascii=False)



import json
import random
from datetime import datetime

from database import get_connection
from utils import evaluate_keywords, get_technical_feedback, evaluate_hr_response
from ai_generator import (
    ai_available,
    generate_mcq_set,
    generate_technical_set,
    generate_hr_set,
)


class InterviewSession:
    """Holds state for an active interview."""

    def __init__(self, student_id, role_id, role_name, difficulty):
        self.student_id = student_id
        self.role_id = role_id
        self.role_name = role_name
        self.difficulty = difficulty
        self.mcq_questions = []
        self.mcq_answers = []
        self.mcq_score = 0.0
        self.technical_questions = []
        self.technical_answers = []
        self.technical_scores = []
        self.technical_score = 0.0
        self.coding_questions = []
        self.coding_answers = []
        self.coding_score = 0.0
        self.coding_scores = []
        self.hr_questions = []
        self.hr_answers = []
        self.hr_scores = []
        self.hr_score = 0.0
        self.current_round = 0
        self.current_index = 0
        self.has_coding_round = False
        
        # --- Interview State & Tracking Variables ---
        self.total_questions = 0
        self.answered_questions = 0
        self.review_data = []
        self.weak_areas = {}
        self.strong_areas = {}
        self.percentage = 0
        self.status = "FAIL"


_active_session = None


def get_active_session():
    return _active_session


def get_coding_questions(role_id, difficulty, count=5):
    """Fetch random coding questions from DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM questions
        WHERE role_id = ? AND question_type = 'coding' AND difficulty = ?
        """,
        (role_id, difficulty),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if len(rows) <= count:
        random.shuffle(rows)
        return rows
    return random.sample(rows, count)


def start_interview(student_id, role_id, role_name, difficulty):
    """Initialize a new interview session."""
    global _active_session
    _active_session = InterviewSession(
        student_id,
        role_id,
        role_name,
        difficulty
    )

    # Check database to see if role has coding round
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT has_coding_round FROM roles WHERE id = ?", (role_id,))
    role_row = cursor.fetchone()
    conn.close()
    
    has_coding = role_row["has_coding_round"] if role_row else 0
    _active_session.has_coding_round = bool(has_coding)

    used_fallback = False
    use_ai = ai_available()

    if use_ai:
        try:
            print("Generating AI MCQ...")
            _active_session.mcq_questions = generate_mcq_set(
                role_name, difficulty, count=5
            )
        except Exception as exc:
            print(f"AI MCQ generation failed: {exc}")
            _active_session.mcq_questions = get_mcq_questions(
                role_id, difficulty, count=5
            )
            used_fallback = True
    else:
        print("Using saved MCQ questions (AI off or unavailable).")
        _active_session.mcq_questions = get_mcq_questions(
            role_id, difficulty, count=5
        )
        used_fallback = True

    if use_ai and not used_fallback:
        try:
            print("Generating AI Technical...")
            _active_session.technical_questions = generate_technical_set(
                role_name, difficulty, count=5
            )
        except Exception as exc:
            print(f"AI technical generation failed: {exc}")
            _active_session.technical_questions = get_technical_questions(
                role_id, difficulty, count=5
            )
            used_fallback = True
    else:
        print("Using saved technical questions.")
        _active_session.technical_questions = get_technical_questions(
            role_id, difficulty, count=5
        )
        if use_ai:
            used_fallback = True

    if _active_session.has_coding_round:
        print("Using saved coding questions.")
        _active_session.coding_questions = get_coding_questions(
            role_id, difficulty, count=5
        )

    if use_ai and not used_fallback:
        try:
            print("Generating AI HR...")
            _active_session.hr_questions = generate_hr_set(role_name, count=5)
        except Exception as exc:
            print(f"AI HR generation failed: {exc}")
            _active_session.hr_questions = get_hr_questions(role_id, count=5)
            used_fallback = True
    else:
        print("Using saved HR questions.")
        _active_session.hr_questions = get_hr_questions(role_id, count=5)
        if use_ai:
            used_fallback = True

    # Synthetic IDs
    for i, q in enumerate(_active_session.mcq_questions, start=1):
        q["id"] = i

    for i, q in enumerate(_active_session.technical_questions, start=100):
        q["id"] = i

    for i, q in enumerate(_active_session.hr_questions, start=200):
        q["id"] = i

    if _active_session.has_coding_round:
        for i, q in enumerate(_active_session.coding_questions, start=300):
            q["id"] = i

    if not _active_session.mcq_questions:
        return False, (
            f"No MCQ questions available.\n\n"
            f"Please contact admin to add MCQ questions for "
            f"{role_name} ({difficulty})."
        )

    if not _active_session.technical_questions:
        return False, (
            f"No technical questions available.\n\n"
            f"Please contact admin to add technical questions for "
            f"{role_name} ({difficulty})."
        )

    if _active_session.has_coding_round and not _active_session.coding_questions:
        return False, (
            f"No coding output questions available.\n\n"
            f"Please contact admin to add coding questions for "
            f"{role_name} ({difficulty})."
        )

    if not _active_session.hr_questions:
        return False, (
            f"No HR questions available.\n\n"
            f"Please contact admin to add HR questions for "
            f"{role_name} ({difficulty})."
        )

    # --- Setup Progress Engine ---
    _active_session.total_questions = (
        len(_active_session.mcq_questions)
        + len(_active_session.technical_questions)
        + len(_active_session.hr_questions)
    )
    if _active_session.has_coding_round:
        _active_session.total_questions += len(_active_session.coding_questions)

    _active_session.current_round = 1
    _active_session.current_index = 0

    if used_fallback:
        return True, (
            "Interview started using saved questions "
            "(Gemini API unavailable)."
        )
    return True, "Interview started."


def get_mcq_questions(role_id, difficulty, count=5):
    """Fetch random MCQ questions from DB (used as fallback)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM questions
        WHERE role_id = ? AND question_type = 'mcq' AND difficulty = ?
        """,
        (role_id, difficulty),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if len(rows) <= count:
        random.shuffle(rows)
        return rows
    return random.sample(rows, count)


def submit_mcq_answer(question_id, user_answer):
    """Submit and validate MCQ answer using the active session."""
    session = _active_session
    if not session:
        return False, 0

    question = next(
        (q for q in session.mcq_questions if q.get("id") == question_id), None
    )
    if not question:
        return False, 0

    correct = question["correct_answer"].strip().upper()
    user = user_answer.strip().upper()
    is_correct = user == correct

    session.mcq_answers.append(
        {"question_id": question_id, "user_answer": user, "correct": is_correct}
    )

    # --- Live Metric Aggregation ---
    session.answered_questions += 1

    session.review_data.append({
        "type": "MCQ",
        "question": question["question"],
        "user_answer": user_answer,
        "correct_answer": question["correct_answer"],
        "is_correct": is_correct
    })

    topic = "MCQ"
    if is_correct:
        session.strong_areas[topic] = session.strong_areas.get(topic, 0) + 1
    else:
        session.weak_areas[topic] = session.weak_areas.get(topic, 0) + 1

    return is_correct, 1 if is_correct else 0


def calculate_mcq_score():
    """Calculate MCQ round percentage score."""
    session = _active_session
    if not session or not session.mcq_questions:
        return 0.0

    correct = sum(1 for a in session.mcq_answers if a["correct"])
    total = len(session.mcq_questions)
    session.mcq_score = round((correct / total) * 100, 2) if total else 0.0
    return session.mcq_score


def get_technical_questions(role_id, difficulty, count=5):
    """Fetch random technical questions from DB (used as fallback)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM questions
        WHERE role_id = ? AND question_type = 'technical' AND difficulty = ?
        """,
        (role_id, difficulty),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if len(rows) <= count:
        random.shuffle(rows)
        return rows
    return random.sample(rows, count)


def submit_technical_answer(question_id, student_answer, keywords):
    """Evaluate technical answer using keyword matching."""
    matched, total, score = evaluate_keywords(student_answer, keywords)
    feedback = get_technical_feedback(score)

    session = _active_session
    if session:
        session.technical_answers.append(
            {
                "question_id": question_id,
                "answer": student_answer,
                "score": score,
                "matched": matched,
                "total": total,
                "feedback": feedback,
            }
        )
        session.technical_scores.append(score)

        # --- Performance Tracking (Assumes score is on a 0-10 scale) ---
        session.answered_questions += 1

        question = next(
            (q for q in session.technical_questions if q.get("id") == question_id), 
            {"question": "Unknown Technical Question"}
        )

        session.review_data.append({
            "type": "Technical",
            "question": question["question"],
            "user_answer": student_answer,
            "score": score
        })

        topic = "Technical"
        # Use >= 60 if your evaluate_keywords module shifts directly to a 0-100 scale
        if score >= 60:
            session.strong_areas[topic] = session.strong_areas.get(topic, 0) + 1
        else:
            session.weak_areas[topic] = session.weak_areas.get(topic, 0) + 1

    return {
        "score": score,
        "matched_keywords": matched,
        "total_keywords": total,
        "feedback": feedback,
    }


def calculate_technical_score():
    """Average technical round scores."""
    session = _active_session
    if not session or not session.technical_scores:
        session.technical_score = 0.0
        return 0.0
    session.technical_score = round(
        sum(session.technical_scores) / len(session.technical_scores), 2
    )
    return session.technical_score


def submit_coding_answer(question_id, user_answer):
    """Submit and validate coding answer using the active session."""
    session = _active_session
    if not session:
        return False, 0

    question = next(
        (q for q in session.coding_questions if q.get("id") == question_id), None
    )
    if not question:
        return False, 0

    correct = question["correct_answer"].strip().upper()
    user = user_answer.strip().upper()
    is_correct = user == correct

    session.coding_answers.append(
        {"question_id": question_id, "user_answer": user, "correct": is_correct}
    )

    # --- Live Metric Aggregation ---
    session.answered_questions += 1

    session.review_data.append({
        "type": "Coding",
        "question": question["question"],
        "code_snippet": question.get("code_snippet"),
        "user_answer": user_answer,
        "correct_answer": question["correct_answer"],
        "is_correct": is_correct
    })

    topic = "Coding"
    if is_correct:
        session.strong_areas[topic] = session.strong_areas.get(topic, 0) + 1
    else:
        session.weak_areas[topic] = session.weak_areas.get(topic, 0) + 1

    return is_correct, 1 if is_correct else 0


def calculate_coding_score():
    """Calculate Coding round percentage score."""
    session = _active_session
    if not session or not session.coding_questions:
        return 0.0

    correct = sum(1 for a in session.coding_answers if a["correct"])
    total = len(session.coding_questions)
    session.coding_score = round((correct / total) * 100, 2) if total else 0.0
    return session.coding_score


def get_hr_questions(role_id, count=5):
    """Fetch random HR questions from DB (used as fallback)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM questions
        WHERE role_id = ? AND question_type = 'hr'
        """,
        (role_id,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if len(rows) <= count:
        random.shuffle(rows)
        return rows
    return random.sample(rows, count)


def submit_hr_answer(question_id, student_answer, expected_keywords):
    """Evaluate HR answer."""
    result = evaluate_hr_response(student_answer, expected_keywords)
    score = result.get("final_score", 0)

    session = _active_session
    if session:
        session.hr_answers.append(
            {
                "question_id": question_id,
                "answer": student_answer,
                "evaluation": result,
            }
        )
        session.hr_scores.append(score)

        # --- Performance Tracking (Assumes score is on a 0-10 scale) ---
        session.answered_questions += 1

        question = next(
            (q for q in session.hr_questions if q.get("id") == question_id), 
            {"question": "Unknown HR Question"}
        )

        session.review_data.append({
            "type": "HR",
            "question": question["question"],
            "user_answer": student_answer,
            "score": score
        })

        topic = "HR"
        # Use >= 60 if your evaluate_hr_response module outputs 0-100 natively
        if score >= 60:
            session.strong_areas[topic] = session.strong_areas.get(topic, 0) + 1
        else:
            session.weak_areas[topic] = session.weak_areas.get(topic, 0) + 1

    return result


def calculate_hr_score():
    """Average HR round scores."""
    session = _active_session
    if not session or not session.hr_scores:
        session.hr_score = 0.0
        return 0.0
    session.hr_score = round(sum(session.hr_scores) / len(session.hr_scores), 2)
    return session.hr_score


def advance_round():
    """Move to next interview round."""
    session = _active_session
    if not session:
        return None

    session.current_round += 1
    session.current_index = 0
    return session.current_round


def get_current_question():
    """Get current question based on round and index."""
    session = _active_session
    if not session:
        return None

    has_coding = getattr(session, "has_coding_round", False)
    if session.current_round == 1:
        questions = session.mcq_questions
    elif session.current_round == 2:
        questions = session.technical_questions
    elif session.current_round == 3:
        questions = session.coding_questions if has_coding else session.hr_questions
    elif session.current_round == 4 and has_coding:
        questions = session.hr_questions
    else:
        return None

    if session.current_index < len(questions):
        return questions[session.current_index]
    return None


def next_question():
    """Advance to next question in current round."""
    session = _active_session
    if not session:
        return False

    session.current_index += 1

    has_coding = getattr(session, "has_coding_round", False)
    if session.current_round == 1:
        total = len(session.mcq_questions)
    elif session.current_round == 2:
        total = len(session.technical_questions)
    elif session.current_round == 3:
        total = len(session.coding_questions) if has_coding else len(session.hr_questions)
    elif session.current_round == 4 and has_coding:
        total = len(session.hr_questions)
    else:
        return False

    return session.current_index < total


def _mcq_option_text(question, letter):
    key = f"option_{letter.lower()}"
    return (question.get(key) or "").strip()


def build_session_snapshot():
    """JSON snapshot of questions, student answers, and ideal answers."""
    session = _active_session
    if not session:
        return None

    def _find_mcq_answer(qid):
        return next((a for a in session.mcq_answers if a.get("question_id") == qid), None)

    def _find_tech_answer(qid):
        return next((a for a in session.technical_answers if a.get("question_id") == qid), None)

    def _find_coding_answer(qid):
        return next((a for a in session.coding_answers if a.get("question_id") == qid), None)

    def _find_hr_answer(qid):
        return next((a for a in session.hr_answers if a.get("question_id") == qid), None)

    mcq_items = []
    for q in session.mcq_questions:
        correct = (q.get("correct_answer") or "A").strip().upper()
        ans = _find_mcq_answer(q.get("id"))
        user = (ans.get("user_answer") if ans else "") or "—"
        ideal = (q.get("ideal_answer") or "").strip()
        if not ideal:
            opt_text = _mcq_option_text(q, correct)
            ideal = f"{correct}) {opt_text}" if opt_text else correct

        mcq_items.append({
            "question": q.get("question", ""),
            "option_a": q.get("option_a", ""),
            "option_b": q.get("option_b", ""),
            "option_c": q.get("option_c", ""),
            "option_d": q.get("option_d", ""),
            "correct_answer": correct,
            "your_answer": user,
            "was_correct": bool(ans and ans.get("correct")),
            "ideal_answer": ideal,
        })

    tech_items = []
    for q in session.technical_questions:
        ans = _find_tech_answer(q.get("id"))
        keywords = (q.get("keywords") or "").strip()
        ideal = (q.get("ideal_answer") or "").strip()
        if not ideal:
            ideal = f"Include these key points: {keywords}"

        tech_items.append({
            "question": q.get("question", ""),
            "keywords": keywords,
            "your_answer": (ans.get("answer") if ans else "") or "—",
            "score": ans.get("score") if ans else None,
            "ideal_answer": ideal,
        })

    coding_items = []
    for q in session.coding_questions:
        correct = (q.get("correct_answer") or "A").strip().upper()
        ans = _find_coding_answer(q.get("id"))
        user = (ans.get("user_answer") if ans else "") or "—"
        ideal = (q.get("ideal_answer") or "").strip()
        if not ideal:
            opt_text = _mcq_option_text(q, correct)
            ideal = f"{correct}) {opt_text}" if opt_text else correct

        coding_items.append({
            "question": q.get("question", ""),
            "code_snippet": q.get("code_snippet", ""),
            "option_a": q.get("option_a", ""),
            "option_b": q.get("option_b", ""),
            "option_c": q.get("option_c", ""),
            "option_d": q.get("option_d", ""),
            "correct_answer": correct,
            "your_answer": user,
            "was_correct": bool(ans and ans.get("correct")),
            "ideal_answer": ideal,
        })

    hr_items = []
    for q in session.hr_questions:
        ans = _find_hr_answer(q.get("id"))
        keywords = (q.get("keywords") or "").strip()
        ideal = (q.get("ideal_answer") or "").strip()
        if not ideal:
            ideal = f"Cover these themes: {keywords}"

        hr_items.append({
            "question": q.get("question", ""),
            "keywords": keywords,
            "your_answer": (ans.get("answer") if ans else "") or "—",
            "score": ans.get("score") if ans else None,
            "ideal_answer": ideal,
        })

    payload = {
        "role_name": session.role_name,
        "difficulty": session.difficulty,
        "mcq": mcq_items,
        "technical": tech_items,
        "coding": coding_items,
        "hr": hr_items,
    }

    return json.dumps(payload, ensure_ascii=False)


def finalize_interview():
    """Calculates metrics across standardized scales and locks pass/fail status."""
    session = _active_session
    if not session:
        return None

    mcq_component = calculate_mcq_score()
    tech_component = calculate_technical_score()
    
    has_coding = getattr(session, "has_coding_round", False)
    if has_coding:
        coding_component = calculate_coding_score()
        hr_component = calculate_hr_score()
        overall_score = round(
            (mcq_component + tech_component + coding_component + hr_component) / 4,
            2
        )
    else:
        hr_component = calculate_hr_score()
        overall_score = round(
            (mcq_component + tech_component + hr_component) / 3,
            2
        )

    session.percentage = overall_score
    session.status = "PASS" if overall_score >= 60 else "FAIL"

    return session.status


def get_progress():
    """Calculate direct completion percentage for UI progress bars."""
    session = _active_session
    if not session or session.total_questions == 0:
        return 0
    return int((session.answered_questions / session.total_questions) * 100)


def get_review_data():
    """Retrieve raw session logs for generation of evaluation reviews."""
    session = _active_session
    if not session:
        return []
    return session.review_data


def get_strength_analysis():
    """Fetch structured performance analysis dicts."""
    session = _active_session
    if not session:
        return {}, {}
    return session.strong_areas, session.weak_areas

def reset_session():
    """
    Reset current interview session.
    Used when user exits interview early
    or finishes interview.
    """
    global _active_session
    _active_session = None