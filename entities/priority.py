from enum import Enum


class Priority(Enum):
    EMERGENCY = 1
    BY_APPOINTMENT = 2
    WITHOUT_APPOINTMENT = 3

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        """Возвращает понятное строковое представление"""
        descriptions = {
            1: "срочно",
            2: "по записи",
            3: "без записи"
        }
        return descriptions[self.value]