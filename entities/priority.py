from enum import Enum

'''Существует 3 типа пациентов по приоритету
необходима неотложная помощь - наивысший приоритет,
пациенты, кто пришел по записи - средний приоритет 
и те, кто пришел без записи и их здоровью ничего не угрожает - низший приоритет'''

class Priority(Enum):
    EMERGENCY = 1
    BY_APPOINTMENT = 2
    WITHOUT_APPOINTMENT = 3

def __lt__ (self, other):
    return self.value < other.value

def __str__ (self):
    names = {
        1: "Неотложная помощь",
        2: "По записи",
        3: "Без записи"
    }
    return names[self.value]
