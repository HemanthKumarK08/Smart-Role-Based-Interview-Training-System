"""Student dashboard module."""

from database import get_connection
from utils import hash_password
import auth


def load_profile(student_id=None):
    """Load student profile information."""
    session = auth.get_session()
    if student_id is None and session["user"]:
        student_id = session["user"]["id"]

    if not student_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, created_at FROM students WHERE id = ?",
        (student_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def select_role(role_id):
    """Validate and return role details for interview."""
    from admin import fetch_roles

    roles = fetch_roles()
    for role in roles:
        if role["id"] == role_id:
            return role
    return None


def select_difficulty(difficulty):
    """Validate difficulty selection."""
    valid = ("Easy", "Medium", "Hard")
    if difficulty in valid:
        return difficulty
    return None

def update_password(student_id, new_password):
    """Update student password."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE students
        SET password_hash = ?
        WHERE id = ?
        """,
        (hash_password(new_password), student_id),
    )

    conn.commit()
    conn.close()

def update_profile(student_id, name, email):
    """Update student name and email."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE students
        SET name = ?, email = ?
        WHERE id = ?
        """,
        (name, email, student_id),
    )

    conn.commit()
    conn.close()