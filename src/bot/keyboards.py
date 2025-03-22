"""
Клавиатуры бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создание основной клавиатуры бота
    """
    keyboard = [
        [
            KeyboardButton(text="✨ Создать поздравление"),
            KeyboardButton(text="❓ Помощь")
        ],
        [
            KeyboardButton(text="❌ Очистить контекст"), 
            KeyboardButton(text="🔄 Перезагрузить")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Расскажите о человеке..."
    )