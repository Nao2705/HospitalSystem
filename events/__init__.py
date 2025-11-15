"""
Пакет событий для имитационной модели.
"""

from .event import Event
from .patient_arrival_event import PatientArrivalEvent
from .service_end_event import ServiceEndEvent

__all__ = [
    'Event',
    'PatientArrivalEvent',
    'ServiceEndEvent'
]