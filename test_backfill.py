from unittest.mock import patch

import backfill


def test_history_collection():
    pages = [
        [{"id": "99"}, {"id": "98"}, {"id": "97"}],
        [{"id": "96"}, {"id": "95"}, {"id": "94"}],
        [],
    ]

    saved_posts = []
    saved_progress = []
    requested_cursors = []

    def fake_fetch(url, params):
        requested_cursors.append(params["max_id"])
        return pages.pop(0)

    with (
        patch.object(backfill, "init_db"),
        patch.object(backfill, "get_progress", return_value=None),
        patch.object(backfill, "get_oldest_id", return_value="100"),
        patch.object(backfill, "fetch_posts", side_effect=fake_fetch),
        patch.object(
            backfill,
            "save_post",
            side_effect=lambda post: saved_posts.append(post["id"]),
        ),
        patch.object(
            backfill,
            "save_progress",
            side_effect=lambda *args: saved_progress.append(args),
        ),
    ):
        backfill.backfill()

    assert requested_cursors == ["100", "97", "94"]
    assert saved_posts == ["99", "98", "97", "96", "95", "94"]
    assert saved_progress[-1] == (
        "mastodon.world:backfill",
        "100",
        "94",
    )

    print("ТЕСТ BACKFILL ПРОЙДЕН!")


if __name__ == "__main__":
    test_history_collection()
