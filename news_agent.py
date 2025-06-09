from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.tavily import TavilyTools
from agno.tools.exa import ExaTools
from textwrap import dedent
import json
from typing import Dict, Any

class NewsAgent:
    def __init__(self):
        self.agent = Agent(
            name="News Researcher",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                DuckDuckGoTools(),
                TavilyTools(),
                ExaTools()
            ],
            instructions=dedent("""
                Вы - опытный новостной аналитик и исследователь! 📰
                
                Ваши задачи:
                1. Найти самые актуальные и важные новости за последние 24 часа
                2. Использовать все доступные источники (DuckDuckGo, Tavily, Exa)
                3. Проверить информацию из нескольких источников
                4. Сосредоточиться на значимых событиях и трендах
                
                Стиль подачи:
                - Представляйте информацию в ясном, журналистском стиле
                - Используйте маркированные списки для ключевых моментов
                - Включайте релевантные цитаты когда возможно
                - Указывайте дату и время для каждой новости
                - Выделяйте тренды и настроения рынка
                - Завершайте кратким анализом общей картины
            """),
            show_tool_calls=True,
            markdown=True,
        )
    
    def get_latest_news(self, topic: str = "latest news") -> str:
        """Получить последние новости по заданной теме"""
        response = self.agent.run(
            f"Найдите и проанализируйте последние новости по теме: {topic}. "
            f"Используйте все доступные инструменты поиска для получения "
            f"наиболее актуальной информации."
        )
        return response.content if response.content else "Не удалось получить новости"