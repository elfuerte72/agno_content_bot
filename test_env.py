#!/usr/bin/env python3
"""
Тестовый скрипт для проверки переменных окружения
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

print("=== Проверка переменных окружения ===")
print(f"TELEGRAM_CHANNEL_ID: '{os.getenv('TELEGRAM_CHANNEL_ID')}'")
print(f"TELEGRAM_CHANNEL_USERNAME: '{os.getenv('TELEGRAM_CHANNEL_USERNAME')}'")
print(f"TELEGRAM_BOT_TOKEN: '{os.getenv('TELEGRAM_BOT_TOKEN')[:20]}...'")

# Проверяем преобразование типов
channel_id_str = os.getenv('TELEGRAM_CHANNEL_ID')
if channel_id_str:
    try:
        channel_id_int = int(channel_id_str)
        print(f"Преобразование в int: {channel_id_int} (тип: {type(channel_id_int)})")
    except ValueError as e:
        print(f"Ошибка преобразования в int: {e}")
else:
    print("TELEGRAM_CHANNEL_ID не найден!")

print("=== Конец проверки ===")