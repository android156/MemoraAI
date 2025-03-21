"""
Обработчики команд и сообщений бота
"""
import asyncio
from aiogram import types, Dispatcher
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


async def clear_command(message: types.Message):
    """Обработчик команды /clear"""
    user.id = message.from_user.id
    logger.info(f"Получена команда /clear от пользователя {user.id}")
    context_manager = ContextManager()
    context_manager.clear_context(user.id)
    await message.answer("Контекст очищен", reply_markup=get_main_keyboard())


async def handle_message(
    message: types.Message,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Обработчик текстовых сообщений"""
    try:
        logger.info(
            f"[DEBUG] ВХОДЯЩЕЕ СООБЩЕНИЕ - От: {message.from_user.id}, "
            f"Текст: {message.text[:50]}..., "
            f"Тип: {type(message)}"
        )

        # Нормализация текста сообщения
        message_text = message.text.strip() if message.text else ""
        logger.debug(f"Нормализованный текст сообщения: {message_text}")

        # Определяем команды кнопок
        BUTTON_COMMANDS = {
            "✨ Создать поздравление": generate_congratulation,
            "❓ Помощь": help_command,
            "❌ Очистить контекст": clear_command,
            "🔄 Перезагрузить бота": start_command
        }

        # Если это команда кнопки, выполняем её без анализа контекста
        if message_text in BUTTON_COMMANDS:
            logger.debug(f"Обработка команды кнопки: {message_text}")
            command_handler = BUTTON_COMMANDS[message_text]
            if command_handler == generate_congratulation:
                await command_handler(message, context_manager, content_generator)
            else:
                await command_handler(message)
            return

        # Проверка на пустое сообщение
        if not message_text:
            logger.warning("Получено пустое сообщение")
            await message.answer("Пожалуйста, отправьте текстовое сообщение")
            return

        # Отправка сообщения о начале обработки
        processing_msg = await message.answer("Анализирую сообщение...")

        try:
            # Обновление контекста
            context = await context_manager.update_context(message.from_user.id, message_text)
            logger.debug(f"Контекст обновлен для пользователя {message.from_user.id}")
            logger.debug(f"История сообщений: {context.messages}")

            # Удаление сообщения о процессе
            await processing_msg.delete()

            # Отправка резюме контекста
            summary = context.get_summary()
            logger.debug(f"Сформировано резюме контекста: {summary}")
            await message.answer(f"Я запомнил:\n{summary}")

        except Exception as e:
            logger.error(f"Ошибка при обработке контекста: {str(e)}", exc_info=True)
            await processing_msg.edit_text("Произошла ошибка при анализе сообщения. Попробуйте еще раз.")

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

    try:
        context = context_manager.get_context(message.from_user.id)
        if not context or not context.messages:
            logger.warning(f"Контекст не найден для пользователя {message.from_user.id}")
            await message.answer("Сначала расскажите о том, кого хотите поздравить!")
            return

        # Отправка сообщения о начале генерации
        processing_msg = await message.answer("Генерирую поздравление...")

        try:
            # Генерация поздравления и изображения
            logger.debug("Начало генерации поздравления")
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

            # Очищаем контекст после успешной генерации
            context_manager.clear_context(message.from_user.id)
            logger.debug(f"Контекст очищен для пользователя {message.from_user.id}")

        except Exception as e:
            error_msg = f"Произошла ошибка при генерации поздравления: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await processing_msg.edit_text(error_msg)

    except Exception as e:
        error_msg = f"Произошла ошибка при обработке команды: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await message.answer(error_msg)

def register_handlers(
    dp: Dispatcher,
    context_manager: ContextManager,
    content_generator: ContentGenerator
):
    """Регистрация обработчиков команд и сообщений"""
    logger.info("Регистрация обработчиков команд бота")
    dp.message.register(start_command, Command(commands=["/start"]))
    dp.message.register(help_command, Command(commands=["/help"]))
    dp.message.register(clear_command, Command(commands=["/clear"]))
    dp.message.register(
        lambda message: generate_congratulation(message, context_manager, content_generator),
        Command(commands=["congratulation"])
    )
    # Регистрируем обработчик для всех остальных сообщений
    dp.message.register(
        lambda message: asyncio.get_event_loop().create_task(handle_message(message, context_manager, content_generator))
    )