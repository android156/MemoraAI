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
    name: str = ""
    aliases: List[str] = field(default_factory=list)
    holiday: str = ""
    interests: List[str] = field(default_factory=list)
    important_detailes: List[str] = field(default_factory=list)
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

    def get_summary(self) -> str:
        """
        Формирование резюме контекста

        Returns:
            str: форматированное резюме контекста
        """
        logger.debug("Формирование резюме контекста")
        summary = []

        if self.name:
            summary.append(f"Поздравляем: **{self.name}**")
            logger.debug(f"Добавлено имя: {self.name}")

        if self.aliases:
            summary.append("Обращения:")
            for alias in self.aliases:
                summary.append(f"- **{alias}**")
            logger.debug(f"Добавлены обращения: {', '.join(self.interests)}")
        

        if self.holiday:
            summary.append(f"Праздник: **{self.holiday}**")
            logger.debug(f"Добавлен праздник: {self.holiday}")

        if self.interests:
            summary.append("Интересы:")
            for interest in self.interests:
                summary.append(f"- **{interest}**")
            logger.debug(f"Добавлены интересы: {', '.join(self.interests)}")

        if self.important_detailes:
            summary.append("Важные уточнения:")
            for detail in self.important_detailes:
                summary.append(f"- **{detail}**")
            logger.debug(f"Добавлены важные уточнения: {', '.join(self.important_detailes)}")

        result = "\n".join(summary) if summary else "Контекст пока пуст"
        logger.debug(f"Сформировано резюме: {result}")
        return result

    def __str__(self) -> str:
        """Строковое представление контекста"""
        return self.get_summary()

    