
import logging
import sqlite3
import requests
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DB_FILE = "app.db"
API_URL = "https://openlibrary.org/search.json"
QUERY = "artificial intelligence"
LIMIT = 10


def get_books() -> List[Dict]:
    resp = requests.get(
        API_URL,
        params={"q": QUERY, "limit": LIMIT},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    books = []
    for doc in data.get("docs", []):
        title = doc.get("title")
        authors = ", ".join(doc.get("author_name", []))
        year = doc.get("first_publish_year")

        if not title or not authors:
            continue

        books.append(
            {
                "title": title.strip(),
                "author": authors.strip(),
                "year": year,
            }
        )
    return books


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publication_year INTEGER
        )
        """
    )
    conn.commit()


def insert_books(conn: sqlite3.Connection, books: List[Dict]) -> None:
    conn.executemany(
        """
        INSERT INTO books (title, author, publication_year)
        VALUES (:title, :author, :year)
        """,
        books,
    )
    conn.commit()


def read_books(conn: sqlite3.Connection) -> None:
    cursor = conn.execute(
        "SELECT title, author, publication_year FROM books ORDER BY id DESC"
    )
    rows = cursor.fetchall()

    for row in rows:
        logging.info("Title=%s | Author=%s | Year=%s", row[0], row[1], row[2])


def main() -> None:
    books = get_books()

    if not books:
        logging.warning("No books fetched")
        return

    with sqlite3.connect(DB_FILE) as conn:
        init_db(conn)
        insert_books(conn, books)
        read_books(conn)


if __name__ == "__main__":
    main()
