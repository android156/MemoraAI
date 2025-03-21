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

async def clear_command(message: types.Message, context_manager: ContextManager):
    """Обработчик команды /clear"""
    user_id = message.from_user.id
    logger.info(f"Получена команда /clear от пользователя {user_id}")
    context_manager.clear_context(user_id)
    await message.answer(
        "Контекст очищен. Можете начать новый диалог.",
        reply_markup=get_main_keyboard()
    )

async def generate_congratulation(
    message: types.Message,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Обработчик генерации поздравления"""
    try:
        user_id = message.from_user.id
        logger.info(f"Генерация поздравления для пользователя {user_id}")

        context = context_manager.get_context(user_id)
        if not context or not context.messages:
            await message.answer(
                "Пожалуйста, сначала расскажите о человеке, которого хотите поздравить.",
                reply_markup=get_main_keyboard()
            )
            return

        await message.answer("Генерирую поздравление...")
        greeting = await content_generator.generate_congratulation(context)

        await message.answer(
            greeting,
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Поздравление успешно отправлено пользователю {user_id}")

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

        # Если сообщение пустое, игнорируем его
        if not message.text:
            return

        message_text = message.text.strip()
        user_id = message.from_user.id

        # Сохраняем сообщение в контекст
        await context_manager.update_context(user_id, message_text)
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
    """Регистрация обработчиков команд бота"""
    logger.info("Регистрация обработчиков команд бота")

    # Регистрация команды help и кнопки помощи
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(help_command, F.text == "❓ Помощь")

    # Регистрация команды start и кнопки перезагрузки
    dp.message.register(start_command, Command(commands=["start"]))
    dp.message.register(start_command, F.text == "🔄 Перезагрузить")

    # Создаем асинхронную функцию для очистки контекста
    async def clear_handler(message: types.Message):
        await clear_command(message, context_manager)

    # Регистрация команды clear и кнопки очистки
    dp.message.register(clear_handler, Command(commands=["clear"]))
    dp.message.register(clear_handler, F.text == "❌ Очистить контекст")

    # Создаем асинхронный обработчик для генерации поздравления
    async def generate_handler(message: types.Message):
        await generate_congratulation(message, context_manager, content_generator)

    # Регистрация генерации поздравления
    dp.message.register(generate_handler, F.text == "✨ Создать поздравление")

    # Регистрация общего обработчика сообщений
    async def message_handler(message: types.Message):
        await handle_message(message, context_manager, content_generator)

    # Регистрируем общий обработчик последним
    dp.message.register(message_handler)
    

    # Общий обработчик для остальных сообщений
    dp.message.register(
        lambda message: handle_message(message, context_manager, content_generator),
        flags={'allow_in_transaction': True}
    )