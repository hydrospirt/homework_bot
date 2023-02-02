import os
import sys
import requests
import time
import telegram
import pprint

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN', default='Не найден')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', default='Не найден')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', default='Не найден')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    ENV_STACK = {
        'Praktikum token': PRACTICUM_TOKEN,
        'Telegram_token': TELEGRAM_TOKEN,
        'Telegram_chat_id': TELEGRAM_CHAT_ID }
    for i, v in ENV_STACK.items():
        if v == 'Не найден':
            return sys.exit(f'Установите переменную окружения {i}')
        print(f'Переменная окружения установлена - успешно')
    return print(True)

check_tokens()

def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': 0}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params).json()
    print(response)

def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        raise KeyError
    try:
        homework = homeworks[0]
    except IndexError:
        raise IndexError
    return homework

def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    keys = ['homework_name', 'status']
    for i in keys:
        if i not in homework:
            raise KeyError(f'ты умен! {i}')


timestamp = int(time.time())

print(timestamp)
get_api_answer(timestamp)
# check_response(get_api_answer(timestamp))
# parse_status(check_response(get_api_answer(timestamp)))