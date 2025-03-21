"""
Сервис для работы с OpenAI API
"""
import json
import logging
from openai import OpenAI, OpenAIError
from models.context import Context

logger = logging.getLogger(__name__)

class AIService:
    """Класс для работы с OpenAI API"""

    def __init__(self, api_key: str):
        """Инициализация клиента OpenAI"""
        logger.info("Инициализация AIService")
        self.client = OpenAI(api_key=api_key)

    async def analyze_context(self, text: str, prev_context=None) -> dict:
        """
        Анализ контекста сообщения и извлечение ключевой информации
        """
        logger.debug(f"Анализ контекста сообщения: {text[:50]}...")
        messages = [
            {
                "role": "system",
                "content": """Проанализируй текст и верни JSON с информацией в следующем формате:
                {
                    "name": "имя человека",
                    "aliases": ["обращение1", "обращение2"],
                    "holiday": "название праздника",
                    "interests": ["интерес1", "интерес2"],
                    "important_detailes": ["уточнение1", "уточнение2"]
                }"""
            },
            
        ]
        if prev_context:
            messages.append({"role": "user", "content": prev_context.get_summary()})
        messages.append({"role": "user", "content": text})
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using standard GPT-4o model
                messages=messages,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            logger.debug(f"Анализ контекста успешно завершен: {result}")
            return result
        except OpenAIError as e:
            logger.error(f"Ошибка OpenAI API: {str(e)}", exc_info=True)
            return {"name": "", "aliases": [], "holiday": "", "interests": [], "important_detailes": []}
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON ответа: {str(e)}", exc_info=True)
            return {"name": "", "holiday": "", "interests": [], "important_detailes": []}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при анализе контекста: {str(e)}", exc_info=True)
            return {"name": "", "aliases": [], "holiday": "", "interests": [], "important_detailes": []}

    async def generate_greeting(self, context: Context) -> str:
        """
        Генерация текста поздравления на основе контекста
        """
        logger.debug("Начало генерации текста поздравления")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Создай уникальное поздравление на основе контекста.
                        Используй теплый, дружелюбный тон и учитывай интересы человека и важные факты."""
                    },
                    {"role": "user", "content": str(context)}
                ],
                max_tokens=500
            )
            greeting_text = response.choices[0].message.content
            logger.debug(f"Поздравление успешно сгенерировано: {greeting_text[:50]}...")
            return greeting_text
        except OpenAIError as e:
            error_msg = f"Ошибка OpenAI API при генерации поздравления: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Неожиданная ошибка при генерации поздравления: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

    async def generate_image(self, context: Context) -> str:
        """
        Генерация изображения для поздравления
        """
        logger.debug("Начало генерации изображения")
        try:
            prompt = f"Праздничная открытка  на {context.holiday} с учетом его интересов {context.interests} и важных фактов {context.important_detailes}"
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
        except OpenAIError as e:
            error_msg = f"Ошибка OpenAI API при генерации изображения: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Неожиданная ошибка при генерации изображения: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)