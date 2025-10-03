"""
Модель контекста диалога
"""
from dataclasses import dataclass, field
from typing import List
import logging

logger = logging.getLogger(__name__)

@dataclass
class Context:
    """Класс для хранения контекста диалога"""
    summory: str = ""
    messages: List[str] = field(default_factory=list)

    def add_message(self, message: str):
        """
        Добавление нового сообщения в контекст
        Args:
            message: текст сообщения
        """
        if not message:
            logger.warning("Попытка добавить пустое сообщение в контекст")
            return

        logger.debug(f"Добавление сообщения в контекст: {message[:50]}...")
        self.messages.append(message)

    def update_summory(self, updated_summory):
        """
        Обновление usummory
        
        Args:
            updated_summory: новый контекст
        """
        self.summory = updated_summory
        
    

    def get_summory(self) -> str:
        return self.summory

    def __str__(self) -> str:
        """Строковое представление контекста"""
        return self.summory

    