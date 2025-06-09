#!/usr/bin/env python3
"""
Тестирование публикации в канал
"""

import asyncio
import logging
from aiogram import Bot
from dotenv import load_dotenv
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_publish():
    """Тестирование публикации в канал"""
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    
    # Определить целевой канал
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    channel_username = os.getenv('TELEGRAM_CHANNEL_USERNAME', '@optimaai_tg')
    target_channel = channel_id or channel_username
    
    if not target_channel:
        print("❌ Канал не настроен в переменных окружения")
        return
    
    try:
        print(f"🎯 Тестирование публикации в канал: {target_channel}")
        
        # Тестовый пост
        test_post = f"""🧪 **Тестовая публикация**

📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
🤖 **Источник:** Telegram News Bot

📰 **Тестовые новости:**
• ✅ Бот успешно подключен к каналу
• 🔄 Система публикации работает корректно
• 📊 Все компоненты функционируют

🎉 **Результат:** Публикация в канал настроена и работает!

#тест #бот #новости"""

        # Отправить сообщение
        message = await bot.send_message(
            chat_id=target_channel,
            text=test_post,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        
        print(f"✅ Тестовое сообщение успешно опубликовано!")
        print(f"   Message ID: {message.message_id}")
        print(f"   Дата: {message.date}")
        print(f"   Канал: {target_channel}")
        
        # Подождать и предложить удалить
        print("\n⏳ Ожидание 10 секунд перед удалением тестового сообщения...")
        await asyncio.sleep(10)
        
        try:
            await bot.delete_message(target_channel, message.message_id)
            print("🗑️ Тестовое сообщение удалено")
        except Exception as delete_error:
            print(f"⚠️ Не удалось удалить тестовое сообщение: {delete_error}")
            print("   (Это нормально, если у бота нет прав на удаление)")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка при тестировании: {error_msg}")
        
        # Диагностика
        if "chat not found" in error_msg.lower():
            print("💡 Канал не найден. Проверьте:")
            print("   - Правильность имени канала")
            print("   - Добавлен ли бот в канал")
        elif "forbidden" in error_msg.lower() or "not enough rights" in error_msg.lower():
            print("💡 Недостаточно прав. Проверьте:")
            print("   - Является ли бот администратором канала")
            print("   - Есть ли у бота права на отправку сообщений")
        elif "bot was blocked" in error_msg.lower():
            print("💡 Бот заблокирован в канале")
            
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_publish())