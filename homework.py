import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler

import requests

import telegram

from dotenv import load_dotenv
from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN', default=False)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', default=False)
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', default=False)

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logs.log',
    encoding='utf-8',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s'
)
handler.setFormatter(formatter)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logger.debug('Проверка переменных окружения')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(
            f'Собщение отправлено в чат {TELEGRAM_CHAT_ID}: {message}'
        )
    except Exception:
        logger.error('Сообщение не было отправлено')
        raise Exception


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        params = {'from_date': 0}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logging.error(f'Ошибка при запросе к API-сервису: {error}')
        raise Exception
    if response.status_code != HTTPStatus.OK:
        logger.error(f'Ошибка HTTP: {response.status_code}')
        raise Exception
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        logger.error(
            'В ответе API структура данных не соответствует ожиданиям:',
            'получен список вместо ожидаемого словаря.'
        )
        raise TypeError
    homeworks = response.get('homeworks')
    if homeworks is None:
        logger.error('В ответе API отсуствует ключ "homeworks"')
        raise KeyError
    if type(response['homeworks']) is not list:
        logger.error('Данные ответа API пришли не ввиде списка')
        raise TypeError
    try:
        homework = homeworks[0]
    except IndexError:
        logger.error('В ответе API нет записей по ключу "homeworks"')
        raise IndexError
    return homework


def parse_status(homework):
    """Извлекает из информации в ответе.
    О конкретной домашней работе статус
    этой работы.
    """
    keys = ['homework_name', 'status']
    for i in keys:
        if i not in homework:
            logger.error(f'Отсуствует ключ "{i}" в {homework}')
            raise KeyError
    homework_name = homework[keys[0]]
    homework_status = homework[keys[1]]
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error(f'Ошибка статуса работы: {homework_status}')
        raise Exception
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Не установлены переменные окружения')
        sys.exit()
    logger.info('Бот запуск - успешно')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            message = parse_status(check_response(get_api_answer(timestamp)))
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(f'Сбой в работе программы: {error}')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
