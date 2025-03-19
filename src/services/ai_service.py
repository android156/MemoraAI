"""
Сервис для работы с OpenAI API
"""
from openai import OpenAI
from models.context import Context

class AIService:
    """Класс для работы с OpenAI API"""

    def __init__(self, api_key: str):
        """Инициализация клиента OpenAI"""
        self.client = OpenAI(api_key=api_key)

    async def analyze_context(self, text: str) -> dict:
        """
        Анализ контекста сообщения и извлечение ключевой информации
        """
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
        return response.choices[0].message.content

    async def generate_greeting(self, context: Context) -> str:
        """
        Генерация текста поздравления на основе контекста
        """
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
        return response.choices[0].message.content

    async def generate_image(self, context: Context) -> str:
        """
        Генерация изображения для поздравления
        """
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=f"Праздничная открытка для {context.name} на {context.holiday}",
            n=1,
            size="1024x1024"
        )
        return response.data[0].url