import sqlite3

DB_NAME = "osint_data.db"


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            author TEXT,
            url TEXT,
            date TEXT,
            text TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collector_state (
            source TEXT PRIMARY KEY,
            last_id TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_progress (
            source TEXT PRIMARY KEY,
            newest_id TEXT,
            resume_max_id TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_post(post):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO posts (id, author, url, date, text)
        VALUES (?, ?, ?, ?, ?)
    """, (
        post["id"],
        post["account"]["acct"],
        post["url"],
        post["created_at"],
        post["content"]
    ))

    connection.commit()
    connection.close()


def get_last_id(source):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT last_id FROM collector_state WHERE source = ?",
        (source,)
    )

    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]

    return None


def save_last_id(source, last_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO collector_state (source, last_id)
        VALUES (?, ?)
        ON CONFLICT(source)
        DO UPDATE SET last_id = excluded.last_id
    """, (source, last_id))

    connection.commit()
    connection.close()

def get_progress(source):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT newest_id, resume_max_id
        FROM collection_progress
        WHERE source = ?
        """,
        (source,)
    )

    result = cursor.fetchone()
    connection.close()

    if result:
        return {
            "newest_id": result[0],
            "resume_max_id": result[1]
        }

    return None

def save_progress(source, newest_id, resume_max_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO collection_progress (
            source, newest_id, resume_max_id
        )
        VALUES (?, ?, ?)
        ON CONFLICT(source)
        DO UPDATE SET
            newest_id = excluded.newest_id,
            resume_max_id = excluded.resume_max_id
    """, (source, newest_id, resume_max_id))

    connection.commit()
    connection.close()


def clear_progress(source):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM collection_progress WHERE source = ?",
        (source,)
    )

    connection.commit()
    connection.close()


def finish_collection(source, newest_id):
    connection = sqlite3.connect(DB_NAME)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO collector_state (source, last_id)
            VALUES (?, ?)
            ON CONFLICT(source)
            DO UPDATE SET last_id = excluded.last_id
        """, (source, newest_id))

        cursor.execute(
            "DELETE FROM collection_progress WHERE source = ?",
            (source,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
