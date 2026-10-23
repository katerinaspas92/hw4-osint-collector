import sqlite3

from api import fetch_posts
from database import (
    init_db,
    save_post,
    get_progress,
    save_progress,
)

DB_NAME = "osint_data.db"
SOURCE = "mastodon.world:backfill"
URL = "https://mastodon.world/api/v1/timelines/public"

PAGE_LIMIT = 40
MAX_REQUESTS = 5


def get_oldest_id():
    """Находит самый старый ID в локальной базе."""
    with sqlite3.connect(DB_NAME) as db:
        row = db.execute(
            "SELECT id FROM posts ORDER BY CAST(id AS INTEGER) ASC LIMIT 1"
        ).fetchone()

    return row[0] if row else None


def backfill():
    """Загружает более старые публикации Mastodon."""
    init_db()

    progress = get_progress(SOURCE)

    if progress is not None:
        cursor = progress["resume_max_id"]
        anchor_id = progress["newest_id"]
        print("Продолжаем исторический сбор с ID:", cursor)
    else:
        cursor = get_oldest_id()
        anchor_id = cursor

        if cursor is None:
            print("База пуста. Сначала запусти collector.py.")
            return

        print("Начинаем загрузку истории до ID:", cursor)

    total = 0

    for page_number in range(1, MAX_REQUESTS + 1):
        params = {
            "limit": PAGE_LIMIT,
            "max_id": cursor,
        }

        posts = fetch_posts(URL, params)

        if not posts:
            print("Более старые публикации не найдены.")
            break

        new_cursor = posts[-1]["id"]

        if int(new_cursor) >= int(cursor):
            print("Пагинация не продвигается назад. Остановка.")
            break

        for post in posts:
            save_post(post)

        total += len(posts)
        cursor = new_cursor

        save_progress(SOURCE, anchor_id, cursor)

        print(
            f"Страница {page_number}: "
            f"получено {len(posts)} публикаций."
        )

    print("Исторический сбор завершил текущий запуск.")
    print("Обработано публикаций:", total)
    print("Последний ID для продолжения:", cursor)


if __name__ == "__main__":
    backfill()
