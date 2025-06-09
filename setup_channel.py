#!/usr/bin/env python3
"""
Скрипт для настройки и диагностики канала Telegram
"""

import asyncio
import logging
from aiogram import Bot
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

async def setup_channel():
    """Настройка и проверка канала"""
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    
    try:
        # Информация о боте
        bot_info = await bot.get_me()
        print(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
        print(f"📝 Имя: {bot_info.first_name}")
        print()
        
        # Проверить каналы
        channels_to_check = [
            "@optimaai_tg",
            os.getenv('TELEGRAM_CHANNEL_ID'),
            os.getenv('TELEGRAM_CHANNEL_USERNAME')
        ]
        
        # Убрать пустые значения
        channels_to_check = [ch for ch in channels_to_check if ch]
        
        print("🔍 Проверка каналов:")
        print("-" * 50)
        
        for channel in channels_to_check:
            print(f"\n📺 Проверка канала: {channel}")
            
            try:
                # Получить информацию о канале
                chat = await bot.get_chat(channel)
                print(f"✅ Канал найден!")
                print(f"   ID: {chat.id}")
                print(f"   Название: {chat.title}")
                print(f"   Username: @{chat.username if chat.username else 'Не установлен'}")
                print(f"   Тип: {chat.type}")
                print(f"   Описание: {chat.description[:100] if chat.description else 'Отсутствует'}...")
                
                # Проверить права администратора
                try:
                    admins = await bot.get_chat_administrators(chat.id)
                    print(f"   👥 Администраторов: {len(admins)}")
                    
                    bot_is_admin = False
                    bot_permissions = None
                    
                    for admin in admins:
                        if admin.user.id == bot_info.id:
                            bot_is_admin = True
                            bot_permissions = admin
                            break
                    
                    if bot_is_admin:
                        print(f"   ✅ Бот является администратором")
                        
                        # Проверить конкретные права
                        perms = bot_permissions
                        if hasattr(perms, 'can_post_messages'):
                            print(f"   📝 Может отправлять сообщения: {'✅' if perms.can_post_messages else '❌'}")
                        if hasattr(perms, 'can_edit_messages'):
                            print(f"   ✏️ Может редактировать сообщения: {'✅' if perms.can_edit_messages else '❌'}")
                        if hasattr(perms, 'can_delete_messages'):
                            print(f"   🗑️ Может удалять сообщения: {'✅' if perms.can_delete_messages else '❌'}")
                            
                    else:
                        print(f"   ❌ Бот НЕ является администратором")
                        print(f"   💡 Добавьте бота @{bot_info.username} как администратора канала")
                        print(f"   📋 Необходимые права:")
                        print(f"      - Отправка сообщений")
                        print(f"      - Редактирование сообщений (опционально)")
                        
                except Exception as admin_error:
                    print(f"   ⚠️ Не удалось проверить права администратора: {admin_error}")
                    
                # Попробовать отправить тестовое сообщение
                try:
                    test_message = await bot.send_message(
                        chat_id=chat.id,
                        text="🧪 Тестовое сообщение от бота\n\nЭто сообщение подтверждает, что бот может публиковать в канале.",
                        parse_mode='Markdown'
                    )
                    print(f"   ✅ Тестовое сообщение отправлено (ID: {test_message.message_id})")
                    
                    # Удалить тестовое сообщение через 5 секунд
                    await asyncio.sleep(2)
                    try:
                        await bot.delete_message(chat.id, test_message.message_id)
                        print(f"   🗑️ Тестовое сообщение удалено")
                    except:
                        print(f"   ⚠️ Не удалось удалить тестовое сообщение")
                        
                except Exception as send_error:
                    print(f"   ❌ Не удалось отправить тестовое сообщение: {send_error}")
                    
                # Рекомендации для .env файла
                print(f"\n📋 Рекомендуемые настройки для .env:")
                print(f"TELEGRAM_CHANNEL_ID={chat.id}")
                print(f"TELEGRAM_CHANNEL_USERNAME=@{chat.username}")
                
            except Exception as e:
                print(f"❌ Ошибка при проверке канала {channel}: {e}")
                
                # Диагностика ошибок
                error_msg = str(e).lower()
                if "chat not found" in error_msg:
                    print(f"   💡 Канал не найден. Возможные причины:")
                    print(f"      - Неверное имя канала")
                    print(f"      - Канал приватный")
                    print(f"      - Бот не добавлен в канал")
                elif "forbidden" in error_msg:
                    print(f"   💡 Доступ запрещен. Возможные причины:")
                    print(f"      - Бот не добавлен в канал")
                    print(f"      - Недостаточно прав")
                    
        print("\n" + "=" * 50)
        print("🎯 ИНСТРУКЦИИ ПО НАСТРОЙКЕ:")
        print("=" * 50)
        print("1. Добавьте бота в канал @optimaai_tg")
        print("2. Назначьте бота администратором с правами:")
        print("   - Отправка сообщений")
        print("   - Редактирование сообщений (опционально)")
        print("3. Обновите .env файл с правильными значениями")
        print("4. Перезапустите бота")
        
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(setup_channel())