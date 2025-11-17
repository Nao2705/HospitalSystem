from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.simulation_core import SimulationCore


class Event(ABC):
    """Базовый класс для всех событий в системе.
    Реализует сравнение для работы в приоритетной очереди."""

    def __init__(self, time: float):
        self.time = time
        self.event_id = 0  # Идентификатор для разрешения коллизий времени

    def get_time(self) -> float:
        """Возвращает время события"""
        return self.time

    @abstractmethod
    def process_event(self, core: 'SimulationCore') -> None:
        """Обрабатывает событие - реализован в подклассах"""
        pass

    def __lt__(self, other: 'Event') -> bool:
        """Сравнение событий по времени и ID для одинаковой по приоритету очереди.
        Событие с меньшим временем имеет высший приоритет.
        При одинаковом времени - с меньшим ID."""
        if self.time == other.time:
            return self.event_id < other.event_id
        return self.time < other.time

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(time={self.time:.2f}, id={self.event_id})"

    def __repr__(self) -> str:
        return self.__str__()