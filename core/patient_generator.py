import random
from typing import Dict, Optional
from utils.name_generator import NameGenerator
from entities.priority import Priority
from events.patient_arrival_event import PatientArrivalEvent
from config.settings import PATIENT_GENERATION_SETTINGS, SOURCE_ID_MAPPING


class PatientGenerator:
    """Генератор пациентов с временными интервалами.
    ИБ - бесконечный источник, И32 - равномерный закон для интервалов"""

    def __init__(self, simulation_core):
        self.simulation_core = simulation_core
        self.next_patient_id = 1

        # Используем настройки из конфигурации
        self.arrival_settings = {
            Priority.EMERGENCY: PATIENT_GENERATION_SETTINGS['EMERGENCY'],
            Priority.BY_APPOINTMENT: PATIENT_GENERATION_SETTINGS['BY_APPOINTMENT'],
            Priority.WITHOUT_APPOINTMENT: PATIENT_GENERATION_SETTINGS['WITHOUT_APPOINTMENT']
        }

    def generate_next_arrival(self) -> Optional[float]:
        """Генерирует следующее время прибытия пациента"""

        # Выбираем тип пациента
        patient_type = self._select_patient_type()

        # Регистрируем генерацию в статистике
        self.simulation_core.statistics.record_patient_generation(patient_type)

        # Интервал прибытия
        settings = self.arrival_settings[patient_type]
        interval = random.uniform(settings['min_interval'], settings['max_interval'])

        next_arrival_time = self.simulation_core.current_time + interval

        # Создаем событие прибытия пациента
        source_id = self._priority_to_source_id(patient_type)
        arrival_event = PatientArrivalEvent(
            time=next_arrival_time,
            patient_id=self.next_patient_id,
            source_id=source_id
        )

        # Планируем событие
        self.simulation_core.schedule_event(arrival_event)

        patient_name = NameGenerator.generate_patient_name()
        print(f"Запланирован пациент {self.next_patient_id} "
              f"{str(patient_type)} - на время {next_arrival_time:.2f}")

        # ID для следующего пациента
        self.next_patient_id += 1

        return next_arrival_time

    def _select_patient_type(self) -> Priority:
        """Выбирает тип пациента по нашим вероятностям"""
        rand = random.random()
        emergency_prob = self.arrival_settings[Priority.EMERGENCY]['probability']
        appointment_prob = self.arrival_settings[Priority.BY_APPOINTMENT]['probability']

        if rand < emergency_prob:
            return Priority.EMERGENCY
        elif rand < emergency_prob + appointment_prob:
            return Priority.BY_APPOINTMENT
        else:
            return Priority.WITHOUT_APPOINTMENT

    def _priority_to_source_id(self, priority: Priority) -> int:
        """Конвертирует Priority в source_id"""
        mapping = {
            Priority.EMERGENCY: 1,
            Priority.BY_APPOINTMENT: 2,
            Priority.WITHOUT_APPOINTMENT: 3
        }
        return mapping[priority]

    def start_generation(self):
        """Запускает генерацию пациентов"""
        if not self.simulation_core.step_by_step:
            print("Запуск генерации пациентов с реалистичными интервалами...")
            print("Ожидаемое распределение:")
            for priority, settings in self.arrival_settings.items():
                print(f" • {settings['description']}: {settings['probability'] * 100:.0f}% "
                      f"(интервал {settings['min_interval']}-{settings['max_interval']} мин)")

        # Генерируем первого пациента
        self.generate_next_arrival()

    def get_generation_stats(self) -> Dict:
        """Возвращает статистику генерации (теперь делегирует Statistics)"""
        return self.simulation_core.statistics.get_generation_stats()