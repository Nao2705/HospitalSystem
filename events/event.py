from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.simulation_core import SimulationCore


class Event(ABC):
    """
    Базовый класс для всех событий в системе.
    Реализует сравнение для работы в приоритетной очереди.
    """

    def __init__(self, time: float):
        self.time = time

    def get_time(self) -> float:
        """Возвращает время события"""
        return self.time

    @abstractmethod
    def process_event(self, core: 'SimulationCore') -> None:
        """Обрабатывает событие - должен быть реализован в подклассах"""
        pass

    def __lt__(self, other: 'Event') -> bool:
        """
        Сравнение событий по времени для приоритетной очереди.
        Событие с меньшим временем имеет высший приоритет.
        """
        return self.time < other.time

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(time={self.time:.2f})"

    def __repr__(self) -> str:
        return self.__str__()