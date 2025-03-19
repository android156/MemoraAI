"""
Менеджер контекста диалога
"""
from typing import Dict, Optional
from models.context import Context

class ContextManager:
    """Класс для управления контекстом диалога с пользователем"""

    def __init__(self):
        """Инициализация хранилища контекстов"""
        self._contexts: Dict[int, Context] = {}

    def get_context(self, user_id: int) -> Optional[Context]:
        """
        Получение контекста для пользователя
        """
        return self._contexts.get(user_id)

    def update_context(self, user_id: int, message: str) -> Context:
        """
        Обновление контекста на основе нового сообщения
        """
        if user_id not in self._contexts:
            self._contexts[user_id] = Context()

        context = self._contexts[user_id]
        context.add_message(message)
        return context

    def clear_context(self, user_id: int):
        """
        Очистка контекста пользователя
        """
        if user_id in self._contexts:
            del self._contexts[user_id]