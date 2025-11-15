from dataclasses import dataclass, field
from typing import Optional
from entities.priority import Priority

@dataclass
class Patient:
    id: int
    source_id: int
    arrival_time: float
    name: str
    service_start_time: Optional[float] = None
    service_end_time: Optional[float] = None
    priority: Priority = field(init=False)  # Вычисляется автоматически

    def __post_init__(self):
        """Автоматически устанавливаем приоритет на основе source_id"""
        if self.source_id == 1:
            self.priority = Priority.EMERGENCY
        elif self.source_id == 2:
            self.priority = Priority.BY_APPOINTMENT
        else:
            self.priority = Priority.WITHOUT_APPOINTMENT

    def __str__(self):
        return f"Пациент {self.id}: {self.name} ({self.priority})"