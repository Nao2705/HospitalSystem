from typing import TYPE_CHECKING
from events.event import Event

if TYPE_CHECKING:
    from core.simulation_core import SimulationCore


class PatientArrivalEvent(Event):
    """
    Событие прибытия нового пациента.
    """

    def __init__(self, time: float, patient_id: int, source_id: int):
        super().__init__(time)
        self.patient_id = patient_id
        self.source_id = source_id

    def process_event(self, core: 'SimulationCore') -> None:
        """Обрабатывает прибытие пациента"""
        print(f"Время {self.time:.2f}: Обработка прибытия пациента {self.patient_id} из источника {self.source_id}")

        # Создаем пациента с использованием общего NameGenerator
        from entities.patient import Patient
        from utils.name_generator import NameGenerator

        patient = Patient(
            id=self.patient_id,
            source_id=self.source_id,
            arrival_time=self.time,
            name=NameGenerator.generate_patient_name()
        )

        # Регистрируем в статистике
        core.statistics.record_patient_arrival(patient)

        # Передаем диспетчеру
        success = core.dispatcher.on_patient_arrival(patient, self.time)

        if not success:
            print(f"Пациенту {patient.name} отказано в обслуживании")

        # Планируем следующее прибытие (бесконечный источник)
        core.schedule_next_arrival()

    def __str__(self) -> str:
        return f"PatientArrivalEvent(time={self.time:.2f}, patient_id={self.patient_id}, source_id={self.source_id})"