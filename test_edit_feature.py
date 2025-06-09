#!/usr/bin/env python3
"""
Тестирование функции редактирования постов
"""

import asyncio
import os
from dotenv import load_dotenv
from post_editor import PostEditor

# Загрузка переменных окружения
load_dotenv()

async def test_post_editor():
    """Тестирование PostEditor класса"""
    
    # Проверка API ключа
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY не найден в переменных окружения")
        return
    
    # Инициализация редактора
    editor = PostEditor(api_key=api_key)
    
    # Тестовый пост
    original_post = """
🔥 **Последние новости технологий**

📊 **Краткое резюме:**
Сегодня в мире технологий произошло несколько важных событий, включая новые разработки в области ИИ и криптовалют.

📰 **Основные новости:**
• OpenAI представила новую модель GPT-5
• Bitcoin достиг нового максимума
• Apple анонсировала новый iPhone
• Tesla запустила новую модель автомобиля

🔍 **Ключевые инсайты:**
Рынок технологий продолжает активно развиваться, особенно в сфере искусственного интеллекта.

#технологии #новости #ИИ #криптовалюты
"""

    print("🧪 Тестирование функции редактирования постов\n")
    print("📝 Оригинальный пост:")
    print(original_post)
    print("\n" + "="*50 + "\n")
    
    # Тест 1: Сделать короче
    print("🎯 Тест 1: Сделать короче")
    try:
        shorter_post = await editor.edit_post(
            original_post, 
            "Сделай пост короче, убери лишние детали, оставь только самое важное"
        )
        print("✅ Результат:")
        print(shorter_post)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 2: Добавить деталей
    print("📝 Тест 2: Добавить деталей")
    try:
        detailed_post = await editor.edit_post(
            original_post, 
            "Добавь больше деталей и подробностей, расширь информацию"
        )
        print("✅ Результат:")
        print(detailed_post)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 3: Более привлекательно
    print("🔥 Тест 3: Более привлекательно")
    try:
        engaging_post = await editor.edit_post(
            original_post, 
            "Сделай пост более привлекательным и интересным, улучши заголовок"
        )
        print("✅ Результат:")
        print(engaging_post)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 4: Добавить эмодзи
    print("📊 Тест 4: Добавить эмодзи")
    try:
        emoji_post = await editor.edit_post(
            original_post, 
            "Добавь больше подходящих эмодзи для лучшего визуального восприятия"
        )
        print("✅ Результат:")
        print(emoji_post)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 5: Пользовательские инструкции
    print("✍️ Тест 5: Пользовательские инструкции")
    try:
        custom_post = await editor.edit_post(
            original_post, 
            "Убери информацию о Tesla и Apple, сосредоточься только на ИИ и криптовалютах"
        )
        print("✅ Результат:")
        print(custom_post)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 6: Предложения по улучшению
    print("💡 Тест 6: Предложения по улучшению")
    try:
        suggestions = await editor.suggest_improvements(original_post)
        print("✅ Предложения:")
        print(suggestions)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Тест 7: Оптимизация для вовлеченности
    print("🚀 Тест 7: Оптимизация для вовлеченности")
    try:
        optimized_post = await editor.optimize_for_engagement(original_post)
        print("✅ Результат:")
        print(optimized_post)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n🎉 Тестирование завершено!")

def test_keyboard_functions():
    """Тестирование функций клавиатур"""
    from telegram_bot import create_approval_keyboard, create_quick_edit_keyboard
    
    print("⌨️ Тестирование клавиатур")
    
    test_post_id = "test123"
    
    # Тест клавиатуры подтверждения
    approval_kb = create_approval_keyboard(test_post_id)
    print(f"✅ Клавиатура подтверждения создана: {len(approval_kb.inline_keyboard)} рядов")
    
    # Тест клавиатуры быстрого редактирования
    quick_edit_kb = create_quick_edit_keyboard(test_post_id)
    print(f"✅ Клавиатура быстрого редактирования создана: {len(quick_edit_kb.inline_keyboard)} рядов")
    
    # Проверка callback_data
    for row in approval_kb.inline_keyboard:
        for button in row:
            print(f"  - Кнопка: {button.text} -> {button.callback_data}")
    
    print()
    for row in quick_edit_kb.inline_keyboard:
        for button in row:
            print(f"  - Кнопка: {button.text} -> {button.callback_data}")

async def test_error_handling():
    """Тестирование обработки ошибок"""
    print("🛠 Тестирование обработки ошибок")
    
    # Тест с неверным API ключом
    try:
        editor = PostEditor(api_key="invalid_key")
        await editor.edit_post("test", "test")
    except Exception as e:
        print(f"✅ Ошибка корректно обработана: {type(e).__name__}")
    
    # Тест с пустыми данными
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        try:
            editor = PostEditor(api_key=api_key)
            await editor.edit_post("", "")
        except Exception as e:
            print(f"✅ Ошибка пустых данных обработана: {type(e).__name__}")

def main():
    """Основная функция тестирования"""
    print("🧪 Запуск тестов функции редактирования\n")
    
    # Тест клавиатур (синхронный)
    test_keyboard_functions()
    print()
    
    # Асинхронные тесты
    asyncio.run(test_post_editor())
    print()
    asyncio.run(test_error_handling())
    
    print("\n✅ Все тесты завершены!")

if __name__ == "__main__":
    main()