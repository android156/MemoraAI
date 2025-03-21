"""
Обработчики команд и сообщений бота
"""
import logging
from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from services.context_manager import ContextManager
from services.content_generator import ContentGenerator
from bot.keyboards import get_main_keyboard
from models.messages import WELCOME_MESSAGE, HELP_MESSAGE

logger = logging.getLogger(__name__)

async def start_command(message: types.Message):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    await message.answer(
        WELCOME_MESSAGE.format(telegram_username=message.from_user.first_name),
        reply_markup=get_main_keyboard()
    )

async def help_command(message: types.Message):
    """Обработчик команды /help"""
    logger.info(f"Получена команда /help от пользователя {message.from_user.id}")
    await message.answer(HELP_MESSAGE, reply_markup=get_main_keyboard())

async def clear_command(message: types.Message):
    """Обработчик команды /clear"""
    user_id = message.from_user.id
    logger.info(f"Получена команда /clear от пользователя {user_id}")
    context_manager = ContextManager()
    context_manager.clear_context(user_id)
    await message.answer("Контекст очищен", reply_markup=get_main_keyboard())

async def generate_congratulation(
    message: types.Message,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Обработчик генерации поздравления"""
    try:
        processing_msg = await message.answer("⏳ Генерирую поздравление...")

        # Получаем контекст для пользователя
        context = context_manager.get_context(message.from_user.id)
        logger.debug(f"Получен контекст для генерации поздравления")

        # Генерация поздравления
        greeting_text, image_url = await content_generator.generate_content(context)
        logger.debug(f"Поздравление сгенерировано, URL изображения: {image_url}")

        # Удаление сообщения о процессе
        await processing_msg.delete()

        # Отправка результата
        await message.answer_photo(
            photo=image_url,
            caption=greeting_text[:1024]  # Ограничение длины caption
        )
        logger.info(f"Поздравление успешно отправлено пользователю {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при генерации поздравления: {str(e)}", exc_info=True)
        await message.answer(
            "Произошла ошибка при генерации поздравления. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )

async def handle_message(
    message: types.Message,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Обработчик текстовых сообщений"""
    try:
        logger.info(
            f"Входящее сообщение - От: {message.from_user.id}, "
            f"Текст: {message.text[:50] if message.text else 'None'}..."
        )

        message_text = message.text.strip() if message.text else ""

        # Определяем команды кнопок
        button_commands = {
            "✨ Создать поздравление": generate_congratulation,
            "❓ Помощь": help_command,
            "❌ Очистить контекст": clear_command,
            "🔄 Перезагрузить бота": start_command
        }

        # Проверяем, является ли сообщение командой кнопки
        if message_text in button_commands:
            handler = button_commands[message_text]
            if handler == generate_congratulation:
                await handler(message, context_manager, content_generator)
            else:
                await handler(message)
            return

        # Если это не команда кнопки, сохраняем сообщение в контекст
        context_manager.add_to_context(message.from_user.id, message_text)
        await message.answer(
            "Я запомнил эту информацию. Что-нибудь ещё?",
            reply_markup=get_main_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
        await message.answer(
            "Произошла ошибка при обработке сообщения. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )

def register_handlers(dp: Dispatcher, context_manager: ContextManager, content_generator: ContentGenerator):
    """Регистрация всех обработчиков"""
    logger.info("Регистрация обработчиков команд бота")

    # Регистрация команд
    dp.message.register(start_command, Command(commands=["start"]))
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(clear_command, Command(commands=["clear"]))

    # Создаем замыкание для передачи дополнительных параметров
    async def message_handler(message: types.Message):
        await handle_message(message, context_manager, content_generator)

    # Регистрируем обработчик для всех остальных сообщений
    dp.message.register(message_handler)