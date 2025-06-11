from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent
from optimai_data.content_instructions import instructions

class ContentFormatter:
    def __init__(self):
        self.agent = Agent(
            name="OptimaAI Content Creator",
            model=OpenAIChat(id="gpt-4o"),
            instructions=instructions,
            markdown=False,
        )
    
    def format_news_post(self, raw_news: str) -> str:
        """Форматировать новости в пост для Telegram канала OptimaAI"""
        
        prompt = dedent(f"""
            Преобразуй следующие новостные данные в HTML-пост для Telegram канала OptimaAI.
            
            КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ:
            - СТРОГИЙ ЛИМИТ: максимум 1000 символов включая HTML теги
            - Используй ТОЛЬКО HTML теги: <b>, <i>, <u>, <a href=''>, <code>, <pre>
            - Для переносов строк используй обычные переносы \n, НЕ <br> теги!
            - НЕ используй markdown символы (**, *, #, _, ```)
            - НЕ добавляй хэштеги или эмодзи
            - НЕ включай прямые ссылки
            
            СТРУКТУРА HTML ПОСТА:
            1. <b>Заголовок</b> - краткий и привлекательный
            2. Обычный перенос строки (\n)
            3. Основной текст с ключевой информацией
            4. Перенос строки при необходимости
            5. Практический вывод или совет
            
            СТИЛЬ:
            - Краткость и ясность
            - Дружелюбный тон для AI-канала
            - Фокус на практической пользе
            - Логически завершенный текст
            
            Исходные данные:
            {raw_news}
            
            Создай HTML-пост до 1000 символов, готовый для отправки через Telegram Bot API.
        """)
        
        response = self.agent.run(prompt)
        
        # Получаем HTML-контент
        content = response.content if response.content else "Ошибка форматирования"
        
        # Проверяем длину и обрезаем если необходимо
        if len(content) > 1000:
            # Обрезаем до 980 символов и добавляем многоточие
            content = content[:980] + "..."
        
        # Очистка от неподдерживаемых тегов и символов
        import re
        # Удаляем <br> теги (заменяем на обычные переносы)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<BR\s*/?>', '\n', content)
        
        # Удаляем markdown символы
        content = content.replace('**', '')
        content = content.replace('*', '')
        content = content.replace('_', '')
        content = content.replace('`', '')
        content = content.replace('#', '')
        
        # Удаляем URL-ссылки
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        content = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Очищаем лишние пробелы
        content = re.sub(r'\s+', ' ', content)  # Множественные пробелы в один
        content = content.strip()
        
        # Финальная проверка длины
        if len(content) > 1000:
            content = content[:997] + "..."
            
        return content