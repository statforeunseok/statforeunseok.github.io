import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path("social_emv.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            platform TEXT NOT NULL,
            post_id TEXT NOT NULL,
            author TEXT,

            post_url TEXT,
            text TEXT,

            published_at TEXT,

            impressions INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,

            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,

            engagements INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,

            cpm REAL DEFAULT 0,
            emv REAL DEFAULT 0,

            created_at TEXT NOT NULL,

            UNIQUE(platform, post_id)
        )
    """)

    connection.commit()
    connection.close()


def save_post(result, author=None, post_url=None, text=None):
    connection = get_connection()

    cursor = connection.cursor()

    performance = result.performance

    cursor.execute("""
        INSERT OR REPLACE INTO posts (
            platform,
            post_id,
            author,
            post_url,
            text,

            impressions,
            views,

            likes,
            comments,
            shares,
            saves,

            engagements,
            engagement_rate,

            cpm,
            emv,

            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        result.platform,
        result.post_id,
        author,
        post_url,
        text,

        performance.impressions,
        performance.views,

        performance.likes,
        performance.comments,
        performance.shares,
        performance.saves,

        performance.engagements,
        performance.engagement_rate,

        result.cpm,
        result.emv,

        datetime.utcnow().isoformat()
    ))

    connection.commit()
    connection.close()


def get_all_posts():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM posts
        ORDER BY created_at DESC
    """)

    posts = cursor.fetchall()

    connection.close()

    return posts


def get_total_emv():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(emv), 0)
        FROM posts
    """)

    total = cursor.fetchone()[0]

    connection.close()

    return total


def get_total_engagements():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(engagements), 0)
        FROM posts
    """)

    total = cursor.fetchone()[0]

    connection.close()

    return total
