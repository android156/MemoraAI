"""
Менеджер контекста диалога
"""
from typing import Dict, Optional
import logging
from models.context import Context
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class ContextManager:
    """Класс для управления контекстом диалога с пользователем"""

    def __init__(self, ai_service: AIService):
        """
        Инициализация хранилища контекстов
        Args:
            ai_service: Сервис для работы с ИИ
        """
        logger.info("Инициализация ContextManager")
        self._contexts: Dict[int, Context] = {}
        self.ai_service = ai_service

    def get_context(self, user_id: int) -> Optional[Context]:
        """
        Получение контекста для пользователя
        """
        return self._contexts.get(user_id)

    async def update_context(self, user_id: int, message: str) -> Context:
        """
        Обновление контекста на основе нового сообщения

        Args:
            user_id: ID пользователя
            message: Текст сообщения

        Returns:
            Context: Обновленный контекст
        """
        logger.debug(f"Обновление контекста для пользователя {user_id}")

        if user_id not in self._contexts:
            logger.debug(f"Создание нового контекста для пользователя {user_id}")
            self._contexts[user_id] = Context()

        context = self._contexts[user_id]
        
        # Анализ сообщения с помощью ИИ
        try:
            analyzed_data = await self.ai_service.analyze_context(message, context)
            logger.debug(f"Результат анализа контекста: {analyzed_data}")
            
            
            # Обновление контекста с анализом
            context.update_values(analyzed_data.items())
            

            # Добавление исходного сообщения в историю
            context.add_message(message)

            logger.debug(f"Контекст успешно обновлен: {context}")
            return context

        except Exception as e:
            logger.error(f"Ошибка при анализе контекста: {str(e)}", exc_info=True)
            # В случае ошибки анализа, просто сохраняем сообщение
            context.add_message(message)
            return context

    def clear_context(self, user_id: int):
        """
        Очистка контекста пользователя
        """
        if user_id in self._contexts:
            logger.debug(f"Очистка контекста для пользователя {user_id}")
            del self._contexts[user_id]