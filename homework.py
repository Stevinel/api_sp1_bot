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
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or ""
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRAKTIKUM_API_URL = (
    "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
)
BOT_CLIENT = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    try:
        if homework["status"] == "reviewing":
            verdict = "Работа взята в ревью."
        elif homework["status"] == "rejected":
            verdict = "К сожалению в работе нашлись ошибки."
        else:
            verdict = ('Ревьюеру всё понравилось,'
            ' можно приступать к следующему уроку.')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as error:
        print(f"bot have a problems with parse_hw_status: {error}")
        logging.error(
            send_message(
                "Значения status или home_work_name пусты или несоответствуют",
                BOT_CLIENT,
            )
        )


def get_homework_statuses(current_timestamp):
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    params = {
        "from_date": current_timestamp,
    }
    if current_timestamp is None:
        current_timestamp = int(time.time())
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_API_URL, params=params, headers=headers
        )
    except requests.RequestException as error:
        return logging.error(error, exc_info=True)
    else:
        return homework_statuses.json()


def send_message(message, BOT_CLIENT):
    return BOT_CLIENT.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    logging.info("Bot started work")
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get("homeworks"):
                send_message(
                    parse_homework_status(new_homework.get("homeworks")[0]),
                    BOT_CLIENT,
                )
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )
            logging.info("Message sent")
            time.sleep(1200)
        except Exception as e:
            print(f"bot have a problem: {e}")
            logging.error(
                send_message("creator, we have a problems", BOT_CLIENT)
            )
            time.sleep(5)


if __name__ == "__main__":
    main()
