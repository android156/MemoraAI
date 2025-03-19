"""
Настройка логирования
"""
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    """
    Настройка логгера с ротацией файлов
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Создание обработчика с ротацией файлов
    handler = RotatingFileHandler(
        'bot.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    
    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger
