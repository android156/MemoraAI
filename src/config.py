"""
Конфигурация приложения
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    """Класс конфигурации приложения"""
    telegram_token: str
    openai_api_key: str

def load_config() -> Config:
    """
    Загрузка конфигурации из переменных окружения
    """
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN не найден в переменных окружения")
        
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
    
    return Config(
        telegram_token=telegram_token,
        openai_api_key=openai_api_key
    )
