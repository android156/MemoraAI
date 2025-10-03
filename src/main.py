"""
Основной файл запуска бота
"""
import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.bot.bot import create_bot
from src.config import load_config

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Временно установим уровень DEBUG для отладки
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Установка уровня INFO для конкретных логгеров
logging.getLogger('httpcore.http11').setLevel(logging.INFO)
logging.getLogger('httpcore.connection').setLevel(logging.INFO)
logging.getLogger('openai._base_client').setLevel(logging.INFO)
logging.getLogger('models.context').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

async def main():
    """
    Точка входа в приложение
    """
    try:
        # Загрузка конфигурации
        logger.info("Загрузка конфигурации приложения")
        config = load_config()
        logger.debug("Конфигурация успешно загружена")

        # Создание и запуск бота
        logger.info("Создание экземпляра бота")
        bot, dp = await create_bot(config)

        logger.info("Запуск бота")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {str(e)}", exc_info=True)
        raise
    finally:
        if 'bot' in locals():
            if bot.session:
                logger.info("Закрытие сессии бота")
                await bot.session.close()

if __name__ == '__main__':
    try:
        logger.info("Запуск приложения бота")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.critical(f"Неожиданная ошибка: {str(e)}", exc_info=True)
        sys.exit(1)