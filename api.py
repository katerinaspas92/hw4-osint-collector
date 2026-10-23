import requests
import time
import logging

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

logging.basicConfig(
    filename="collector.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

MAX_RETRIES = 5
BASE_DELAY = 2
REQUEST_DELAY = 2

def get_retry_delay(retry_after, attempt):
    fallback = BASE_DELAY * (2 ** attempt)

    if not retry_after:
        return fallback

    try:
        return max(0, int(retry_after))
    except ValueError:
        pass

    try:
        retry_date = parsedate_to_datetime(retry_after)

        if retry_date.tzinfo is None:
            retry_date = retry_date.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delay = (retry_date - now).total_seconds()

        return max(0, delay)

    except (TypeError, ValueError, OverflowError):
        return fallback


def fetch_posts(url, params):
    for attempt in range(MAX_RETRIES + 1):
        try:
            time.sleep(REQUEST_DELAY)

            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                delay = get_retry_delay(retry_after, attempt)

                logging.warning(
                    "Rate limit 429. Ожидание %s секунд",
                    delay
                )

            elif response.status_code in (500, 502, 503, 504):
                delay = BASE_DELAY * (2 ** attempt)

                logging.warning(
                    "Ошибка сервера %s. Ожидание %s секунд",
                    response.status_code,
                    delay
                )

            else:
                response.raise_for_status()

                logging.info("Запрос выполнен успешно")
                return response.json()

        except requests.HTTPError as error:
            logging.error(
                "Постоянная HTTP-ошибка: %s",
                error
            )
            raise

        except requests.RequestException as error:
            delay = BASE_DELAY * (2 ** attempt)

            logging.error("Ошибка запроса: %s", error)

        if attempt == MAX_RETRIES:
            logging.error("Исчерпаны попытки запроса")
            raise RuntimeError("Не удалось получить данные Mastodon")

        time.sleep(delay)
