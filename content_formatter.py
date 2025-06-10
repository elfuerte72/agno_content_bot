from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent

class ContentFormatter:
    def __init__(self):
        self.agent = Agent(
            name="OptimaAI Content Creator",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
                "Создавай посты в дружелюбном SMM-стиле для Telegram канала OptimaAI",
                "Объясняй сложные технические термины простыми словами", 
                "НЕ используй markdown символы: **, *, #, _, ```",
                "НЕ добавляй хэштеги в конце поста",
                "НЕ включай прямые ссылки на источники",
                "Пиши как опытный SMM-специалист в сфере ИИ",
                "Делай контент понятным для широкой аудитории",
                "Фокусируйся на практической пользе информации для обучения ИИ",
                "Упоминай OptimaAI как экспертов в области обучения ИИ, когда это уместно",
                "Стиль: профессиональный, но доступный и дружелюбный",
                "Длина поста: 200-400 слов",
                "Структура: заголовок, основная информация, практические выводы",
                "Избегай технического жаргона без объяснений",
                "Показывай, как информация поможет в работе с ИИ"
            ],
            markdown=False,
        )
    
    def format_news_post(self, raw_news: str) -> str:
        """Форматировать новости в пост для Telegram канала OptimaAI"""
        
        prompt = dedent(f"""
            Преобразуй следующие новостные данные в пост для Telegram канала OptimaAI.
            
            ВАЖНЫЕ ТРЕБОВАНИЯ:
            - Убери ВСЕ markdown символы (**, *, #, _, ```)
            - НЕ добавляй хэштеги
            - НЕ включай прямые ссылки
            - Объясняй сложные термины простыми словами
            - Пиши в дружелюбном SMM-стиле
            - Фокусируйся на практической пользе для изучения ИИ
            
            СТРУКТУРА ПОСТА:
            1. Привлекательный заголовок (без markdown)
            2. Краткое объяснение сути новости
            3. Почему это важно для тех, кто изучает ИИ
            4. Практические выводы или советы
            
            СТИЛЬ OptimaAI:
            - Профессионально, но доступно
            - Как эксперты в области обучения ИИ
            - Помогаем людям понять сложные технологии
            - Показываем практическую ценность
            
            Исходные данные:
            {raw_news}
            
            Создай пост, который будет интересен и полезен аудитории OptimaAI - людям, которые хотят эффективно использовать искусственный интеллект в своей работе и жизни.
        """)
        
        response = self.agent.run(prompt)
        
        # Дополнительная очистка от markdown символов на случай, если агент их добавил
        content = response.content if response.content else "Ошибка форматирования"
        
        # Удаляем markdown символы
        content = content.replace('**', '')
        content = content.replace('*', '')
        content = content.replace('_', '')
        content = content.replace('`', '')
        content = content.replace('#', '')
        
        # Удаляем хэштеги (строки, начинающиеся с #)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Пропускаем строки, которые являются хэштегами
            if not line.strip().startswith('#') or len(line.strip()) == 1:
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Удаляем URL-ссылки (простая очистка)
        import re
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        content = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Очищаем лишние пробелы и переносы строк
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Убираем множественные переносы
        content = content.strip()
        
        return content