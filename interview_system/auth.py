"""Authentication module for admin and student users."""

from datetime import datetime

from database import get_connection
from utils import hash_password, validate_email

# Session state
_current_user = None
_user_type = None


def get_session():
    """Return current session (user dict and type)."""
    return {"user": _current_user, "type": _user_type}


def logout():
    """Clear current session."""
    global _current_user, _user_type
    _current_user = None
    _user_type = None
    return True, "Logged out successfully."


def create_admin(username, password):
    """Register a new admin (optional setup)."""
    if not username or not password:
        return False, "Username and password are required."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            (username.strip(), hash_password(password)),
        )
        conn.commit()
        return True, "Admin created successfully."
    except Exception:
        return False, "Username already exists."
    finally:
        conn.close()


def admin_login(username, password):
    """Authenticate admin user."""
    global _current_user, _user_type

    if not username or not password:
        return False, "Username and password are required."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash FROM admins WHERE username = ?",
        (username.strip(),),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "Username does not exist."

    if row["password_hash"] != hash_password(password):
        return False, "Incorrect password."

    _current_user = {"id": row["id"], "username": row["username"]}
    _user_type = "admin"
    return True, "Admin login successful."


def student_register(name, email, password, confirm_password):
    """Register a new student."""
    if not all([name, email, password, confirm_password]):
        return False, "All fields are required."

    if not validate_email(email):
        return False, "Invalid email format."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE email = ?", (email.strip().lower(),))
    if cursor.fetchone():
        conn.close()
        return False, "Email already registered."

    try:
        cursor.execute(
            """
            INSERT INTO students (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                name.strip(),
                email.strip().lower(),
                hash_password(password),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        from database import log_activity
        log_activity(f"Student {name.strip()} registered")
        return True, "Registration successful. Please login."
    except Exception as exc:
        return False, f"Registration failed: {exc}"
    finally:
        conn.close()


def student_login(email, password):
    """Authenticate student user."""
    global _current_user, _user_type

    if not email or not password:
        return False, "Email and password are required."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, password_hash FROM students WHERE email = ?",
        (email.strip().lower(),),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "Email not found."

    if row["password_hash"] != hash_password(password):
        return False, "Incorrect password."

    _current_user = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
    }
    _user_type = "student"
    return True, "Student login successful."
