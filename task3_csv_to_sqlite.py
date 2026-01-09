

import csv
import logging
import re
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DB_FILE = "app.db"
CSV_FILE = "users.csv"
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.commit()


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def load_csv():
    records = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            email = row.get("email", "").strip()

            if not name or not is_valid_email(email):
                logging.warning("Invalid row skipped: %s", row)
                continue

            records.append((name, email))
    return records


def insert_users(conn, users):
    conn.executemany(
        "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", users
    )
    conn.commit()


def count_users(conn):
    cursor = conn.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


def main():
    users = load_csv()
    if not users:
        logging.warning("No valid users found")
        return

    with sqlite3.connect(DB_FILE) as conn:
        init_db(conn)

        before = count_users(conn)
        insert_users(conn, users)
        after = count_users(conn)

    if after > before:
        logging.info("Database updated: %d new user(s) inserted", after - before)
    else:
        logging.info("No changes applied (all users already present)")
