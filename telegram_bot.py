import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from news_agent import NewsAgent
from content_formatter import ContentFormatter
from datetime import datetime
import hashlib

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверка обязательных переменных окружения
required_env_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    logger.error(f"Отсутствуют обязательные переменные окружения: {missing_vars}")
    exit(1)

# Инициализация бота и диспетчера с FSM
storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher(storage=storage)

# Состояния для FSM
class NewsStates(StatesGroup):
    waiting_for_approval = State()

# Инициализация агентов
try:
    news_agent = NewsAgent()
    content_formatter = ContentFormatter()
    logger.info("Агенты инициализированы успешно")
except Exception as e:
    logger.error(f"Ошибка инициализации агентов: {e}")
    exit(1)

# Хранилище для постов (в продакшене используйте базу данных)
pending_posts = {}

class TelegramNewsBot:
    def __init__(self):
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
    async def generate_news_post(self, topic: str = "latest news"):
        """Генерировать новостной пост"""
        try:
            logger.info(f"Получение новостей по теме: {topic}")
            
            # Шаг 1: Получить новости
            raw_news = news_agent.get_latest_news(topic)
            logger.info("Новости получены успешно")
            
            # Шаг 2: Форматировать контент
            formatted_post = content_formatter.format_news_post(raw_news)
            logger.info("Контент отформатирован")
            
            return formatted_post
                
        except Exception as e:
            logger.error(f"Ошибка при обработке новостей: {e}")
            return f"❌ Ошибка: {str(e)}"
    
    async def publish_to_channel(self, post_content: str):
        """Опубликовать пост в канале"""
        if not self.channel_id:
            return "⚠️ Канал не настроен"
        
        try:
            await bot.send_message(
                chat_id=self.channel_id,
                text=post_content,
                parse_mode='Markdown'
            )
            logger.info(f"Пост опубликован в канале {self.channel_id}")
            return "✅ Пост успешно опубликован в канале!"
        except Exception as e:
            logger.error(f"Ошибка публикации в канале: {e}")
            return f"❌ Ошибка публикации: {str(e)}"

# Создание экземпляра бота
telegram_news_bot = TelegramNewsBot()

def create_approval_keyboard(post_id: str) -> InlineKeyboardMarkup:
    """Создать клавиатуру для подтверждения поста"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтверждаю", 
                callback_data=f"approve_{post_id}"
            ),
            InlineKeyboardButton(
                text="🔄 Другой вариант", 
                callback_data=f"regenerate_{post_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data=f"cancel_{post_id}"
            )
        ]
    ])
    return keyboard

def generate_post_id(user_id: int, topic: str) -> str:
    """Генерировать уникальный ID для поста"""
    content = f"{user_id}_{topic}_{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:8]

@dp.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "🤖 Привет! Я улучшенный бот для получения новостей.\n\n"
        "📰 **Новые возможности:**\n"
        "• Предварительный просмотр постов\n"
        "• Подтверждение перед публикацией\n"
        "• Возможность перегенерации контента\n\n"
        "**Доступные команды:**\n"
        "📰 /news - Получить последние новости\n"
        "🔍 /news <тема> - Получить новости по теме\n"
        "⚙️ /status - Проверить статус бота\n"
        "ℹ️ /help - Показать справку",
        parse_mode='Markdown'
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 **Справка по командам:**\n\n"
        "🔹 `/start` - Начать работу с ботом\n"
        "🔹 `/news` - Получить последние новости\n"
        "🔹 `/news технологии` - Новости по теме 'технологии'\n"
        "🔹 `/status` - Проверить работу бота\n\n"
        "💡 **Как работает публикация:**\n"
        "1️⃣ Запросите новости командой `/news`\n"
        "2️⃣ Просмотрите сгенерированный пост\n"
        "3️⃣ Выберите действие:\n"
        "   • ✅ **Подтверждаю** - опубликовать в канале\n"
        "   • 🔄 **Другой вариант** - сгенерировать заново\n"
        "   • ❌ **Отменить** - отменить публикацию\n\n"
        "🎯 **Примеры использования:**\n"
        "• `/news` - общие новости\n"
        "• `/news криптовалюты` - новости о криптовалютах\n"
        "• `/news спорт` - спортивные новости",
        parse_mode='Markdown'
    )

@dp.message(Command("status"))
async def status_command(message: Message):
    """Обработчик команды /status"""
    try:
        channel_status = "✅ Настроен" if telegram_news_bot.channel_id else "⚠️ Не настроен"
        
        await message.answer(
            f"🔧 **Статус бота:**\n\n"
            f"🤖 Агенты: ✅ Работают\n"
            f"📺 Канал: {channel_status}\n"
            f"📊 Активных постов: {len(pending_posts)}\n"
            f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y')}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка проверки статуса: {str(e)}")

@dp.message(Command("news"))
async def news_command(message: Message, state: FSMContext):
    """Обработчик команды /news"""
    try:
        # Извлечь тему из сообщения
        topic = message.text.replace("/news", "").strip()
        if not topic:
            topic = "последние новости"
        
        # Показать индикатор загрузки
        loading_message = await message.answer("🔄 Генерирую новостной пост, подождите...")
        
        # Сгенерировать пост
        post_content = await telegram_news_bot.generate_news_post(topic)
        
        # Удалить сообщение о загрузке
        await loading_message.delete()
        
        # Создать уникальный ID для поста
        post_id = generate_post_id(message.from_user.id, topic)
        
        # Сохранить пост в хранилище
        pending_posts[post_id] = {
            'content': post_content,
            'topic': topic,
            'user_id': message.from_user.id,
            'created_at': datetime.now()
        }
        
        # Отправить пост с кнопками подтверждения
        await message.answer(
            f"📰 **Предварительный просмотр поста:**\n"
            f"🏷️ **Тема:** {topic}\n\n"
            f"---\n\n{post_content}\n\n---\n\n"
            f"❓ **Что делаем с этим постом?**",
            reply_markup=create_approval_keyboard(post_id),
            parse_mode='Markdown'
        )
        
        # Установить состояние ожидания подтверждения
        await state.set_state(NewsStates.waiting_for_approval)
        await state.update_data(post_id=post_id)
        
    except Exception as e:
        logger.error(f"Ошибка в команде /news: {e}")
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения поста"""
    post_id = callback.data.split("_", 1)[1]
    
    if post_id not in pending_posts:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    post_data = pending_posts[post_id]
    
    # Показать индикатор загрузки
    await callback.message.edit_text(
        f"📤 Публикую пост в канале...\n\n"
        f"**Тема:** {post_data['topic']}",
        parse_mode='Markdown'
    )
    
    # Опубликовать в канале
    result = await telegram_news_bot.publish_to_channel(post_data['content'])
    
    # Обновить сообщение с результатом
    await callback.message.edit_text(
        f"✅ **Пост обработан!**\n\n"
        f"**Тема:** {post_data['topic']}\n"
        f"**Результат:** {result}\n"
        f"**Время:** {datetime.now().strftime('%H:%M:%S')}",
        parse_mode='Markdown'
    )
    
    # Удалить пост из хранилища
    del pending_posts[post_id]
    
    # Очистить состояние
    await state.clear()
    
    await callback.answer("✅ Пост опубликован!")

@dp.callback_query(F.data.startswith("regenerate_"))
async def regenerate_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик перегенерации поста"""
    post_id = callback.data.split("_", 1)[1]
    
    if post_id not in pending_posts:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    post_data = pending_posts[post_id]
    
    # Показать индикатор загрузки
    await callback.message.edit_text(
        f"🔄 Генерирую новый вариант поста...\n\n"
        f"**Тема:** {post_data['topic']}",
        parse_mode='Markdown'
    )
    
    # Сгенерировать новый пост
    new_content = await telegram_news_bot.generate_news_post(post_data['topic'])
    
    # Создать новый ID для поста
    new_post_id = generate_post_id(callback.from_user.id, post_data['topic'])
    
    # Обновить данные поста
    pending_posts[new_post_id] = {
        'content': new_content,
        'topic': post_data['topic'],
        'user_id': callback.from_user.id,
        'created_at': datetime.now()
    }
    
    # Удалить старый пост
    del pending_posts[post_id]
    
# Отправить новый пост
    await callback.message.edit_text(
        f"📰 **Новый вариант поста:**\n"
        f"🏷️ **Тема:** {post_data['topic']}\n\n"
        f"---\n\n{new_content}\n\n---\n\n"
        f"❓ **Что делаем с этим постом?**",
        reply_markup=create_approval_keyboard(new_post_id),
        parse_mode='Markdown'
    )
    
    await callback.answer("🔄 Новый вариант сгенерирован!")

@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены поста"""
    post_id = callback.data.split("_", 1)[1]
    
    if post_id not in pending_posts:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    post_data = pending_posts[post_id]
    
    # Удалить пост из хранилища
    del pending_posts[post_id]
    
    # Обновить сообщение
    await callback.message.edit_text(
        f"❌ **Пост отменен**\n\n"
        f"**Тема:** {post_data['topic']}\n"
        f"**Время:** {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"Используйте /news для создания нового поста.",
        parse_mode='Markdown'
    )
    
    # Очистить состояние
    await state.clear()
    
    await callback.answer("❌ Пост отменен")

@dp.message()
async def handle_text(message: Message):
    """Обработчик текстовых сообщений"""
    await message.answer(
        "🤔 Я не понимаю эту команду.\n"
        "Используйте /help для просмотра доступных команд."
    )

async def cleanup_old_posts():
    """Очистка старых постов (запускается периодически)"""
    current_time = datetime.now()
    posts_to_remove = []
    
    for post_id, post_data in pending_posts.items():
        # Удалить посты старше 1 часа
        if (current_time - post_data['created_at']).total_seconds() > 3600:
            posts_to_remove.append(post_id)
    
    for post_id in posts_to_remove:
        del pending_posts[post_id]
        logger.info(f"Удален старый пост: {post_id}")

async def periodic_cleanup():
    """Периодическая очистка старых постов"""
    while True:
        await asyncio.sleep(1800)  # Каждые 30 минут
        await cleanup_old_posts()

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск улучшенного Telegram бота...")
    
    try:
        # Проверить подключение к Telegram API
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот подключен: @{bot_info.username}")
        
        # Запустить задачу очистки в фоне
        asyncio.create_task(periodic_cleanup())
        
        # Запустить polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")