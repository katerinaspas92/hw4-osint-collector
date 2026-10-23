import os
from unittest.mock import Mock, patch, call

import api


def make_response(status, data=None, headers=None):
    response = Mock()
    response.status_code = status
    response.headers = headers or {}
    response.json.return_value = data or []
    return response


def test_rotation():
    with patch.dict(os.environ, {"OSINT_API_TOKENS": "TOKEN_A,TOKEN_B,TOKEN_C"}):
        api._token_index = 0

        with patch("api.requests.get", return_value=make_response(200)) as get:
            with patch("api.time.sleep"):
                for _ in range(4):
                    api.fetch_posts("https://example.com/api", {"limit": 1})

        tokens = [
            item.kwargs["headers"]["Authorization"]
            for item in get.call_args_list
        ]

        assert tokens == [
            "Bearer TOKEN_A",
            "Bearer TOKEN_B",
            "Bearer TOKEN_C",
            "Bearer TOKEN_A",
        ]

    print("ТЕСТ РОТАЦИИ ПРОЙДЕН!")


def test_without_tokens():
    with patch.dict(os.environ, {"OSINT_API_TOKENS": ""}):
        with patch("api.requests.get", return_value=make_response(200)) as get:
            with patch("api.time.sleep"):
                api.fetch_posts("https://example.com/api", {"limit": 1})

        assert "headers" not in get.call_args.kwargs

    print("ТЕСТ БЕЗ ТОКЕНОВ ПРОЙДЕН!")


def test_rate_limit():
    responses = [
        make_response(429, headers={"Retry-After": "1"}),
        make_response(200),
    ]

    with patch.dict(os.environ, {"OSINT_API_TOKENS": "TOKEN_A,TOKEN_B"}):
        api._token_index = 0

        with patch("api.requests.get", side_effect=responses) as get:
            with patch("api.time.sleep") as sleep:
                api.fetch_posts("https://example.com/api", {"limit": 1})

        first = get.call_args_list[0].kwargs["headers"]["Authorization"]
        second = get.call_args_list[1].kwargs["headers"]["Authorization"]

        assert first == second == "Bearer TOKEN_A"
        assert call(1) in sleep.call_args_list

    print("ТЕСТ 429 БЕЗ СМЕНЫ ТОКЕНА ПРОЙДЕН!")


if __name__ == "__main__":
    test_rotation()
    test_without_tokens()
    test_rate_limit()
