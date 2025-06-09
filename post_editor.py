"""
Модуль для редактирования постов с помощью ИИ
"""

import openai
import asyncio
import logging
from typing import Optional
from textwrap import dedent

logger = logging.getLogger(__name__)

class PostEditor:
    """Класс для редактирования постов с помощью OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Инициализация редактора постов
        
        Args:
            api_key: API ключ OpenAI
            model: Модель для использования (по умолчанию gpt-4o)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
    async def edit_post(self, original_post: str, edit_instructions: str) -> str:
        """
        Редактировать пост согласно инструкциям
        
        Args:
            original_post: Оригинальный текст поста
            edit_instructions: Инструкции по редактированию
            
        Returns:
            Отредактированный пост
            
        Raises:
            Exception: При ошибке редактирования
        """
        try:
            logger.info("Начало редактирования поста с помощью ИИ")
            
            # Создаем системный промпт
            system_prompt = dedent("""
                Вы - эксперт редактор контента для Telegram каналов. 
                
                Ваши задачи:
                1. Внимательно прочитать оригинальный пост
                2. Понять инструкции по редактированию
                3. Применить изменения, сохраняя общий стиль и структуру
                4. Убедиться, что пост остается привлекательным и читаемым
                5. Сохранить эмодзи и форматирование, если не указано иное
                
                Правила:
                - Отвечайте только отредактированным постом
                - Не добавляйте комментарии или объяснения
                - Сохраняйте длину поста подходящей для Telegram (до 4096 символов)
                - Если инструкции неясны, делайте разумные предположения
            """).strip()
            
            # Создаем пользовательский промпт
            user_prompt = dedent(f"""
                Оригинальный пост:
                {original_post}
                
                Инструкции по редактированию:
                {edit_instructions}
                
                Пожалуйста, примените указанные изменения к оригинальному посту.
            """).strip()
            
            # Выполняем запрос к OpenAI в отдельном потоке
            response = await asyncio.to_thread(
                self._make_openai_request,
                system_prompt,
                user_prompt
            )
            
            edited_post = response.choices[0].message.content.strip()
            
            # Проверяем, что ответ не пустой
            if not edited_post:
                raise Exception("Получен пустой ответ от ИИ")
            
            logger.info("Пост успешно отредактирован")
            return edited_post
            
        except Exception as e:
            logger.error(f"Ошибка редактирования поста: {e}")
            raise Exception(f"Не удалось отредактировать пост: {str(e)}")
    
    def _make_openai_request(self, system_prompt: str, user_prompt: str):
        """
        Выполнить запрос к OpenAI API
        
        Args:
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
            
        Returns:
            Ответ от OpenAI API
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
    
    async def suggest_improvements(self, post: str) -> str:
        """
        Предложить улучшения для поста
        
        Args:
            post: Текст поста для анализа
            
        Returns:
            Предложения по улучшению
        """
        try:
            system_prompt = dedent("""
                Вы - эксперт по контент-маркетингу для Telegram каналов.
                Проанализируйте пост и предложите конкретные улучшения.
                
                Фокусируйтесь на:
                - Привлекательности заголовка
                - Структуре и читаемости
                - Использовании эмодзи
                - Длине и формате
                - Вовлеченности аудитории
            """).strip()
            
            user_prompt = f"Проанализируйте этот пост и предложите 3-5 конкретных улучшений:\n\n{post}"
            
            response = await asyncio.to_thread(
                self._make_openai_request,
                system_prompt,
                user_prompt
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка анализа поста: {e}")
            return "Не удалось проанализировать пост"
    
    async def optimize_for_engagement(self, post: str) -> str:
        """
        Оптимизировать пост для максимальной вовлеченности
        
        Args:
            post: Оригинальный пост
            
        Returns:
            Оптимизированный пост
        """
        try:
            system_prompt = dedent("""
                Вы - эксперт по созданию вирусного контента для Telegram.
                Оптимизируйте пост для максимальной вовлеченности аудитории.
                
                Техники:
                - Привлекательные заголовки с эмодзи
                - Структурированная подача информации
                - Призывы к действию
                - Интригующие формулировки
                - Оптимальная длина абзацев
            """).strip()
            
            user_prompt = f"Оптимизируйте этот пост для максимальной вовлеченности:\n\n{post}"
            
            response = await asyncio.to_thread(
                self._make_openai_request,
                system_prompt,
                user_prompt
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации поста: {e}")
            raise Exception(f"Не удалось оптимизировать пост: {str(e)}")