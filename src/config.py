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
    openai_proxy_enabled: bool
    openai_proxy_host: str | None
    openai_proxy_port: int | None
    openai_proxy_username: str | None
    openai_proxy_password: str | None

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
    
    # Загрузка параметров прокси
    proxy_enabled = os.getenv("OPENAI_PROXY_ENABLED", "false").lower() == "true"
    proxy_host = os.getenv("OPENAI_PROXY_HOST")
    proxy_port = int(os.getenv("OPENAI_PROXY_PORT")) if os.getenv("OPENAI_PROXY_PORT") else None
    proxy_username = os.getenv("OPENAI_PROXY_USERNAME")
    proxy_password = os.getenv("OPENAI_PROXY_PASSWORD")
    
    return Config(
        telegram_token=telegram_token,
        openai_api_key=openai_api_key,
        openai_proxy_enabled=proxy_enabled,
        openai_proxy_host=proxy_host,
        openai_proxy_port=proxy_port,
        openai_proxy_username=proxy_username,
        openai_proxy_password=proxy_password
    )
