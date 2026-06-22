"""Admin module: role management, question management, analytics."""

from database import get_connection, log_activity
from utils import parse_keywords
from question_import import load_questions_file
from docx import Document
from utils import hash_password


# --- Role Management ---


def add_role(role_name, has_coding_round=0):
    """Add a new job role."""
    if not role_name or not role_name.strip():
        return False, "Role name is required."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role_name.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, "Role already exists."

    try:
        cursor.execute(
            "INSERT INTO roles (role_name, has_coding_round) VALUES (?, ?)",
            (role_name.strip(), has_coding_round),
        )
        conn.commit()
        log_activity(f"Admin created new role: {role_name.strip()}")
        return True, "Role added successfully."
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def update_role(role_id, new_name, has_coding_round=0):
    """Update an existing role."""
    if not new_name or not new_name.strip():
        return False, "Role name is required."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM roles WHERE role_name = ? AND id != ?",
        (new_name.strip(), role_id),
    )
    if cursor.fetchone():
        conn.close()
        return False, "Role name already exists."

    cursor.execute(
        "UPDATE roles SET role_name = ?, has_coding_round = ? WHERE id = ?",
        (new_name.strip(), has_coding_round, role_id),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected:
        return True, "Role updated successfully."
    return False, "Role not found."


def delete_role(role_id):
    """Delete a role and its questions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE role_id = ?", (role_id,))
    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected:
        return True, "Role deleted successfully."
    return False, "Role not found."


def fetch_roles():
    """Return all roles in creation order."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, role_name, has_coding_round
        FROM roles
        ORDER BY id ASC
    """)

    rows = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return rows


# --- Question Management ---


def add_mcq_question(
    role_id, difficulty, question, option_a, option_b, option_c, option_d, correct_answer
):
    """Add an MCQ question for Round 1."""
    fields = [question, option_a, option_b, option_c, option_d, correct_answer]
    if not all(f and str(f).strip() for f in fields):
        return False, "All fields and options are required."

    if correct_answer.strip().upper() not in ("A", "B", "C", "D"):
        return False, "Correct answer must be A, B, C, or D."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, difficulty, question,
                option_a, option_b, option_c, option_d, correct_answer
            ) VALUES (?, 'mcq', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                role_id,
                difficulty,
                question.strip(),
                option_a.strip(),
                option_b.strip(),
                option_c.strip(),
                option_d.strip(),
                correct_answer.strip().upper(),
            ),
        )
        conn.commit()
        log_activity("Admin added MCQ question")
        return True, "MCQ question added."
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def add_technical_question(role_id, difficulty, question, keywords):
    """Add a technical typed question for Round 2."""
    if not question or not question.strip():
        return False, "Question is required."

    kw_list = parse_keywords(keywords)
    if len(kw_list) < 3:
        return False, "Minimum 3 keywords required (comma-separated)."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, difficulty, question, keywords
            ) VALUES (?, 'technical', ?, ?, ?)
            """,
            (role_id, difficulty, question.strip(), keywords.strip()),
        )
        conn.commit()
        log_activity("Admin added Technical question")
        return True, "Technical question added."
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def add_hr_question(role_id, question, expected_keywords):
    """Add an HR typed question for Round 3."""
    if not question or not question.strip():
        return False, "Question is required."

    if not expected_keywords or not expected_keywords.strip():
        return False, "Expected keywords are required."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, question, keywords
            ) VALUES (?, 'hr', ?, ?)
            """,
            (role_id, question.strip(), expected_keywords.strip()),
        )
        conn.commit()
        log_activity("Admin added HR question")
        return True, "HR question added."
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def add_coding_question(
    role_id, difficulty, question, code_snippet, option_a, option_b, option_c, option_d, correct_answer
):
    """Add a Coding question for Round 3."""
    fields = [question, code_snippet, option_a, option_b, option_c, option_d, correct_answer]
    if not all(f and str(f).strip() for f in fields):
        return False, "All fields and options are required."

    if correct_answer.strip().upper() not in ("A", "B", "C", "D"):
        return False, "Correct answer must be A, B, C, or D."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, difficulty, question, code_snippet,
                option_a, option_b, option_c, option_d, correct_answer
            ) VALUES (?, 'coding', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                role_id,
                difficulty,
                question.strip(),
                code_snippet.strip(),
                option_a.strip(),
                option_b.strip(),
                option_c.strip(),
                option_d.strip(),
                correct_answer.strip().upper(),
            ),
        )
        conn.commit()
        log_activity("Admin added Coding question")
        return True, "Coding question added."
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def check_duplicate_question(role_id, question_type, question, code_snippet=None):
    """Check if a question already exists in the database for the given role."""
    conn = get_connection()
    cursor = conn.cursor()
    if question_type == "coding":
        cursor.execute(
            """
            SELECT id FROM questions
            WHERE role_id = ? AND question_type = 'coding' AND question = ? AND code_snippet = ?
            """,
            (role_id, question, code_snippet)
        )
    else:
        cursor.execute(
            """
            SELECT id FROM questions
            WHERE role_id = ? AND question_type = ? AND question = ?
            """,
            (role_id, question_type, question)
        )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def _insert_coding(
    role_id,
    difficulty,
    question,
    code_snippet,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer,
    ideal_answer=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, difficulty, question, code_snippet,
                option_a, option_b, option_c, option_d,
                correct_answer, ideal_answer
            ) VALUES (?, 'coding', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                role_id,
                difficulty,
                question,
                code_snippet,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                ideal_answer,
            ),
        )
        conn.commit()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def edit_question(question_id, **kwargs):
    """Edit an existing question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Question not found."

    qtype = row["question_type"]
    updates = []
    values = []

    field_map = {
        "difficulty": "difficulty",
        "question": "question",
        "option_a": "option_a",
        "option_b": "option_b",
        "option_c": "option_c",
        "option_d": "option_d",
        "correct_answer": "correct_answer",
        "keywords": "keywords",
        "code_snippet": "code_snippet",
    }

    for key, col in field_map.items():
        if key in kwargs and kwargs[key] is not None:
            updates.append(f"{col} = ?")
            values.append(kwargs[key])

    if qtype == "technical" and "keywords" in kwargs:
        if len(parse_keywords(kwargs["keywords"])) < 3:
            conn.close()
            return False, "Minimum 3 keywords required."

    if not updates:
        conn.close()
        return False, "No fields to update."

    values.append(question_id)
    cursor.execute(
        f"UPDATE questions SET {', '.join(updates)} WHERE id = ?", values
    )
    conn.commit()
    conn.close()
    return True, "Question updated."


def delete_question(question_id):
    """Delete a question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected:
        return True, "Question deleted."
    return False, "Question not found."


def delete_questions_for_role(role_id, difficulty=None):
    """Remove questions for a role before bulk replace.

    If *difficulty* is given, only questions for that role+difficulty are
    removed.  Without it, all questions for the role are removed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    if difficulty:
        cursor.execute(
            "DELETE FROM questions WHERE role_id = ? AND difficulty = ?",
            (role_id, difficulty),
        )
    else:
        cursor.execute("DELETE FROM questions WHERE role_id = ?", (role_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


def import_questions_from_file(
    role_id,
    filepath,
    difficulty,
    replace_existing=False
):
    """
    Import MCQ, technical, coding, and HR questions from CSV/JSON/DOCX.

    When replace_existing is True:
      - Deletes only the questions for this role + difficulty first.
      - Skips duplicate checks against the DB (those rows were just deleted).
    When replace_existing is False:
      - Appends new questions; rows that already exist in the DB are skipped
        with a warning rather than aborting the whole import.

    The delete is performed AFTER parsing succeeds so no data is lost if the
    file cannot be read.
    """
    if not role_id:
        return False, "Select a valid job role."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM roles WHERE id = ?", (role_id,))
    if not cursor.fetchone():
        conn.close()
        return False, "Role not found."
    conn.close()

    # --- 1. Parse file first (no DB writes yet) --------------------------
    try:
        parsed = load_questions_file(filepath)
    except Exception as exc:
        return False, f"Could not read file: {exc}"

    if not parsed:
        return False, "The file appears to be empty or has no valid rows."

    # --- 2. Now it is safe to delete (only after successful parse) -------
    if replace_existing:
        delete_questions_for_role(role_id, difficulty=difficulty)

    counts = {"mcq": 0, "technical": 0, "coding": 0, "hr": 0}
    errors = []
    skipped_duplicates = 0
    seen_in_file = set()

    for i, item in enumerate(parsed, start=1):
        row_num = item.get("row_num", i)
        qtype = (item.get("type") or "").strip().lower()
        ideal = item.get("ideal_answer") or None

        # Force difficulty from UI dropdown
        item["difficulty"] = difficulty

        try:
            if qtype == "mcq":
                if not item.get("question"):
                    raise ValueError("question is required.")
                for f in ["option_a", "option_b", "option_c", "option_d"]:
                    if not item.get(f):
                        raise ValueError(f"MCQ missing '{f}'.")
                if not item.get("correct_answer"):
                    raise ValueError("correct_answer is required.")
                if item["correct_answer"].upper() not in ("A", "B", "C", "D"):
                    raise ValueError("correct_answer must be A, B, C, or D.")

                # Only check DB duplicates when NOT replacing (replacing already
                # cleared the slate for this role+difficulty).
                if not replace_existing and check_duplicate_question(
                    role_id, "mcq", item["question"]
                ):
                    skipped_duplicates += 1
                    continue  # silently skip, don't count as error

                ok, msg = _insert_mcq(
                    role_id,
                    item["difficulty"],
                    item["question"],
                    item["option_a"],
                    item["option_b"],
                    item["option_c"],
                    item["option_d"],
                    item["correct_answer"].upper(),
                    ideal,
                )
                if not ok:
                    raise ValueError(msg)

            elif qtype == "coding":
                if not item.get("question"):
                    raise ValueError("question is required.")
                if not item.get("code_snippet"):
                    raise ValueError("Missing Code Snippet")
                for f in ["option_a", "option_b", "option_c", "option_d"]:
                    if not item.get(f):
                        raise ValueError(f"Missing Option {f[-1].upper()}")
                if not item.get("correct_answer"):
                    raise ValueError("correct_answer is required.")
                if item["correct_answer"].upper() not in ("A", "B", "C", "D"):
                    raise ValueError("Invalid Correct Answer")

                # Check duplicates within this upload file
                seen_key = (item["question"].strip(), item["code_snippet"].strip())
                if seen_key in seen_in_file:
                    skipped_duplicates += 1
                    continue
                seen_in_file.add(seen_key)

                # Check DB duplicates only in append mode
                if not replace_existing and check_duplicate_question(
                    role_id, "coding", item["question"], item["code_snippet"]
                ):
                    skipped_duplicates += 1
                    continue

                ok, msg = _insert_coding(
                    role_id,
                    item["difficulty"],
                    item["question"],
                    item["code_snippet"],
                    item["option_a"],
                    item["option_b"],
                    item["option_c"],
                    item["option_d"],
                    item["correct_answer"].upper(),
                    ideal,
                )
                if not ok:
                    raise ValueError(msg)

            elif qtype == "technical":
                if not item.get("question"):
                    raise ValueError("question is required.")
                kws = [k.strip() for k in (item.get("keywords") or "").split(",") if k.strip()]
                if len(kws) < 3:
                    raise ValueError("technical needs 3+ keywords.")

                # Skip DB duplicates in append mode
                if not replace_existing and check_duplicate_question(
                    role_id, "technical", item["question"]
                ):
                    skipped_duplicates += 1
                    continue

                ok, msg = _insert_technical(
                    role_id,
                    item["difficulty"],
                    item["question"],
                    item.get("keywords"),
                    ideal,
                )
                if not ok:
                    raise ValueError(msg)

            elif qtype == "hr":
                if not item.get("question"):
                    raise ValueError("question is required.")
                if not item.get("keywords"):
                    raise ValueError("HR needs keywords.")

                # Skip DB duplicates in append mode
                if not replace_existing and check_duplicate_question(
                    role_id, "hr", item["question"]
                ):
                    skipped_duplicates += 1
                    continue

                ok, msg = _insert_hr(
                    role_id,
                    item["question"],
                    item.get("keywords"),
                    ideal,
                )
                if not ok:
                    raise ValueError(msg)
            else:
                raise ValueError(f"Invalid type '{qtype}'. Use: mcq, technical, coding, hr")

            if ok:
                counts[qtype] += 1
        except Exception as exc:
            errors.append(f"Row {row_num}: {exc}")

    total = sum(counts.values())
    if total == 0 and skipped_duplicates == 0:
        detail = "\n".join(errors[:5]) if errors else "No valid rows found in file."
        return False, f"Import failed — nothing was imported.\n{detail}"

    log_activity(f"Admin added {total} questions")

    summary = (
        f"Imported {total} new question(s): "
        f"{counts['mcq']} MCQ, {counts['technical']} technical, "
        f"{counts['coding']} coding, {counts['hr']} HR."
    )
    if replace_existing:
        summary = f"Replaced existing '{difficulty}' questions for this role. " + summary
    if skipped_duplicates:
        summary += f"\n{skipped_duplicates} duplicate(s) already in database were skipped."
    if errors:
        summary += f"\n\nSkipped {len(errors)} invalid row(s):\n" + "\n".join(errors[:8])

    # Return True even if total==0 but duplicates were skipped, so the UI
    # still calls _refresh_questions() and shows the unchanged question list.
    return True, summary


def _insert_mcq(
    role_id,
    difficulty,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer,
    ideal_answer=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, difficulty, question,
                option_a, option_b, option_c, option_d,
                correct_answer, ideal_answer
            ) VALUES (?, 'mcq', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                role_id,
                difficulty,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                ideal_answer,
            ),
        )
        conn.commit()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def _insert_technical(role_id, difficulty, question, keywords, ideal_answer=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, difficulty, question,
                keywords, ideal_answer
            ) VALUES (?, 'technical', ?, ?, ?, ?)
            """,
            (role_id, difficulty, question, keywords, ideal_answer),
        )
        conn.commit()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def _insert_hr(role_id, question, keywords, ideal_answer=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO questions (
                role_id, question_type, question, keywords, ideal_answer
            ) VALUES (?, 'hr', ?, ?, ?)
            """,
            (role_id, question, keywords, ideal_answer),
        )
        conn.commit()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
    finally:
        conn.close()


def view_questions(role_id=None, question_type=None):
    """View questions with optional filters."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT q.*, r.role_name
        FROM questions q
        JOIN roles r ON q.role_id = r.id
        WHERE 1=1
    """
    params = []

    if role_id:
        query += " AND q.role_id = ?"
        params.append(role_id)
    if question_type:
        query += " AND q.question_type = ?"
        params.append(question_type)

    query += " ORDER BY q.question_type, q.id"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# --- Analytics ---


def view_students(search_query=None):
    """Return all registered students, optionally filtered, with interview count."""
    conn = get_connection()
    cursor = conn.cursor()
    if search_query and search_query.strip():
        q = f"%{search_query.strip()}%"
        cursor.execute(
            """
            SELECT id, name, email, created_at
            FROM students
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
            """,
            (q, q),
        )
    else:
        cursor.execute(
            "SELECT id, name, email, created_at FROM students ORDER BY created_at DESC"
        )
    rows = [dict(r) for r in cursor.fetchall()]

    for row in rows:
        cursor.execute(
            "SELECT COUNT(*) FROM results WHERE student_id = ?",
            (row["id"],)
        )
        row["total_interviews"] = cursor.fetchone()[0]

    conn.close()
    return rows


def view_student_scores(student_id=None):
    """View performance results."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT res.*, s.name AS student_name, r.role_name
        FROM results res
        JOIN students s ON res.student_id = s.id
        JOIN roles r ON res.role_id = r.id
    """
    params = []
    if student_id:
        query += " WHERE res.student_id = ?"
        params.append(student_id)
    query += " ORDER BY res.created_at DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def filter_by_role(role_id):
    """Filter results by job role."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT res.*, s.name AS student_name, r.role_name
        FROM results res
        JOIN students s ON res.student_id = s.id
        JOIN roles r ON res.role_id = r.id
        WHERE res.role_id = ?
        ORDER BY res.overall_score DESC
        """,
        (role_id,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def show_top_students(limit=10):
    """Return top performers by overall score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.name, s.email, r.role_name,
               res.overall_score, res.mcq_score, res.technical_score,
               res.hr_score, res.created_at
        FROM results res
        JOIN students s ON res.student_id = s.id
        JOIN roles r ON res.role_id = r.id
        ORDER BY res.overall_score DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def parse_docx(filepath):
    """
    Parse DOCX question file.
    Returns list of question dictionaries.
    """

    doc = Document(filepath)

    text = "\n".join(
        para.text.strip()
        for para in doc.paragraphs
        if para.text.strip()
    )

    blocks = text.split("----")
    questions = []

    for block in blocks:
        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        data = {
            "type": "",
            "difficulty": "",
            "question": "",
            "option_a": "",
            "option_b": "",
            "option_c": "",
            "option_d": "",
            "correct_answer": "",
            "keywords": "",
            "ideal_answer": "",
        }

        for line in lines:
            if line.startswith("TYPE:"):
                data["type"] = line.replace(
                    "TYPE:", ""
                ).strip()

            elif line.startswith("DIFFICULTY:"):
                data["difficulty"] = line.replace(
                    "DIFFICULTY:", ""
                ).strip()

            elif line.startswith("QUESTION:"):
                data["question"] = line.replace(
                    "QUESTION:", ""
                ).strip()

            elif line.startswith("A:"):
                data["option_a"] = line.replace(
                    "A:", ""
                ).strip()

            elif line.startswith("B:"):
                data["option_b"] = line.replace(
                    "B:", ""
                ).strip()

            elif line.startswith("C:"):
                data["option_c"] = line.replace(
                    "C:", ""
                ).strip()

            elif line.startswith("D:"):
                data["option_d"] = line.replace(
                    "D:", ""
                ).strip()

            elif line.startswith("ANSWER:"):
                data["correct_answer"] = line.replace(
                    "ANSWER:", ""
                ).strip()

            elif line.startswith("KEYWORDS:"):
                data["keywords"] = line.replace(
                    "KEYWORDS:", ""
                ).strip()

            elif line.startswith("IDEAL_ANSWER:"):
                data["ideal_answer"] = line.replace(
                    "IDEAL_ANSWER:", ""
                ).strip()

        if data["question"]:
            questions.append(data)

    return questions

# =========================================
# ADMIN ANALYTICS HELPERS
# =========================================

def get_dashboard_stats():
    """Return overall admin dashboard statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM roles")
    total_roles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results")
    total_interviews = cursor.fetchone()[0]

    conn.close()

    return {
        "students": total_students,
        "roles": total_roles,
        "questions": total_questions,
        "interviews": total_interviews,
    }


def get_pass_fail_stats():
    """Return pass/fail interview counts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS pass_count,
            SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS fail_count
        FROM results
        """
    )

    row = cursor.fetchone()
    conn.close()

    return {
        "pass": row["pass_count"] or 0,
        "fail": row["fail_count"] or 0,
    }


def get_average_scores():
    """Return average round scores."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            AVG(mcq_score) AS avg_mcq,
            AVG(technical_score) AS avg_technical,
            AVG(coding_score) AS avg_coding,
            AVG(hr_score) AS avg_hr,
            AVG(overall_score) AS avg_overall
        FROM results
        """
    )

    row = cursor.fetchone()
    conn.close()

    return {
        "mcq": round(row["avg_mcq"] or 0, 2),
        "technical": round(row["avg_technical"] or 0, 2),
        "coding": round(row["avg_coding"] or 0, 2),
        "hr": round(row["avg_hr"] or 0, 2),
        "overall": round(row["avg_overall"] or 0, 2),
    }


def get_coding_analytics_stats():
    """Return detailed coding round statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Coding Round Attempts (attempts where role has coding round)
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM results res
        JOIN roles r ON res.role_id = r.id
        WHERE r.has_coding_round = 1
        """
    )
    attempts = cursor.fetchone()[0]

    # 2. Average Coding Score (only for roles with coding round)
    cursor.execute(
        """
        SELECT AVG(coding_score)
        FROM results res
        JOIN roles r ON res.role_id = r.id
        WHERE r.has_coding_round = 1
        """
    )
    avg_score = cursor.fetchone()[0] or 0.0

    # 3. Coding Round Success Rate (percent of attempts with coding_score >= 60)
    success_rate = 0.0
    if attempts > 0:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM results res
            JOIN roles r ON res.role_id = r.id
            WHERE r.has_coding_round = 1 AND res.coding_score >= 60
            """
        )
        passed_attempts = cursor.fetchone()[0]
        success_rate = (passed_attempts / attempts) * 100.0

    # 4. Best Coding Performer
    cursor.execute(
        """
        SELECT s.name, res.coding_score
        FROM results res
        JOIN students s ON res.student_id = s.id
        JOIN roles r ON res.role_id = r.id
        WHERE r.has_coding_round = 1
        ORDER BY res.coding_score DESC, res.created_at DESC
        LIMIT 1
        """
    )
    best_row = cursor.fetchone()
    best_performer = "—"
    if best_row:
        best_performer = f"{best_row['name']} ({best_row['coding_score']:.1f}%)"

    conn.close()

    return {
        "attempts": attempts,
        "avg_score": round(avg_score, 2),
        "success_rate": round(success_rate, 2),
        "best_performer": best_performer,
    }


def get_role_wise_performance():
    """Return average score by job role."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            r.role_name,
            COUNT(res.id) AS total_attempts,
            AVG(res.overall_score) AS avg_score
        FROM results res
        JOIN roles r ON res.role_id = r.id
        GROUP BY r.id
        ORDER BY avg_score DESC
        """
    )

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_recent_interviews(limit=10):
    """Return latest interview attempts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            s.name,
            r.role_name,
            res.overall_score,
            res.status,
            res.created_at
        FROM results res
        JOIN students s ON res.student_id = s.id
        JOIN roles r ON res.role_id = r.id
        ORDER BY res.created_at DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def load_admin_profile(admin_id):
    """Load admin profile."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username
        FROM admins
        WHERE id = ?
        """,
        (admin_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def update_admin_profile(admin_id, username):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE admins SET username=? WHERE id=?",
            (username, admin_id)
        )

        conn.commit()
        return True, "Profile updated successfully."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()

#from utils import hash_password

def update_admin_password(admin_id, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE admins SET password_hash=? WHERE id=?",
            (hash_password(password), admin_id)
        )

        conn.commit()
        return True, "Password updated successfully."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def delete_student(student_id):
    """Delete a student record and their associated interview results."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM results WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return True, "Student deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_student_profile_stats(student_id):
    """Fetch structured profile statistics for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, email, created_at FROM students WHERE id = ?", (student_id,))
        student_row = cursor.fetchone()
        if not student_row:
            return None

        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_interviews,
                AVG(overall_score) as avg_score,
                MAX(overall_score) as best_score
            FROM results
            WHERE student_id = ?
            """,
            (student_id,),
        )
        stats_row = cursor.fetchone()
        return {
            "name": student_row["name"],
            "email": student_row["email"],
            "created_at": student_row["created_at"],
            "total_interviews": stats_row["total_interviews"] or 0,
            "avg_score": round(stats_row["avg_score"] or 0.0, 2),
            "best_score": round(stats_row["best_score"] or 0.0, 2),
        }
    except Exception:
        return None
    finally:
        conn.close()


def get_question_count_per_role():
    """Return the count of questions per job role."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT r.role_name, COUNT(q.id) AS question_count
            FROM roles r
            LEFT JOIN questions q ON r.id = q.role_id
            GROUP BY r.id, r.role_name
            ORDER BY question_count DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def search_questions(search_query=None, role_id=None, difficulty=None, question_type=None):
    """Filter and search questions dynamically with optional keywords and filters."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT q.*, r.role_name
            FROM questions q
            JOIN roles r ON q.role_id = r.id
            WHERE 1=1
        """
        params = []

        if role_id:
            query += " AND q.role_id = ?"
            params.append(role_id)
        if difficulty:
            query += " AND q.difficulty = ?"
            params.append(difficulty)
        if question_type:
            query += " AND q.question_type = ?"
            params.append(question_type)
            
        if search_query and search_query.strip():
            search_pattern = f"%{search_query.strip()}%"
            query += " AND (q.question LIKE ? OR q.keywords LIKE ?)"
            params.append(search_pattern)
            params.append(search_pattern)

        query += " ORDER BY q.question_type, q.id"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def export_all_results_csv(filepath):
    """Export all results to a CSV file."""
    import csv
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT s.name AS student_name, s.email, r.role_name, res.difficulty,
                   res.mcq_score, res.technical_score, res.coding_score, res.hr_score, res.overall_score,
                   res.status, res.created_at AS interview_date
            FROM results res
            JOIN students s ON res.student_id = s.id
            JOIN roles r ON res.role_id = r.id
            ORDER BY res.created_at DESC
            """
        )
        rows = cursor.fetchall()
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Student Name", "Email", "Role", "Difficulty",
                "MCQ Score", "Technical Score", "Coding Score", "HR Score", "Overall Score",
                "Status", "Interview Date"
            ])
            for row in rows:
                writer.writerow([
                    row["student_name"],
                    row["email"],
                    row["role_name"],
                    row["difficulty"] or "—",
                    f"{row['mcq_score']}%",
                    f"{row['technical_score']}%",
                    f"{row.get('coding_score', 0.0)}%",
                    f"{row['hr_score']}%",
                    f"{row['overall_score']}%",
                    row["status"] or ("PASS" if row["overall_score"] >= 60 else "FAIL"),
                    row["interview_date"]
                ])
        return True
    except Exception as e:
        print(f"Error exporting results CSV: {e}")
        raise e
    finally:
        conn.close()


def get_top_performers(limit=5):
    """Get top students based on their average overall interview score."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT s.name, AVG(res.overall_score) AS avg_score
            FROM results res
            JOIN students s ON res.student_id = s.id
            GROUP BY s.id, s.name
            ORDER BY avg_score DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def get_most_failed_roles():
    """Get failure counts per role, sorted descending."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT r.role_name, COUNT(res.id) AS fail_count
            FROM results res
            JOIN roles r ON res.role_id = r.id
            WHERE res.status = 'FAIL' OR (res.status IS NULL AND res.overall_score < 60)
            GROUP BY r.id, r.role_name
            ORDER BY fail_count DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def get_question_difficulty_summary():
    """Return counts of Easy, Medium, and Hard questions."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN LOWER(difficulty) = 'easy' THEN 1 ELSE 0 END) AS easy_count,
                SUM(CASE WHEN LOWER(difficulty) = 'medium' THEN 1 ELSE 0 END) AS medium_count,
                SUM(CASE WHEN LOWER(difficulty) = 'hard' THEN 1 ELSE 0 END) AS hard_count
            FROM questions
            """
        )
        row = cursor.fetchone()
        return {
            "easy": (row["easy_count"] or 0) if row else 0,
            "medium": (row["medium_count"] or 0) if row else 0,
            "hard": (row["hard_count"] or 0) if row else 0
        }
    except Exception:
        return {"easy": 0, "medium": 0, "hard": 0}
    finally:
        conn.close()


def get_recent_activities(limit=10):
    """Retrieve the latest activities from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT activity_text, created_at
            FROM activities
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()