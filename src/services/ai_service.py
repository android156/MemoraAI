"""
Сервис для работы с OpenAI API
"""
import json
import logging
import httpx
from openai import OpenAI, OpenAIError
from models.context import Context

logger = logging.getLogger(__name__)

class AIService:
    """Класс для работы с OpenAI API"""

    def __init__(
        self, 
        api_key: str,
        proxy_enabled: bool = False,
        proxy_host: str | None = None,
        proxy_port: int | None = None,
        proxy_username: str | None = None,
        proxy_password: str | None = None
    ):
        """Инициализация клиента OpenAI с поддержкой HTTPS-прокси"""
        logger.info("Инициализация AIService")
        
        # Настройка прокси, если включен
        if proxy_enabled and proxy_host and proxy_port:
            # Формирование URL прокси с авторизацией
            if proxy_username and proxy_password:
                proxy_url = f"https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                logger.info(f"OpenAI подключение через HTTPS прокси: {proxy_host}:{proxy_port} (с авторизацией)")
            else:
                proxy_url = f"https://{proxy_host}:{proxy_port}"
                logger.info(f"OpenAI подключение через HTTPS прокси: {proxy_host}:{proxy_port}")
            
            # Создание HTTP-клиента с прокси
            http_client = httpx.Client(
                proxy=proxy_url
            )
            self.client = OpenAI(api_key=api_key, http_client=http_client)
        else:
            logger.info("OpenAI подключение напрямую (без прокси)")
            self.client = OpenAI(api_key=api_key)

    async def analyze_context(self, text: str, prev_context=None) -> str:
        """
        Анализ контекста сообщения и извлечение ключевой информации
        """
        logger.debug(f"Анализ контекста сообщения: {text[:50]}...")
        messages = [
            {
                "role": "system",
                "content": """Ты — помощник чат-бота в Telegram, который помогает пользователю
                составлять персонализированные поздравления для друзей, родных и коллег.
                
                
                Твоя задача:

                Проанализировать полученную информацию, посмотреть есть ли "Ранее собранные данные". Если они были то, ты их найдешь после строки "Ранее собранные данные:", между двумя строками "***". Остальная информация - "Новая информация" находится после строки "Новая информация:", между двумя строками "---". Ты анализируешь новую информацию

                И собираешь ключевые факты, которые могут пригодиться для создания поздравления.                
                
                Это могут быть:                    
                    Событие с которым поздравляют (переезд, отпуск, свадьба, развод, новый проект, и т.д. и т.п.), если не указано, то не пиши про это.
                    Имя, возраст, родство или степень близости
                    Профессия, хобби, характер
                    Семейное положение, дети, питомцы
                    Интересные или забавные особенности
                    Отношение пользователя к адресату (уважение, дружба, ирония и т.д. и т.п.)                    
                    Пожелания пользователя о формате (стихотворение, хокку, проза и т.д. и т.п.) или стиле поздравления (официальное, игривое, романтическое, подкол и т.д. и т.п.). Если не указано, то не надо про это писать.
                    Собранные ключевые факты должны быть записаны кратко и информативно, без лишних слов (чтобы экономить токены).
                    Не придумывай факты и не фантазируй — только на основе полученной информации. Не пиши поздравлений, твоя цель — только структурировать факты для будущего поздравления.
                    
                    Если не было Ранее собранных данных, то твоим ответом будут Собранные ключевые факты.
                    
                    Если были Ранее собранные данные, их надо дополнить или скорректировать/уточнить собранными ключевыми фактами.
                    Собранные ключевые факты могут:
                    - Добавиться к фактам из Ранее собранных данных
                    - Уточнить или исправить факты в Ранее собранных данных
                    Твоим ответом в этом случае будут обновленные с учетом Собранных ключевых фактов Ранее собранные данные.
                    Ответ должен быть кратким и информативным, без лишних слов (чтобы экономить токены)                   
                
                """
            },
            
        ]
        if prev_context:
            old_content = f'Ранее собранные данные:\n***\n{prev_context.summory}\n***'
            messages.append({"role": "user", "content": old_content})
        new_content = f'Новая информация:\n---\n{text}\n---'
        messages.append({"role": "user", "content": new_content})
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using standard GPT-4o model
                messages=messages,                
            )
            result = response.choices[0].message.content
            logger.debug(f"Анализ контекста успешно завершен: {result}")
            return result
        except OpenAIError as e:
            logger.error(f"Ошибка OpenAI API: {str(e)}", exc_info=True)
            return prev_context.summory if prev_context else ""
        
        except Exception as e:
            logger.error(f"Неожиданная ошибка при анализе контекста: {str(e)}", exc_info=True)
            return prev_context.summory if prev_context else ""

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
                        "content": """Ты — мастер создания тёплых, уместных и запоминающихся поздравлений. На вход ты получаешь краткое описание фактов о человеке и пожелания к формату поздравления, собранные в ходе переписки.
                        
                        Твоя задача:
                        На основе предоставленных фактов о человеке и пожеланий создать одно персонализированное поздравление, подходящее для отправки в мессенджере вместе с открыткой. Если по полученной информации невозможно понять с каким событием поздравляют, ни что в поздравлении не должно быть однозначной привязкой к какому-то конкретному празднику.

                        Поздравление должно быть:

                            Ярким, образным, тёплым уместным по стилю. (Возможны разные варианты стилей: официальный, игривый, романтический, нежный, поэтический и т.д. — смотри указания к поздравлению). По умолчанию стиль - яркая проза. Используй эмодзи, если это необходимо.

                            Не длиннее 1000 символов!

                        Не повторяй факты дословно, используй их творчески.
                        Если указан поэтический формат — пиши стихами (например, четверостишия, хокку, белый стих, и т.д и т.п.).

                        Если стиль не указан — подбери нейтрально-дружелюбный тон, яркая проза.
                        
                        Подпись в конце не нужна.
                        """
                    },
                    {"role": "user", "content": f'Указания к поздравлению: *** {context.summory} ***'}
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

    async def generate_image(self, greeting_text) -> str:
        """
        Генерация изображения для поздравления
        """
        logger.debug("Начало генерации изображения")
        
        try:
            prompt = f"""Ты — генератор образных и эстетически приятных изображений-открыток. 
            На вход ты получаешь поздравление в виде текста.

            Твоя задача:

            Создай изображение, подходящее для поздравительной открытки, основываясь на Информацию АЛЬФА1. Если по информации АЛЬФА1 невозможно понять с каким событием поздравляют, ни что на изображении не должно быть однозначной привязкой к какому-то конкретному празднику.

            изображение должно передавать настроение, атмосферу события и детали связанные с поздравляемым. Изображение не должно содержать текста.

            Изображение должно быть:

                Ярким, но не перегруженным

                В соответствии с указанным стилем поздравления. По умолчанию открытка в стиле профессионального фото.
                            
            Информация АЛЬФА1:
            ***
            {greeting_text}
            ***
            """
            
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