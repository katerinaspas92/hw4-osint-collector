from unittest.mock import patch, Mock

from api import fetch_posts


def test_rate_limit():
    response_429 = Mock()
    response_429.status_code = 429
    response_429.headers = {"Retry-After": "3"}

    response_200 = Mock()
    response_200.status_code = 200
    response_200.json.return_value = [{"id": "12345"}]

    with patch("api.requests.get") as mock_get, \
         patch("api.time.sleep") as mock_sleep:

        mock_get.side_effect = [response_429, response_200]

        result = fetch_posts(
            "https://example.com/api",
            {"limit": 2}
        )

        assert result == [{"id": "12345"}]
        assert mock_get.call_count == 2
        assert mock_sleep.call_args_list[1].args[0] == 3

    print("ТЕСТ 429 ПРОЙДЕН!")

def test_server_error():
    response_503 = Mock()
    response_503.status_code = 503

    response_200 = Mock()
    response_200.status_code = 200
    response_200.json.return_value = [{"id": "67890"}]

    with patch("api.requests.get") as mock_get, \
         patch("api.time.sleep") as mock_sleep:

        mock_get.side_effect = [response_503, response_200]

        result = fetch_posts(
            "https://example.com/api",
            {"limit": 2}
        )

        assert result == [{"id": "67890"}]
        assert mock_get.call_count == 2
        assert mock_sleep.call_args_list[1].args[0] == 2

    print("ТЕСТ 503 ПРОЙДЕН!")

def test_forbidden():
    response_403 = Mock()
    response_403.status_code = 403

    response_403.raise_for_status.side_effect = (
        __import__("requests").HTTPError("403 Forbidden")
    )

    with patch("api.requests.get") as mock_get, \
         patch("api.time.sleep"):

        mock_get.return_value = response_403

        try:
            fetch_posts(
                "https://example.com/api",
                {"limit": 2}
            )

            assert False, "Ошибка 403 не была обработана"

        except __import__("requests").HTTPError:
            pass

        assert mock_get.call_count == 1

    print("ТЕСТ 403 ПРОЙДЕН!")

def test_connection_error():
    import requests

    response_200 = Mock()
    response_200.status_code = 200
    response_200.json.return_value = [{"id": "99999"}]

    with patch("api.requests.get") as mock_get, \
         patch("api.time.sleep") as mock_sleep:

        mock_get.side_effect = [
            requests.ConnectionError("Нет соединения"),
            response_200
        ]

        result = fetch_posts(
            "https://example.com/api",
            {"limit": 2}
        )

        assert result == [{"id": "99999"}]
        assert mock_get.call_count == 2
        assert mock_sleep.call_args_list[1].args[0] == 2

    print("ТЕСТ CONNECTION ERROR ПРОЙДЕН!")

if __name__ == "__main__":
    test_rate_limit()

    test_server_error()

    test_forbidden()

    test_connection_error()
