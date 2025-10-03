"""
Конфигурация приложения
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Константы для настроек прокси (несекретные данные)
DEFAULT_PROXY_ENABLED = True  # Включить/выключить прокси
DEFAULT_PROXY_HOST = "185.89.41.214"  # Адрес прокси-сервера (например, "proxy.example.com")
DEFAULT_PROXY_PORT = 8000  # Порт прокси-сервера (например, 8080)


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
    # Используем константы по умолчанию для несекретных настроек
    proxy_enabled_str = os.getenv("OPENAI_PROXY_ENABLED",
                                  str(DEFAULT_PROXY_ENABLED)).lower()
    proxy_enabled = proxy_enabled_str == "true"
    proxy_host = os.getenv("OPENAI_PROXY_HOST", DEFAULT_PROXY_HOST)
    proxy_port = int(os.getenv("OPENAI_PROXY_PORT")) if os.getenv(
        "OPENAI_PROXY_PORT") else DEFAULT_PROXY_PORT

    # Секретные данные загружаются только из переменных окружения
    proxy_username = os.getenv("OPENAI_PROXY_USERNAME")
    proxy_password = os.getenv("OPENAI_PROXY_PASSWORD")

    return Config(telegram_token=telegram_token,
                  openai_api_key=openai_api_key,
                  openai_proxy_enabled=proxy_enabled,
                  openai_proxy_host=proxy_host,
                  openai_proxy_port=proxy_port,
                  openai_proxy_username=proxy_username,
                  openai_proxy_password=proxy_password)
