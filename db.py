"""SQLite database for tracking study progress."""

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path("study_data.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def _connect():
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                box INTEGER DEFAULT 1,
                next_review_date TEXT NOT NULL,
                times_studied INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                stem TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT,
                created_at TEXT NOT NULL,
                box INTEGER DEFAULT 1,
                next_review_date TEXT,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            );
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                score REAL NOT NULL,
                attempted_at TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
        """)
        conn.commit()


def get_or_create_topic(name: str) -> dict:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM topics WHERE name = ?", (name,)).fetchone()
        if row:
            return dict(row)
        conn.execute(
            "INSERT INTO topics (name, next_review_date) VALUES (?, ?)",
            (name, date.today().isoformat()),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM topics WHERE name = ?", (name,)).fetchone()
        return dict(row)


def save_question(topic_id: int, q: dict) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO questions (topic_id, stem, option_a, option_b, option_c, option_d,
               correct_answer, explanation, created_at, box, next_review_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
            (
                topic_id, q["stem"], q["option_a"], q["option_b"],
                q["option_c"], q["option_d"], q["correct_answer"],
                q.get("explanation", ""), datetime.now().isoformat(),
                date.today().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid


def save_attempt(question_id: int, user_answer: str, score: float):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO attempts (question_id, user_answer, score, attempted_at) VALUES (?, ?, ?, ?)",
            (question_id, user_answer, score, datetime.now().isoformat()),
        )
        conn.commit()


def update_question_after_attempt(question_id: int, score: float):
    """Update a question's Leitner box based on attempt score."""
    from review import get_next_review_date

    with _connect() as conn:
        row = conn.execute("SELECT box FROM questions WHERE id = ?", (question_id,)).fetchone()
        if not row:
            return
        old_box = row["box"]
        if score >= 1.0:
            new_box = min(old_box + 1, 5)
        elif score >= 0.5:
            new_box = old_box
        else:
            new_box = 1
        next_date = get_next_review_date(new_box)
        conn.execute(
            "UPDATE questions SET box = ?, next_review_date = ? WHERE id = ?",
            (new_box, next_date, question_id),
        )
        conn.commit()


def get_review_questions(topic_id: int) -> list[dict]:
    """Fetch all due questions for a topic, ordered by priority (lowest box first)."""
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM questions
               WHERE topic_id = ? AND next_review_date <= ?
               ORDER BY box ASC, next_review_date ASC""",
            (topic_id, date.today().isoformat()),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["is_review"] = True
        result.append(d)
    return result


def count_review_questions(topic_id: int) -> int:
    """Count due questions for a topic."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM questions WHERE topic_id = ? AND next_review_date <= ?",
            (topic_id, date.today().isoformat()),
        ).fetchone()
        return row["cnt"]


def update_topic_after_quiz(topic_name: str, score_pct: float):
    """Update Leitner box based on quiz score. >=70% moves up, <70% resets to box 1."""
    from review import get_next_review_date

    with _connect() as conn:
        topic = conn.execute("SELECT * FROM topics WHERE name = ?", (topic_name,)).fetchone()
        if not topic:
            return

        old_box = topic["box"]
        if score_pct >= 70:
            new_box = min(old_box + 1, 5)
        else:
            new_box = 1

        next_date = get_next_review_date(new_box)
        conn.execute(
            "UPDATE topics SET box = ?, next_review_date = ?, times_studied = times_studied + 1 WHERE name = ?",
            (new_box, next_date, topic_name),
        )
        conn.commit()
        return new_box, next_date


def get_due_topics() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM topics WHERE next_review_date <= ? ORDER BY box ASC",
            (date.today().isoformat(),),
        ).fetchall()
    return [dict(r) for r in rows]


def get_progress() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("""
            SELECT t.name, t.box, t.next_review_date, t.times_studied,
                   COUNT(a.id) as total_attempts,
                   SUM(a.score) as total_score
            FROM topics t
            LEFT JOIN questions q ON q.topic_id = t.id
            LEFT JOIN attempts a ON a.question_id = q.id
            GROUP BY t.id
            ORDER BY t.box ASC, t.name
        """).fetchall()
    return [dict(r) for r in rows]
