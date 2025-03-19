"""
Инициализация и настройка бота
"""
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from config import Config
from bot.handlers import handle_message, start_command, help_command
from services.ai_service import AIService
from services.context_manager import ContextManager
from services.content_generator import ContentGenerator

logger = logging.getLogger(__name__)

async def create_bot(config: Config) -> tuple[Bot, Dispatcher]:
    """
    Создание и настройка экземпляра бота

    Returns:
        tuple[Bot, Dispatcher]: Кортеж из объектов бота и диспетчера
    """
    logger.info("Начало инициализации бота")

    # Создание бота с правильными настройками HTML-разметки
    bot = Bot(
        token=config.telegram_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    logger.debug("Бот создан с настройками HTML-разметки")

    # Создание диспетчера
    dp = Dispatcher()
    logger.debug("Диспетчер создан")

    # Инициализация сервисов
    try:
        logger.info("Инициализация сервисов")
        ai_service = AIService(config.openai_api_key)
        context_manager = ContextManager(ai_service)
        content_generator = ContentGenerator(ai_service)
        logger.debug("Сервисы успешно инициализированы")
    except Exception as e:
        logger.error(f"Ошибка при инициализации сервисов: {str(e)}", exc_info=True)
        raise

    # Регистрация обработчиков
    try:
        # Регистрация обработчиков
        dp.message.register(start_command, Command("start"))
        dp.message.register(help_command, Command("help"))

        # Регистрация обработчика с сервисами
        dp.message.register(
            handle_message,
            lambda msg: not msg.text.startswith('/')
        )

        # Внедрение зависимостей для обработчика
        async def dependencies_middleware(handler, event, data):
            # Get handler's parameters
            from inspect import signature
            handler_params = signature(handler.callback).parameters
            
            # Only pass dependencies that the handler expects
            filtered_data = {}
            if 'context_manager' in handler_params:
                filtered_data['context_manager'] = context_manager
            if 'content_generator' in handler_params:
                filtered_data['content_generator'] = content_generator
                
            return await handler(event, **filtered_data)

        dp.message.middleware.register(dependencies_middleware)

        logger.debug("Обработчики команд зарегистрированы")
    except Exception as e:
        logger.error(f"Ошибка при регистрации обработчиков: {str(e)}", exc_info=True)
        raise

    # Установка команд бота с использованием правильного формата BotCommand
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Перезагрузить бота"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="congratulation", description="Создать поздравление")
        ])
        logger.debug("Команды бота установлены")
    except Exception as e:
        logger.error(f"Ошибка при установке команд бота: {str(e)}", exc_info=True)
        raise

    logger.info("Инициализация бота завершена успешно")
    return bot, dp