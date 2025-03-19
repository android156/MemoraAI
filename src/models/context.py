"""
Модель контекста диалога
"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class Context:
    """Класс для хранения контекста диалога"""
    name: str = ""
    holiday: str = ""
    interests: List[str] = field(default_factory=list)
    characteristics: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    
    def add_message(self, message: str):
        """Добавление нового сообщения в контекст"""
        self.messages.append(message)
    
    def get_summary(self) -> str:
        """
        Формирование резюме контекста
        """
        summary = []
        if self.name:
            summary.append(f"Поздравляем: **{self.name}**")
        if self.holiday:
            summary.append(f"Праздник: **{self.holiday}**")
        if self.interests:
            summary.append("Интересы:")
            for interest in self.interests:
                summary.append(f"- **{interest}**")
        if self.characteristics:
            summary.append("Особенности:")
            for char in self.characteristics:
                summary.append(f"- **{char}**")
        
        return "\n".join(summary) if summary else "Контекст пока пуст"
    
    def __str__(self) -> str:
        """Строковое представление контекста"""
        return self.get_summary()
