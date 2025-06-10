# 📋 План улучшения Agno Content Bot для OptimaAI

## 🎯 Цель проекта
Создать интеллектуального Telegram бота для автоматической генерации и публикации контента в канал OptimaAI с использованием мультиагентной архитектуры Agno Framework.

## 📊 Текущее состояние
- ✅ Базовая функциональность генерации новостей
- ✅ Система редактирования постов  
- ✅ Интеграция с Telegram API
- ✅ FSM состояния для управления диалогами

## 🚀 Разделение на задачи

### 📋 **ЗАДАЧА 1: Обновление стиля генерации постов** (Приоритет 1)

**Контекст для агента:**
```
Файлы: @content_formatter.py, @optimai_data/
Цель: Обновить стиль форматирования под требования OptimaAI
```

**Требования:**
- Убрать все markdown символы (`**`, `*`, `#`, `_`, ``` )
- Исключить хэштеги из постов
- Убрать прямые ссылки на источники
- Добавить дружелюбный SMM-стиль
- Объяснять сложные термины простыми словами

**Новые инструкции для агента:**
```python
instructions = [
    "Создавай посты в дружелюбном SMM-стиле для Telegram канала OptimaAI",
    "Объясняй сложные технические термины простыми словами", 
    "НЕ используй markdown символы: **, *, #, _, ```",
    "НЕ добавляй хэштеги в конце поста",
    "НЕ включай прямые ссылки на источники",
    "Пиши как опытный SMM-специалист в сфере ИИ",
    "Делай контент понятным для широкой аудитории",
    "Фокусируйся на практической пользе информации для обучения ИИ",
    "Упоминай OptimaAI как экспертов в области обучения ИИ, когда это уместно"
]
```

**Инструкция для агента:**
> Обнови файл `content_formatter.py` согласно новым требованиям стиля OptimaAI. Используй данные из папки `optimai_data/` для понимания тона и стиля компании. Создай только обновленный `content_formatter.py`.

---

### 📋 **ЗАДАЧА 2: Генерация изображений** (Приоритет 1)

**Контекст для агента:**
```
Цель: Создать модуль для генерации изображений к постам с помощью DALL-E
Новый файл: image_generator.py
```

**Требования:**
- Интеграция с OpenAI DALL-E API
- Агент для создания промптов изображений
- Обработка ошибок генерации
- Возврат URL изображения

**Код для реализации:**
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import openai
import os
from typing import Optional

class PostImageGenerator:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Создавай краткие описания для изображений к новостным постам об ИИ",
                "Стиль: современный, технологичный, профессиональный",
                "Избегай текста на изображениях",
                "Фокусируйся на визуальной метафоре темы",
                "Описание должно быть на английском языке для DALL-E",
                "Максимум 100 слов в описании"
            ]
        )
    
    async def generate_image_prompt(self, post_content: str) -> str:
        """Генерирует промпт для изображения на основе контента поста"""
        response = self.agent.run(
            f"Создай описание изображения для этого поста: {post_content}"
        )
        return response.content
    
    async def generate_image(self, post_content: str) -> Optional[str]:
        """Генерирует изображение для поста"""
        try:
            image_prompt = await self.generate_image_prompt(post_content)
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            return response.data[0].url
        except Exception as e:
            print(f"Ошибка генерации изображения: {e}")
            return None
```

**Инструкция для агента:**
> Создай новый файл `image_generator.py` с классом PostImageGenerator для генерации изображений к постам. Используй предоставленный код как основу, добавь необходимые импорты и обработку ошибок.

---

### 📋 **ЗАДАЧА 3: База знаний OptimaAI** (Приоритет 1)

**Контекст для агента:**
```
Файлы: @optimai_data/ (данные компании)
Цель: Создать векторную базу знаний с информацией о компании
Новый файл: optimai_knowledge.py
```

**Требования:**
- Векторная база данных LanceDB
- Загрузка данных из папки optimai_data/
- Поиск по базе знаний
- Источники трендов ИИ для российского рынка

**Код для реализации:**
```python
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
import os

class OptimaAIKnowledge:
    def __init__(self):
        self.vector_db = LanceDb(
            uri="data/optimai_knowledge",
            table_name="company_knowledge", 
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small")
        )
        
        # Загрузка данных компании из папки optimai_data
        self.company_knowledge = TextKnowledgeBase(
            path="optimai_data/",
            vector_db=self.vector_db
        )
        
        # Источники трендов ИИ (российский рынок)
        self.trends_sources = [
            "https://vc.ru/tag/искусственный-интеллект",
            "https://habr.com/ru/hub/artificial_intelligence/",
            "https://www.cnews.ru/news/line/tag/ii"
        ]
    
    async def load_knowledge(self):
        """Загружает базу знаний"""
        await self.company_knowledge.aload(recreate=False)
    
    def search_company_info(self, query: str) -> str:
        """Поиск информации о компании"""
        return self.company_knowledge.search(query)
```

**Инструкция для агента:**
> Создай новый файл `optimai_knowledge.py` с классом OptimaAIKnowledge для работы с базой знаний компании. Используй данные из папки `optimai_data/` и создай папку `data/` для хранения векторной базы.

---

### 📋 **ЗАДАЧА 4: Команда исследователей** (Приоритет 2)

**Контекст для агента:**
```
Цель: Создать мультиагентную команду для сбора и анализа новостей
Новый файл: research_team.py
Зависимости: Agno Teams, Exa, Tavily, ReasoningTools
```

**Требования:**
- Агент поиска новостей (Exa, Tavily)
- Агент анализа трендов (ReasoningTools)
- Агент проверки фактов
- Координатор команды

**Код для реализации:**
```python
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools

class ResearchTeam:
    def __init__(self):
        # Агент поиска новостей
        self.news_searcher = Agent(
            name="News Searcher",
            role="Поиск актуальных новостей в сфере ИИ",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ExaTools(), TavilyTools()],
            instructions=[
                "Ищи самые актуальные новости в сфере ИИ",
                "Фокусируйся на российском рынке ИИ",
                "Обращай внимание на новости о компаниях, обучении ИИ, новых технологиях",
                "Приоритет: OpenAI, Google AI, российские ИИ-компании"
            ]
        )
        
        # Агент анализа трендов
        self.trend_analyzer = Agent(
            name="Trend Analyzer", 
            role="Анализ трендов и популярности тем",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Анализируй популярность и актуальность тем в сфере ИИ",
                "Определяй, какие темы будут интересны аудитории OptimaAI",
                "Учитывай специфику обучения ИИ и промптинга",
                "Оценивай потенциал темы для образовательного контента"
            ]
        )
        
        # Агент проверки фактов
        self.fact_checker = Agent(
            name="Fact Checker",
            role="Проверка достоверности информации",
            model=OpenAIChat(id="gpt-4o-mini"), 
            tools=[ReasoningTools(add_instructions=True), TavilyTools()],
            instructions=[
                "Проверяй достоверность фактов в новостях",
                "Ищи подтверждения из нескольких источников",
                "Отмечай недостоверную или спорную информацию",
                "Оценивай надежность источников"
            ]
        )
        
        # Координатор команды
        self.team = Team(
            name="Research Team",
            mode="coordinate",
            members=[self.news_searcher, self.trend_analyzer, self.fact_checker],
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Координируй работу команды исследователей",
                "Синтезируй результаты всех агентов",
                "Создавай итоговый отчет с проверенными фактами",
                "Оценивай качество и актуальность информации"
            ]
        )
    
    async def research_topic(self, topic: str) -> str:
        """Исследует тему с помощью команды агентов"""
        return self.team.run(f"Исследуй тему: {topic}")
```

**Инструкция для агента:**
> Создай новый файл `research_team.py` с классом ResearchTeam, содержащим команду из трех агентов для исследования новостей. Убедись, что все инструменты правильно импортированы.

---

### 📋 **ЗАДАЧА 5: Редакторская команда** (Приоритет 2)

**Контекст для агента:**
```
Файлы: Результат ЗАДАЧИ 3 (optimai_knowledge.py)
Цель: Создать команду для создания и редактирования контента
Новый файл: editorial_team.py
```

**Требования:**
- Агент создания контента (с базой знаний OptimaAI)
- Агент стилистического редактирования
- Агент проверки качества
- Координатор команды

**Код для реализации:**
```python
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

class EditorialTeam:
    def __init__(self, optimai_knowledge):
        self.knowledge = optimai_knowledge
        
        # Агент создания контента
        self.content_creator = Agent(
            name="Content Creator",
            role="Создание постов для Telegram канала",
            model=OpenAIChat(id="gpt-4o-mini"),
            knowledge=self.knowledge.company_knowledge,
            instructions=[
                "Создавай посты в стиле OptimaAI - дружелюбно и профессионально",
                "Объясняй сложные термины простыми словами",
                "Фокусируйся на практической пользе для обучения ИИ",
                "НЕ используй markdown символы и хэштеги",
                "Длина поста: 200-400 слов",
                "Стиль: как опытный SMM-специалист"
            ]
        )
        
        # Агент стилистического редактирования
        self.style_editor = Agent(
            name="Style Editor",
            role="Редактирование стиля и тона",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Проверяй соответствие стиля OptimaAI",
                "Убеждайся, что тон дружелюбный и доступный",
                "Проверяй, что сложные термины объяснены",
                "Оптимизируй для Telegram аудитории"
            ]
        )
        
        # Агент проверки качества
        self.quality_checker = Agent(
            name="Quality Checker", 
            role="Проверка качества и соответствия требованиям",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Проверяй отсутствие markdown символов",
                "Убеждайся, что нет хэштегов и прямых ссылок",
                "Проверяй длину поста (200-400 слов)",
                "Оценивай качество и читаемость",
                "Проверяй соответствие бренду OptimaAI"
            ]
        )
        
        # Главный редактор (координатор)
        self.team = Team(
            name="Editorial Team",
            mode="coordinate", 
            members=[self.content_creator, self.style_editor, self.quality_checker],
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Координируй создание качественного контента",
                "Обеспечивай соответствие всем требованиям",
                "Создавай финальную версию поста",
                "Гарантируй высокое качество контента"
            ]
        )
    
    async def create_post(self, research_data: str, topic: str) -> str:
        """Создает пост на основе исследовательских данных"""
        prompt = f"""
        Создай пост для Telegram канала OptimaAI на основе этих данных:
        
        Тема: {topic}
        Исследовательские данные: {research_data}
        
        Требования:
        - Стиль OptimaAI (дружелюбный, профессиональный)
        - Без markdown символов и хэштегов
        - 200-400 слов
        - Объяснение сложных терминов
        """
        
        return self.team.run(prompt)
```

**Инструкция для агента:**
> Создай новый файл `editorial_team.py` с классом EditorialTeam. Этот класс должен принимать объект optimai_knowledge из ЗАДАЧИ 3 и использовать его для создания контента.

---

### 📋 **ЗАДАЧА 6: Интеграция в основной бот** (Приоритет 2)

**Контекст для агента:**
```
Файлы: @telegram_bot.py + все созданные модули из предыдущих задач
Цель: Интегрировать новую мультиагентную архитектуру в основной бот
```

**Требования:**
- Импортировать все новые модули
- Обновить класс TelegramNewsBot
- Модифицировать метод generate_news_post
- Обновить команду /news для работы с изображениями
- Добавить память администратора

**Ключевые изменения в telegram_bot.py:**

1. **Добавить импорты:**
```python
from research_team import ResearchTeam
from editorial_team import EditorialTeam
from optimai_knowledge import OptimaAIKnowledge
from image_generator import PostImageGenerator
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
```

2. **Обновить инициализацию TelegramNewsBot:**
```python
class TelegramNewsBot:
    def __init__(self):
        # Существующий код...
        
        # Новые компоненты
        self.knowledge = OptimaAIKnowledge()
        self.research_team = ResearchTeam()
        self.editorial_team = EditorialTeam(self.knowledge)
        self.image_generator = PostImageGenerator(os.getenv('OPENAI_API_KEY'))
        
        # Память администратора
        self.admin_memory = Memory(
            model=OpenAIChat(id="gpt-4o-mini"),
            db=SqliteMemoryDb(table_name="admin_memory", db_file="data/admin.db"),
            user_id="admin"
        )
```

3. **Обновить метод generate_news_post:**
```python
async def generate_news_post(self, topic: str = "latest AI news"):
    """Обновленная генерация поста с мультиагентной архитектурой"""
    try:
        # Шаг 1: Исследование темы
        research_data = await self.research_team.research_topic(topic)
        
        # Шаг 2: Создание поста
        post_content = await self.editorial_team.create_post(research_data, topic)
        
        # Шаг 3: Генерация изображения
        image_url = await self.image_generator.generate_image(post_content)
        
        return {
            'content': post_content,
            'image_url': image_url,
            'topic': topic
        }
        
    except Exception as e:
        logger.error(f"Ошибка генерации поста: {e}")
        return None
```

4. **Обновить команду /news для работы с изображениями:**
```python
# В функции news_command добавить обработку изображений
if post_data.get('image_url'):
    await status_msg.delete()
    await message.answer_photo(
        photo=post_data['image_url'],
        caption=preview_text,
        reply_markup=keyboard
    )
else:
    await status_msg.edit_text(preview_text, reply_markup=keyboard)
```

**Инструкция для агента:**
> Обнови файл `telegram_bot.py`, интегрировав все созданные модули. Добавь импорты, обнови класс TelegramNewsBot, модифицируй методы для работы с новой архитектурой. Убедись, что команда /news работает с изображениями.

---

### 📋 **ЗАДАЧА 7: Дополнительные функции** (Приоритет 3)

**Контекст для агента:**
```
Файлы: Обновленный telegram_bot.py из ЗАДАЧИ 6
Цель: Добавить дедупликацию контента и расширенное логирование
Новый файл: content_deduplication.py
```

**Требования:**
- Система предотвращения дублирования контента
- Расширенное логирование
- Методы для работы с памятью администратора

**Код для content_deduplication.py:**
```python
from agno.storage.sqlite import SqliteStorage
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict

class ContentDeduplicator:
    def __init__(self):
        self.storage = SqliteStorage(
            table_name="published_content",
            db_file="data/content_history.db"
        )
    
    def generate_content_hash(self, content: str) -> str:
        """Генерирует хэш контента для сравнения"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_duplicate(self, content: str, similarity_threshold: float = 0.8) -> bool:
        """Проверяет, является ли контент дубликатом"""
        content_hash = self.generate_content_hash(content)
        
        # Проверка точного совпадения
        recent_posts = self.get_recent_posts(days=30)
        for post in recent_posts:
            if post.get('content_hash') == content_hash:
                return True
        
        return False
    
    def save_published_content(self, content: str, topic: str):
        """Сохраняет опубликованный контент"""
        content_hash = self.generate_content_hash(content)
        
        data = {
            'content_hash': content_hash,
            'content_preview': content[:200],
            'topic': topic,
            'published_at': datetime.now().isoformat()
        }
        
        self.storage.create(data)
    
    def get_recent_posts(self, days: int = 30) -> List[Dict]:
        """Получает недавние посты"""
        cutoff_date = datetime.now() - timedelta(days=days)
        # Реализация зависит от API storage
        return []
```

**Дополнения для telegram_bot.py:**
```python
# Добавить в импорты
from content_deduplication import ContentDeduplicator

# Добавить в __init__ TelegramNewsBot
self.deduplicator = ContentDeduplicator()

# Добавить методы для памяти администратора
async def save_admin_preference(self, preference_type: str, value: str):
    """Сохраняет предпочтения администратора"""
    await self.admin_memory.add(
        f"Предпочтение {preference_type}: {value}",
        user_id="admin"
    )

async def get_admin_context(self) -> str:
    """Получает контекст предпочтений администратора"""
    memories = await self.admin_memory.search("предпочтения стиль", limit=5)
    return "\n".join([m.memory for m in memories])

# Добавить проверку дублирования в generate_news_post
if self.deduplicator.is_duplicate(post_content):
    logger.info("Обнаружен дубликат контента, генерирую альтернативный вариант")
    return await self.generate_news_post(f"{topic} альтернативный подход")

# Расширить логирование
logger.info(f"Research completed for topic: {topic}")
logger.info(f"Content created, length: {len(post_content)}")
logger.info(f"Image generated: {bool(image_url)}")
```

**Инструкция для агента:**
> Создай файл `content_deduplication.py` и добавь функции дедупликации в `telegram_bot.py`. Также добавь методы для работы с памятью администратора и расширенное логирование.

---

## 📦 Обновление зависимостей

**Обновить `requirements.txt`:**
```
agno[openai,anthropic,groq,duckduckgo-search,tavily,exa]
lancedb
pillow
aiogram
python-dotenv
```

## 🔧 Переменные окружения

**Обновить `.env`:**
```env
# Существующие
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=@optimaai_tg

# Новые
TAVILY_API_KEY=your_tavily_api_key
EXA_API_KEY=your_exa_api_key
AGNO_DEBUG=true
```

## 📁 Итоговая структура файлов

```
agno_content_bot/
├── data/                          # Новая папка для данных
│   ├── optimai_knowledge/         # Векторная БД знаний
│   ├── content_history.db         # История контента
│   └── admin.db                   # Память администратора
├── optimai_data/                  # Данные компании (существует)
├── telegram_bot.py               # Основной бот (ЗАДАЧА 6)
├── research_team.py              # ЗАДАЧА 4
├── editorial_team.py             # ЗАДАЧА 5
├── optimai_knowledge.py          # ЗАДАЧА 3
├── content_deduplication.py      # ЗАДАЧА 7
├── image_generator.py            # ЗАДАЧА 2
├── content_formatter.py          # ЗАДАЧА 1
├── post_editor.py                # Существующий (можно обновить)
├── requirements.txt              # Обновить
└── .env                          # Обновить
```

## 🎯 Порядок выполнения задач

1. **ЗАДАЧА 1** → **ЗАДАЧА 2** → **ЗАДАЧА 3** (можно параллельно)
2. **ЗАДАЧА 4** → **ЗАДАЧА 5** (после ЗАДАЧИ 3)
3. **ЗАДАЧА 6** (после всех предыдущих)
4. **ЗАДАЧА 7** (опционально)

## 📞 Инструкции для каждой задачи

Каждая задача должна выполняться отдельно с передачей агенту только:
- Конкретного раздела этого документа
- Необходимых существующих файлов
- Четкой инструкции: "Создай/обнови только этот компонент"

**Пример запроса для ЗАДАЧИ 1:**
```
@PLANNING.md (ЗАДАЧА 1)
@content_formatter.py
@optimai_data/

Выполни ЗАДАЧУ 1: обнови content_formatter.py под требования OptimaAI
``` 