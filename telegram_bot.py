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
from post_editor import PostEditor
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

# Инициализация редактора постов
post_editor = PostEditor(api_key=os.getenv('OPENAI_API_KEY'))

# Инициализация бота и диспетчера с FSM
storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher(storage=storage)

# Состояния для FSM
class NewsStates(StatesGroup):
    waiting_for_approval = State()
    edit_instruction = State()  # Новое состояние для редактирования

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

# Функция для безопасного получения поста
def get_post_safely(post_id: str, user_id: int = None):
    """Безопасно получить пост из хранилища"""
    if post_id not in pending_posts:
        logger.warning(f"Пост {post_id} не найден в хранилище. Доступные посты: {list(pending_posts.keys())}")
        return None
    
    post_data = pending_posts[post_id]
    
    # Дополнительная проверка владельца (опционально)
    if user_id and post_data.get('user_id') != user_id:
        logger.warning(f"Пост {post_id} принадлежит другому пользователю")
        return None
        
    return post_data

class TelegramNewsBot:
    def __init__(self):
        # Получаем ID канала и преобразуем в int если это возможно
        channel_id_str = os.getenv('TELEGRAM_CHANNEL_ID')
        if channel_id_str:
            try:
                self.channel_id = int(channel_id_str)
            except ValueError:
                self.channel_id = channel_id_str  # Оставляем как строку если не число
        else:
            self.channel_id = None
            
        self.channel_username = os.getenv('TELEGRAM_CHANNEL_USERNAME', '@optimaai_tg')
        logger.info(f"Инициализация бота с каналом: {self.channel_username} (ID: {self.channel_id})")
        logger.info(f"Тип channel_id: {type(self.channel_id)}, значение из env: '{channel_id_str}'")
        
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
    
    async def edit_post_with_ai(self, original_post: str, edit_instructions: str) -> str:
        """Редактировать пост с помощью ИИ"""
        try:
            return await post_editor.edit_post(original_post, edit_instructions)
        except Exception as e:
            logger.error(f"Ошибка редактирования поста: {e}")
            raise e
    
    async def publish_to_channel(self, post_content: str):
        """Опубликовать пост в канале"""
        # Определить целевой канал
        target_channel = self.channel_id or self.channel_username
        
        if not target_channel:
            logger.error("Канал не настроен - отсутствует TELEGRAM_CHANNEL_ID и TELEGRAM_CHANNEL_USERNAME")
            return "⚠️ Канал не настроен в переменных окружения"
        
        try:
            logger.info(f"Попытка публикации в канал: {target_channel} (тип: {type(target_channel)})")
            logger.info(f"channel_id: {self.channel_id}, channel_username: {self.channel_username}")
            
            # Сначала проверить доступ к каналу
            try:
                chat_info = await bot.get_chat(target_channel)
                logger.info(f"Канал найден: {chat_info.title} (ID: {chat_info.id})")
                
                # Проверить права администратора
                try:
                    admins = await bot.get_chat_administrators(chat_info.id)
                    bot_info = await bot.get_me()
                    is_admin = any(admin.user.id == bot_info.id for admin in admins)
                    
                    if not is_admin:
                        logger.error(f"Бот не является администратором канала {target_channel}")
                        return "❌ Бот не является администратором канала. Добавьте бота как администратора с правами на отправку сообщений."
                        
                    logger.info("Бот имеет права администратора")
                    
                except Exception as admin_error:
                    logger.warning(f"Не удалось проверить права администратора: {admin_error}")
                    
            except Exception as chat_error:
                logger.error(f"Не удалось получить информацию о канале {target_channel}: {chat_error}")
                return f"❌ Канал не найден или недоступен: {target_channel}. Убедитесь, что бот добавлен в канал."
            
            # Отправить сообщение (без Markdown, так как контент уже очищен от символов)
            message = await bot.send_message(
                chat_id=target_channel,
                text=post_content,
                parse_mode=None,  # Убираем Markdown, так как контент уже очищен
                disable_web_page_preview=False
            )
            
            logger.info(f"✅ Пост успешно опубликован в канале {target_channel} (message_id: {message.message_id})")
            return f"✅ Пост успешно опубликован в канале {chat_info.title}!"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Ошибка публикации в канале {target_channel}: {error_msg}")
            
            # Детализированная обработка ошибок
            if "chat not found" in error_msg.lower():
                return f"❌ Канал {target_channel} не найден. Проверьте правильность имени канала."
            elif "not enough rights" in error_msg.lower() or "forbidden" in error_msg.lower():
                return f"❌ Недостаточно прав для публикации в канале {target_channel}. Добавьте бота как администратора."
            elif "bot was blocked" in error_msg.lower():
                return f"❌ Бот заблокирован в канале {target_channel}."
            else:
                return f"❌ Ошибка публикации: {error_msg}"

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
                text="✏️ Редактировать", 
                callback_data=f"edit_{post_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Другой вариант", 
                callback_data=f"regenerate_{post_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data=f"cancel_{post_id}"
            )
        ]
    ])
    return keyboard

def create_quick_edit_keyboard(post_id: str) -> InlineKeyboardMarkup:
    """Создать клавиатуру для быстрого редактирования"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎯 Сделать короче", 
                callback_data=f"quick_edit_{post_id}_shorter"
            ),
            InlineKeyboardButton(
                text="📝 Добавить деталей", 
                callback_data=f"quick_edit_{post_id}_details"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔥 Более привлекательно", 
                callback_data=f"quick_edit_{post_id}_engaging"
            ),
            InlineKeyboardButton(
                text="📊 Добавить эмодзи", 
                callback_data=f"quick_edit_{post_id}_emoji"
            )
        ],
        [
            InlineKeyboardButton(
                text="✍️ Свои инструкции", 
                callback_data=f"custom_edit_{post_id}"
            ),
            InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data=f"back_to_post_{post_id}"
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
        "• ✏️ **Редактирование постов с ИИ**\n"
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
        "   • ✏️ **Редактировать** - изменить пост с помощью ИИ\n"
        "   • 🔄 **Другой вариант** - сгенерировать заново\n"
        "   • ❌ **Отменить** - отменить публикацию\n\n"
        "✏️ **Как работает редактирование:**\n"
        "1️⃣ Нажмите кнопку **Редактировать**\n"
        "2️⃣ Опишите, что нужно изменить\n"
        "3️⃣ ИИ применит ваши изменения\n"
        "4️⃣ Просмотрите результат и выберите действие\n\n"
        "🎯 **Примеры редактирования:**\n"
        "• 'Сделай заголовок более привлекательным'\n"
        "• 'Добавь больше деталей о криптовалютах'\n"
        "• 'Убери информацию о спорте'\n"
        "• 'Сделай текст короче'",
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
            f"✏️ ИИ-редактор: ✅ Активен\n"
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
            'original_content': post_content,  # Сохраняем оригинал для редактирования
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

@dp.callback_query(F.data.startswith("edit_"))
async def edit_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик редактирования поста"""
    post_id = callback.data.split("_", 1)[1]
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    # Показать варианты редактирования
    await callback.message.edit_text(
        f"✏️ **Редактирование поста**\n\n"
        f"**Тема:** {post_data['topic']}\n\n"
        f"🚀 **Выберите тип редактирования:**\n\n"
        f"🎯 **Сделать короче** - убрать лишние детали\n"
        f"📝 **Добавить деталей** - расширить информацию\n"
        f"🔥 **Более привлекательно** - улучшить подачу\n"
        f"📊 **Добавить эмодзи** - сделать ярче\n\n"
        f"Или выберите 'Свои инструкции' для пользовательского редактирования:",
        reply_markup=create_quick_edit_keyboard(post_id),
        parse_mode='Markdown'
    )
    
    await callback.answer("✏️ Выберите тип редактирования")

@dp.callback_query(F.data.startswith("quick_edit_"))
async def quick_edit_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик быстрого редактирования"""
    parts = callback.data.split("_")
    post_id = parts[2]
    edit_type = parts[3]
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    # Определить инструкции по типу редактирования
    edit_instructions = {
        "shorter": "Сделай пост короче, убери лишние детали, оставь только самое важное",
        "details": "Добавь больше деталей и подробностей, расширь информацию",
        "engaging": "Сделай пост более привлекательным и интересным, улучши заголовок",
        "emoji": "Добавь больше подходящих эмодзи для лучшего визуального восприятия"
    }
    
    instruction = edit_instructions.get(edit_type, "Улучши пост")
    
    # Показать индикатор загрузки
    await callback.message.edit_text(
        f"🔄 Применяю изменения: {instruction.lower()}...",
        parse_mode='Markdown'
    )
    
    try:
        # Применить редактирование
        edited_content = await telegram_news_bot.edit_post_with_ai(
            post_data['original_content'], 
            instruction
        )
        
        # Обновить данные поста
        pending_posts[post_id]['content'] = edited_content
        
        # Отправить отредактированный пост
        await callback.message.edit_text(
            f"✅ **Пост отредактирован!**\n\n"
            f"📝 **Применено:** {instruction}\n\n"
            f"📰 **Обновленный пост:**\n"
            f"🏷️ **Тема:** {post_data['topic']}\n\n"
            f"---\n\n{edited_content}\n\n---\n\n"
            f"❓ **Что делаем с этим постом?**",
            reply_markup=create_approval_keyboard(post_id),
            parse_mode='Markdown'
        )
        
        await callback.answer("✅ Изменения применены!")
        
    except Exception as e:
        logger.error(f"Ошибка быстрого редактирования: {e}")
        await callback.message.edit_text(
            f"❌ Не удалось применить изменения.\n\n"
            f"**Тема:** {post_data['topic']}\n\n"
            f"Попробуйте другой тип редактирования:",
            reply_markup=create_quick_edit_keyboard(post_id),
            parse_mode='Markdown'
        )
        await callback.answer("❌ Ошибка редактирования")

@dp.callback_query(F.data.startswith("back_to_post_"))
async def back_to_post(callback: CallbackQuery, state: FSMContext):
    """Вернуться к просмотру поста"""
    post_id = callback.data.split("_", 3)[3]
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    # Показать пост с кнопками подтверждения
    await callback.message.edit_text(
        f"📰 **Предварительный просмотр поста:**\n"
        f"🏷️ **Тема:** {post_data['topic']}\n\n"
        f"---\n\n{post_data['content']}\n\n---\n\n"
        f"❓ **Что делаем с этим постом?**",
        reply_markup=create_approval_keyboard(post_id),
        parse_mode='Markdown'
    )
    
    await callback.answer("⬅️ Возврат к посту")

@dp.callback_query(F.data.startswith("custom_edit_"))
async def custom_edit_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик пользовательского редактирования"""
    post_id = callback.data.split("_", 2)[2]
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
    # Обновить сообщение с запросом инструкций
    await callback.message.edit_text(
        f"✏️ **Пользовательское редактирование**\n\n"
        f"**Тема:** {post_data['topic']}\n\n"
        f"📝 **Опишите, что нужно изменить:**\n\n"
        f"Примеры инструкций:\n"
        f"• 'Сделай заголовок более привлекательным'\n"
        f"• 'Добавь больше деталей о технологиях'\n"
        f"• 'Убери информацию о спорте'\n"
        f"• 'Измени тон на более формальный'\n\n"
        f"💬 **Напишите ваши инструкции:**",
        parse_mode='Markdown'
    )
    
    # Установить состояние ожидания инструкций по редактированию
    await state.set_state(NewsStates.edit_instruction)
    await state.update_data(post_id=post_id, message_id=callback.message.message_id)
    
    await callback.answer("✏️ Опишите, что нужно изменить")

@dp.message(NewsStates.edit_instruction)
async def handle_edit_instruction(message: Message, state: FSMContext):
    """Обработчик инструкций по редактированию"""
    try:
        # Получить данные из состояния
        state_data = await state.get_data()
        post_id = state_data.get('post_id')
        message_id = state_data.get('message_id')
        
        if not post_id or post_id not in pending_posts:
            await message.answer("❌ Ошибка: пост не найден")
            await state.clear()
            return
        
        post_data = pending_posts[post_id]
        edit_instructions = message.text
        
        # Показать индикатор загрузки
        loading_message = await message.answer("🔄 Применяю ваши изменения...")
        
        try:
            # Применить редактирование с помощью ИИ
            edited_content = await telegram_news_bot.edit_post_with_ai(
                post_data['original_content'], 
                edit_instructions
            )
            
            # Обновить данные поста
            pending_posts[post_id]['content'] = edited_content
            
            # Удалить сообщение о загрузке
            await loading_message.delete()
            
            # Отправить отредактированный пост
            await message.answer(
                f"✅ **Пост отредактирован!**\n\n"
                f"📝 **Ваши инструкции:** {edit_instructions}\n\n"
                f"📰 **Обновленный пост:**\n"
                f"🏷️ **Тема:** {post_data['topic']}\n\n"
                f"---\n\n{edited_content}\n\n---\n\n"
                f"❓ **Что делаем с этим постом?**",
                reply_markup=create_approval_keyboard(post_id),
                parse_mode='Markdown'
            )
            
            # Вернуться к состоянию ожидания подтверждения
            await state.set_state(NewsStates.waiting_for_approval)
            await state.update_data(post_id=post_id)
            
        except Exception as e:
            logger.error(f"Ошибка редактирования поста: {e}")
            await loading_message.delete()
            await message.answer(
                "❌ Извините, не удалось применить ваши изменения. "
                "Попробуйте еще раз позже или используйте другие опции."
            )
            await state.clear()
            
    except Exception as e:
        logger.error(f"Ошибка обработки инструкций редактирования: {e}")
        await message.answer("❌ Произошла ошибка при обработке ваших инструкций")
        await state.clear()

@dp.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения поста"""
    post_id = callback.data.split("_", 1)[1]
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
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
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
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
        'original_content': new_content,  # Новый оригинал
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
    
    post_data = get_post_safely(post_id, callback.from_user.id)
    if not post_data:
        await callback.answer("❌ Пост не найден или уже обработан", show_alert=True)
        return
    
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
async def handle_text(message: Message, state: FSMContext):
    """Обработчик текстовых сообщений"""
    # Проверить, не находимся ли мы в состоянии редактирования
    current_state = await state.get_state()
    if current_state == NewsStates.edit_instruction:
        # Это сообщение уже обработано в handle_edit_instruction
        return
    
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
    logger.info("🚀 Запуск улучшенного Telegram бота с функцией редактирования...")
    
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