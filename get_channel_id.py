#!/usr/bin/env python3
"""
Скрипт для получения chat_id канала Telegram
"""

import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

async def get_channel_id():
    """Получить chat_id канала"""
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    
    try:
        # Попробовать получить информацию о канале
        channel_username = "@optimaai_tg"
        
        # Метод 1: Через getChat
        try:
            chat = await bot.get_chat(channel_username)
            print(f"✅ Канал найден!")
            print(f"ID: {chat.id}")
            print(f"Название: {chat.title}")
            print(f"Username: @{chat.username}")
            print(f"Тип: {chat.type}")
            
            # Проверить права администратора
            try:
                admins = await bot.get_chat_administrators(chat.id)
                bot_admin = False
                for admin in admins:
                    if admin.user.id == (await bot.get_me()).id:
                        bot_admin = True
                        print(f"✅ Бот является администратором канала")
                        break
                
                if not bot_admin:
                    print(f"❌ Бот НЕ является администратором канала")
                    print(f"Добавьте бота как администратора с правами на отправку сообщений")
                    
            except Exception as e:
                print(f"❌ Ошибка проверки прав администратора: {e}")
                
        except Exception as e:
            print(f"❌ Ошибка получения информации о канале: {e}")
            print(f"Возможные причины:")
            print(f"1. Бот не добавлен в канал как администратор")
            print(f"2. Канал приватный и бот не имеет доступа")
            print(f"3. Неверное имя канала")
            
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(get_channel_id())