"""
Сервис для работы с OpenAI API
"""
import logging
from openai import OpenAI
from models.context import Context

logger = logging.getLogger(__name__)

class AIService:
    """Класс для работы с OpenAI API"""

    def __init__(self, api_key: str):
        """Инициализация клиента OpenAI"""
        logger.info("Инициализация AIService")
        self.client = OpenAI(api_key=api_key)

    async def analyze_context(self, text: str) -> dict:
        """
        Анализ контекста сообщения и извлечение ключевой информации
        """
        logger.debug(f"Анализ контекста сообщения: {text[:50]}...")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": "Проанализируй текст и выдели ключевую информацию о человеке и празднике"
                    },
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            logger.debug("Анализ контекста успешно завершен")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка при анализе контекста: {str(e)}", exc_info=True)
            raise

    async def generate_greeting(self, context: Context) -> str:
        """
        Генерация текста поздравления на основе контекста
        """
        logger.debug("Начало генерации текста поздравления")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Создай уникальное поздравление на основе контекста"
                    },
                    {"role": "user", "content": str(context)}
                ],
                max_tokens=500
            )
            greeting_text = response.choices[0].message.content
            logger.debug(f"Поздравление успешно сгенерировано: {greeting_text[:50]}...")
            return greeting_text
        except Exception as e:
            logger.error(f"Ошибка при генерации поздравления: {str(e)}", exc_info=True)
            raise

    async def generate_image(self, context: Context) -> str:
        """
        Генерация изображения для поздравления
        """
        logger.debug("Начало генерации изображения")
        try:
            prompt = f"Праздничная открытка для {context.name} на {context.holiday}"
            logger.debug(f"Промпт для генерации изображения: {prompt}")

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            logger.debug(f"Изображение успешно сгенерировано: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Ошибка при генерации изображения: {str(e)}", exc_info=True)
            raise