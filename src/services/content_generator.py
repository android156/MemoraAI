"""
Генератор контента для поздравлений
"""
from services.ai_service import AIService
from models.context import Context

class ContentGenerator:
    """Класс для генерации поздравлений и изображений"""

    def __init__(self, ai_service: AIService):
        """Инициализация генератора контента"""
        self.ai_service = ai_service

    async def generate_content(self, context: Context) -> tuple[str, str]:
        """
        Генерация поздравления и изображения

        Returns:
            tuple: (текст_поздравления, url_изображения)
        """
        # Генерация текста поздравления
        greeting_text = await self.ai_service.generate_greeting(context)

        # Генерация изображения
        image_url = await self.ai_service.generate_image(greeting_text)

        return greeting_text, image_url