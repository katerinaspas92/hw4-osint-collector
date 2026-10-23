import os
from unittest.mock import Mock, patch

from api import fetch_posts


def test_without_proxy():
    response = Mock()
    response.status_code = 200
    response.json.return_value = [{"id": "123"}]

    with patch.dict(os.environ, {"OSINT_PROXY_URL": ""}):
        with patch("api.requests.get", return_value=response) as mock_get:
            with patch("api.time.sleep"):
                result = fetch_posts(
                    "https://mastodon.world/api/v1/timelines/public",
                    {"limit": 1},
                )

    assert result == [{"id": "123"}]
    assert mock_get.call_args.kwargs["proxies"] is None

    print("ТЕСТ БЕЗ ПРОКСИ ПРОЙДЕН!")


def test_with_proxy():
    response = Mock()
    response.status_code = 200
    response.json.return_value = [{"id": "456"}]

    proxy_url = "http://127.0.0.1:8080"

    with patch.dict(os.environ, {"OSINT_PROXY_URL": proxy_url}):
        with patch("api.requests.get", return_value=response) as mock_get:
            with patch("api.time.sleep"):
                result = fetch_posts(
                    "https://mastodon.world/api/v1/timelines/public",
                    {"limit": 1},
                )

    assert result == [{"id": "456"}]
    assert mock_get.call_args.kwargs["proxies"] == {
        "http": proxy_url,
        "https": proxy_url,
    }

    print("ТЕСТ С ПРОКСИ ПРОЙДЕН!")


if __name__ == "__main__":
    test_without_proxy()
    test_with_proxy()
