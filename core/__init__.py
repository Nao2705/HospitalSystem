"""
Пакет ядра имитационной модели.
Содержит основные компоненты управления системой.
"""

from .simulation_core import SimulationCore
from .patient_generator import PatientGenerator

__all__ = [
    'SimulationCore',
    'PatientGenerator'
]