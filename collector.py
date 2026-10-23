

from api import fetch_posts

from database import (
    init_db,
    save_post,
    get_last_id,
    get_progress,
    save_progress,
    finish_collection,
)

def collect_posts():
    init_db()

    source = "mastodon.world"
    last_id = get_last_id(source)

    progress = get_progress(source)

    print("Последний сохранённый ID:", last_id)

    url = "https://mastodon.world/api/v1/timelines/public"

    params = {
        "limit": 40
    }

    if last_id is not None:
        params["since_id"] = last_id

    collection_complete = False 

    resume_max_id = None

    newest_id = None

    max_id = None

    if progress is not None:
        newest_id = progress["newest_id"]
        max_id = progress["resume_max_id"]

        print("Найден незавершённый сбор.")
        print("Продолжаем с ID:", max_id) 

    request_count = 0

    max_requests = 5

    while True:

        if request_count >= max_requests:
            print("Достигнут лимит запросов за один запуск.")
            break

        request_count += 1

        if max_id is not None:
            params["max_id"] = max_id

        posts = fetch_posts(url, params)

        if not posts:
            print("Новых публикаций больше нет.")

            collection_complete = True

            break

        if newest_id is None:
            newest_id = posts[0]["id"]

        for post in posts:

            save_post(post)

            print("Автор:", post["account"]["username"])
            print("Дата:", post["created_at"])
            print("Ссылка:", post["url"])
            print("Текст:", post["content"])
            print("-" * 50)

        new_max_id = posts[-1]["id"]

        if max_id is not None and int(new_max_id) >= int(max_id):
            print("Пагинация не продвигается назад. Останавливаем сбор.")
            break
        max_id = new_max_id

        save_progress(source, newest_id, max_id)

        if len(posts) < params["limit"]:
            print("Получена неполная страница. Проверяем завершение сбора.")


    if collection_complete and newest_id is not None:
        finish_collection(source, newest_id)

        print("Сбор завершён успешно.")
        print("Новый сохранённый курсор:", newest_id)

    else:
        print("Сбор не завершён полностью.")
        print("Промежуточный прогресс сохранён.")


if __name__ == "__main__":
    collect_posts()
