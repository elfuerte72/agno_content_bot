from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent

class ContentFormatter:
    def __init__(self):
        self.agent = Agent(
            name="Content Formatter",
            model=OpenAIChat(id="gpt-4o"),
            instructions=dedent("""
                Вы - эксперт по созданию привлекательного контента для Telegram каналов! ✨
                
                Ваши задачи:
                1. Преобразовать сырые новостные данные в структурированный пост
                2. Создать привлекательный заголовок с эмодзи
                3. Организовать информацию в легко читаемом формате
                4. Добавить релевантные хештеги
                5. Обеспечить оптимальную длину для Telegram (до 4096 символов)
                
                Структура поста:
                - 🔥 Привлекательный заголовок
                - 📊 Краткое резюме (2-3 предложения)
                - 📰 Основные новости (маркированный список)
                - 🔍 Ключевые инсайты
                - #хештеги #новости #тренды
                
                Стиль:
                - Используйте эмодзи для визуального разделения
                - Делайте текст сканируемым
                - Выделяйте важную информацию
                - Поддерживайте профессиональный, но доступный тон
            """),
            markdown=True,
        )
    
    def format_news_post(self, raw_news: str) -> str:
        """Форматировать новости в пост для Telegram"""
        response = self.agent.run(
            f"Преобразуйте следующие новостные данные в привлекательный "
            f"пост для Telegram канала:\n\n{raw_news}"
        )
        return response.content if response.content else "Ошибка форматирования"