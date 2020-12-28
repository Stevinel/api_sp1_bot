import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename="homework.log",
    filemode="a",
    format="%(asctime)s, %(levelname)s, %(name)s, %(message)s",
)
logger = logging.getLogger("__name__")
handler = RotatingFileHandler("homework.log", maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRAKTIKUM_API_URL = (
    "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
)


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_name is None or homework_status is None:
        return "problems with parse hw_status"
    if homework_status == "reviewing":
        verdict = "Работа взята в ревью."
    elif homework_status == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    elif homework_status == "approved":
        verdict = (
            "Ревьюеру всё понравилось," " можно приступать к следующему уроку."
        )
    else:
        return "noname status"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    current_timestamp = current_timestamp or int(time.time())
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    params = {
        "from_date": current_timestamp,
    }
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_API_URL, params=params, headers=headers
        )
        return homework_statuses.json()
    except (requests.exceptions.RequestException, ValueError):
        return {}


def send_message(message, BOT_CLIENT):
    return BOT_CLIENT.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logging.info("Bot started work")
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            logging.info("Trying to sent message")
            if new_homework.get("homeworks"):
                send_message(
                    parse_homework_status(new_homework.get("homeworks")[0]),
                    bot_client,
                )
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )
            logging.info("A request was made")
            time.sleep(1200)
        except Exception as error:
            logger.error(error, exc_info=True)
            logging.error(
                send_message("creator, we have a problems", bot_client)
            )
            time.sleep(300)


if __name__ == "__main__":
    main()
