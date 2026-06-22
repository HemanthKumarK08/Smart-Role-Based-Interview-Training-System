# """SQLite database initialization and connection management."""

# import os
# import sqlite3

# DB_DIR = os.path.join(os.path.dirname(__file__), "database")
# DB_PATH = os.path.join(DB_DIR, "interview.db")


# def get_connection():
#     """Return a connection to the SQLite database."""
#     os.makedirs(DB_DIR, exist_ok=True)
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn


# def init_db():
#     """Create all required tables if they do not exist."""
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS admins (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password_hash TEXT NOT NULL
#         )
#         """
#     )

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS students (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             email TEXT UNIQUE NOT NULL,
#             password_hash TEXT NOT NULL,
#             created_at TEXT NOT NULL
#         )
#         """
#     )

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS roles (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             role_name TEXT UNIQUE NOT NULL
#         )
#         """
#     )

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS questions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             role_id INTEGER NOT NULL,
#             question_type TEXT NOT NULL,
#             difficulty TEXT,
#             question TEXT NOT NULL,
#             option_a TEXT,
#             option_b TEXT,
#             option_c TEXT,
#             option_d TEXT,
#             correct_answer TEXT,
#             keywords TEXT,
#             ideal_answer TEXT,
#             FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
#         )
#         """
#     )

#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS results (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             student_id INTEGER NOT NULL,
#             role_id INTEGER NOT NULL,
#             mcq_score REAL NOT NULL,
#             technical_score REAL NOT NULL,
#             hr_score REAL NOT NULL,
#             overall_score REAL NOT NULL,
#             feedback TEXT NOT NULL,
#             created_at TEXT NOT NULL,
#             session_data TEXT,
#             difficulty TEXT,
#             FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
#             FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
#         )
#         """
#     )

#     _migrate_schema(cursor)
#     conn.commit()
#     conn.close()


# def _migrate_schema(cursor):
#     """Add columns introduced after initial release."""
#     cursor.execute("PRAGMA table_info(questions)")
#     qcols = {row[1] for row in cursor.fetchall()}
#     if "ideal_answer" not in qcols:
#         cursor.execute("ALTER TABLE questions ADD COLUMN ideal_answer TEXT")

#     cursor.execute("PRAGMA table_info(results)")
#     rcols = {row[1] for row in cursor.fetchall()}
#     if "session_data" not in rcols:
#         cursor.execute("ALTER TABLE results ADD COLUMN session_data TEXT")
#     if "difficulty" not in rcols:
#         cursor.execute("ALTER TABLE results ADD COLUMN difficulty TEXT")



"""SQLite database initialization and connection management."""

import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "interview.db")


def get_connection():
    """Return a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all required tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # ADMINS
    # -----------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    # -----------------------------
    # STUDENTS
    # -----------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # -----------------------------
    # ROLES
    # -----------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            has_coding_round INTEGER DEFAULT 0
        )
        """
    )

    # -----------------------------
    # QUESTIONS
    # -----------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            question_type TEXT NOT NULL,
            difficulty TEXT,
            question TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT,
            keywords TEXT,
            ideal_answer TEXT,
            code_snippet TEXT,
            FOREIGN KEY (role_id)
                REFERENCES roles(id)
                ON DELETE CASCADE
        )
        """
    )

    # -----------------------------
    # RESULTS
    # -----------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,

            mcq_score REAL NOT NULL,
            technical_score REAL NOT NULL,
            coding_score REAL DEFAULT 0,
            hr_score REAL NOT NULL,
            overall_score REAL NOT NULL,

            percentage REAL DEFAULT 0,
            status TEXT DEFAULT 'FAIL',

            feedback TEXT NOT NULL,
            created_at TEXT NOT NULL,

            session_data TEXT,
            difficulty TEXT,

            strong_areas TEXT,
            weak_areas TEXT,

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (role_id)
                REFERENCES roles(id)
                ON DELETE CASCADE
        )
        """
    )

    # -----------------------------
    # ACTIVITIES
    # -----------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    _migrate_schema(cursor)

    conn.commit()
    conn.close()


def _migrate_schema(cursor):
    """Add columns introduced after initial release."""

    # -----------------------------
    # ROLES TABLE
    # -----------------------------
    cursor.execute("PRAGMA table_info(roles)")
    role_cols = {row[1] for row in cursor.fetchall()}
    if "has_coding_round" not in role_cols:
        cursor.execute(
            "ALTER TABLE roles "
            "ADD COLUMN has_coding_round INTEGER DEFAULT 0"
        )

    # -----------------------------
    # QUESTIONS TABLE
    # -----------------------------
    cursor.execute("PRAGMA table_info(questions)")
    qcols = {row[1] for row in cursor.fetchall()}

    if "ideal_answer" not in qcols:
        cursor.execute(
            "ALTER TABLE questions "
            "ADD COLUMN ideal_answer TEXT"
        )

    if "code_snippet" not in qcols:
        cursor.execute(
            "ALTER TABLE questions "
            "ADD COLUMN code_snippet TEXT"
        )

    # -----------------------------
    # RESULTS TABLE
    # -----------------------------
    cursor.execute("PRAGMA table_info(results)")
    rcols = {row[1] for row in cursor.fetchall()}

    if "coding_score" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN coding_score REAL DEFAULT 0"
        )

    if "session_data" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN session_data TEXT"
        )

    if "difficulty" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN difficulty TEXT"
        )

    if "percentage" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN percentage REAL DEFAULT 0"
        )

    if "status" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN status TEXT DEFAULT 'FAIL'"
        )

    if "strong_areas" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN strong_areas TEXT"
        )

    if "weak_areas" not in rcols:
        cursor.execute(
            "ALTER TABLE results "
            "ADD COLUMN weak_areas TEXT"
        )


def log_activity(activity_text):
    """Insert a new activity log entry."""
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO activities (activity_text, created_at) VALUES (?, ?)",
            (activity_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
    finally:
        conn.close()