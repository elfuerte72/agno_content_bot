#!/usr/bin/env python3
"""
Telegram News Bot - Запуск
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def check_environment():
    """Проверка необходимых переменных окружения"""
    required_vars = [
        'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nПожалуйста, настройте файл .env")
        sys.exit(1)
    
    print("✅ Все переменные окружения настроены")

def main():
    """Основная функция"""
    print("🚀 Запуск Telegram News Bot...")
    
    # Проверить окружение
    check_environment()
    
    # Импортировать и запустить бота
    from telegram_bot import main as bot_main
    asyncio.run(bot_main())

if __name__ == "__main__":
    main()