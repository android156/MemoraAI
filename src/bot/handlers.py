"""
Обработчики команд и сообщений бота
"""
from aiogram import Dispatcher, types
from aiogram.filters import Command
import logging
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

async def handle_message(
    message: types.Message,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Обработчик текстовых сообщений"""
    logger.info(
        f"Получено сообщение от пользователя {message.from_user.id}: {message.text[:50]}..."
    )
    try:
        # Обновление контекста
        context = context_manager.update_context(message.from_user.id, message.text)

        # Отправка резюме контекста
        summary = context.get_summary()
        logger.debug(f"Сформировано резюме контекста: {summary}")
        await message.answer(f"Я запомнил:\n{summary}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
        await message.answer("Произошла ошибка при обработке сообщения. Попробуйте еще раз.")

async def generate_congratulation(
    message: types.Message,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Обработчик команды /congratulation"""
    logger.info(f"Получена команда /congratulation от пользователя {message.from_user.id}")

    context = context_manager.get_context(message.from_user.id)
    if not context:
        logger.warning(f"Контекст не найден для пользователя {message.from_user.id}")
        await message.answer("Сначала расскажите о том, кого хотите поздравить!")
        return

    # Генерация поздравления и изображения
    try:
        logger.debug("Начало генерации поздравления")
        greeting_text, image_url = await content_generator.generate_content(context)
        logger.debug(f"Поздравление сгенерировано, URL изображения: {image_url}")

        # Отправка результата
        await message.answer_photo(
            photo=image_url,
            caption=greeting_text[:1024]  # Ограничение длины caption
        )
        logger.info(f"Поздравление успешно отправлено пользователю {message.from_user.id}")
    except Exception as e:
        error_msg = f"Произошла ошибка при генерации поздравления: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await message.answer(error_msg)

def register_handlers(
    dp: Dispatcher,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Регистрация обработчиков команд и сообщений"""
    logger.info("Регистрация обработчиков команд бота")
    dp.message.register(start_command, Command(commands=["start"]))
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(
        generate_congratulation,
        Command(commands=["congratulation"])
    )
    dp.message.register(
        lambda msg: handle_message(msg, context_manager, content_generator)
    )