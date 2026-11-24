"""
Модуль работы с базой данных (SQLite)
Хранение книг, собранных с Rusbuk.ru
"""

import sqlite3
from pathlib import Path
from typing import List, Dict

DB_PATH = Path(__file__).parent.parent / "data" / "books.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создаёт таблицу книг, если её ещё нет"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            price TEXT,
            category TEXT,
            url TEXT,
            source TEXT DEFAULT 'rusbuk.ru',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_books(books: List[Dict]) -> int:
    """
    Сохраняет список книг в базу.
    books = [{"title": "...", "author": "...", "price": "...", "category": "...", "url": "..."}, ...]
    """
    if not books:
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    saved = 0

    for b in books:
        title = (b.get("title") or "").strip()
        if not title:
            continue

        # Проверка на дубликат по названию + цене
        cursor.execute(
            "SELECT id FROM books WHERE title = ? AND price = ?",
            (title, b.get("price", ""))
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """INSERT INTO books (title, author, price, category, url, source)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    title,
                    b.get("author", ""),
                    b.get("price", ""),
                    b.get("category", ""),
                    b.get("url", ""),
                    b.get("source", "rusbuk.ru")
                )
            )
            saved += 1

    conn.commit()
    conn.close()
    return saved


def get_all_books(limit: int = 1000) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, author, price, category, url, source, created_at "
        "FROM books ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_books(query: str = "", author: str = "", category: str = "") -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT id, title, author, price, category, url, source, created_at FROM books WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE ? OR author LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if author:
        sql += " AND author LIKE ?"
        params.append(f"%{author}%")
    if category:
        sql += " AND category LIKE ?"
        params.append(f"%{category}%")

    sql += " ORDER BY id DESC LIMIT 500"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats() -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM books")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(DISTINCT author) as authors FROM books WHERE author != ''")
    authors = cursor.fetchone()["authors"]
    cursor.execute("SELECT COUNT(DISTINCT category) as categories FROM books WHERE category != ''")
    categories = cursor.fetchone()["categories"]
    conn.close()
    return {
        "total_books": total,
        "unique_authors": authors,
        "categories": categories
    }


def clear_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books")
    conn.commit()
    conn.close()
