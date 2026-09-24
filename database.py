"""
database.py
------------
All SQLite access for PICKLEQ lives here. Nothing in the UI files should
talk to sqlite3 directly - they call functions in this module instead.
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pickleq.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def init_db():
    """Creates all tables (if they don't exist yet) and seeds default data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'player',   -- 'player' or 'staff'
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',  -- 'available' or 'occupied'
            current_party TEXT,
            session_minutes INTEGER,
            session_start TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_name TEXT NOT NULL,
            party_size INTEGER NOT NULL DEFAULT 1,
            user_id INTEGER,
            join_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'waiting',   -- 'waiting', 'playing', 'done'
            court_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (court_id) REFERENCES courts(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            court_name TEXT NOT NULL,
            party_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes REAL NOT NULL
        )
    """)

    # seed a few courts if the table is empty
    cur.execute("SELECT COUNT(*) AS c FROM courts")
    if cur.fetchone()["c"] == 0:
        for i in range(1, 4):
            cur.execute("INSERT INTO courts (name, status) VALUES (?, 'available')", (f"Court {i}",))

    # seed a default staff account so there is something to log in with
    cur.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'staff'")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users (full_name, username, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Court Staff", "admin", hash_password("admin123"), "staff", datetime.now().isoformat()),
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Users / authentication
# ---------------------------------------------------------------------------

def create_user(full_name, username, password, role="player"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (full_name, username, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (full_name.strip(), username.strip(), hash_password(password), role, datetime.now().isoformat()),
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

def join_queue(party_name, party_size, user_id=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO queue (party_name, party_size, user_id, join_time, status) VALUES (?, ?, ?, ?, 'waiting')",
        (party_name.strip(), party_size, user_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_waiting_queue():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM queue WHERE status = 'waiting' ORDER BY join_time ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_from_queue(queue_id):
    conn = get_connection()
    conn.execute("DELETE FROM queue WHERE id = ?", (queue_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Courts / rotation timer
# ---------------------------------------------------------------------------

def get_courts():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM courts ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def start_session(court_id, queue_id, session_minutes):
    """Pulls a party off the queue and assigns it to a court."""
    conn = get_connection()
    q = conn.execute("SELECT * FROM queue WHERE id = ?", (queue_id,)).fetchone()
    if q is None:
        conn.close()
        return False, "That party is no longer in the queue."

    conn.execute(
        "UPDATE courts SET status = 'occupied', current_party = ?, session_minutes = ?, session_start = ? WHERE id = ?",
        (q["party_name"], session_minutes, datetime.now().isoformat(), court_id),
    )
    conn.execute("UPDATE queue SET status = 'playing', court_id = ? WHERE id = ?", (court_id, queue_id))
    conn.commit()
    conn.close()
    return True, "Session started."


def end_session(court_id):
    """Frees a court and writes an entry to the usage log."""
    conn = get_connection()
    court = conn.execute("SELECT * FROM courts WHERE id = ?", (court_id,)).fetchone()
    if court and court["status"] == "occupied":
        start_dt = datetime.fromisoformat(court["session_start"])
        end_dt = datetime.now()
        duration = round((end_dt - start_dt).total_seconds() / 60, 1)

        conn.execute(
            "INSERT INTO usage_log (court_name, party_name, start_time, end_time, duration_minutes) VALUES (?, ?, ?, ?, ?)",
            (court["name"], court["current_party"], court["session_start"], end_dt.isoformat(), duration),
        )
        conn.execute(
            "UPDATE queue SET status = 'done' WHERE court_id = ? AND status = 'playing'", (court_id,)
        )
        conn.execute(
            "UPDATE courts SET status = 'available', current_party = NULL, session_minutes = NULL, session_start = NULL WHERE id = ?",
            (court_id,),
        )
        conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Usage log
# ---------------------------------------------------------------------------

def get_usage_log():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usage_log ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
