from typing import TYPE_CHECKING
from events.event import Event

if TYPE_CHECKING:
    from core.simulation_core import SimulationCore


class ServiceEndEvent(Event):
    """Событие окончания обслуживания пациента."""

    def __init__(self, time: float, doctor_id: int, patient_id: int):
        super().__init__(time)
        self.doctor_id = doctor_id
        self.patient_id = patient_id

    def process_event(self, core: 'SimulationCore') -> None:
        """Обрабатывает окончание обслуживания"""
        print(f"Время {self.time:.2f}: Завершение обслуживания врачом {self.doctor_id}, пациент {self.patient_id}")

        # Находим врача
        doctor = None
        for doc in core.doctors:
            if doc.id == self.doctor_id:
                doctor = doc
                break

        if doctor is None:
            print(f"Ошибка: Врач {self.doctor_id} не найден")
            return

        # Завершаем обслуживание
        try:
            patient = doctor.end_service(self.time)

            if patient is None:
                print(f"Ошибка: Врач {doctor.name} не занят обслуживанием")
                return

            # Регистрируем в статистике
            core.statistics.record_service_end(patient)

            # Уведомляем диспетчер о свободном враче
            core.dispatcher.on_doctor_became_free(self.doctor_id, self.time)

            print(f"Врач {doctor.name} освободился после приема {patient.name}")

        except Exception as e:
            print(f"Ошибка при завершении обслуживания: {e}")

    def __str__(self) -> str:
        return f"ServiceEndEvent(time={self.time:.2f}, doctor_id={self.doctor_id}, patient_id={self.patient_id})"