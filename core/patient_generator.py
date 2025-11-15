import random
from typing import Dict
from entities.patient import Patient
from utils.name_generator import NameGenerator
from entities.priority import Priority
from events.patient_arrival_event import PatientArrivalEvent


class PatientGenerator:
    """
    Генератор пациентов с реалистичными временными интервалами.
    ИБ - бесконечный источник, И32 - равномерный закон для интервалов
    """

    def __init__(self, simulation_core):
        self.simulation_core = simulation_core
        self.next_patient_id = 1

        # РЕАЛИСТИЧНЫЕ настройки для 8-часового рабочего дня (480 минут)
        self.arrival_settings = {
            Priority.EMERGENCY: {
                'min_interval': 45.0,  # 45-120 минут между неотложками
                'max_interval': 120.0,
                'probability': 0.15,  # 15% - неотложные случаи
                'description': 'Неотложная помощь'
            },
            Priority.BY_APPOINTMENT: {
                'min_interval': 10.0,  # 10-25 минут между записями
                'max_interval': 25.0,
                'probability': 0.45,  # 45% - по записи (основной поток)
                'description': 'По записи'
            },
            Priority.WITHOUT_APPOINTMENT: {
                'min_interval': 5.0,  # 5-15 минут между без записи
                'max_interval': 15.0,
                'probability': 0.40,  # 40% - без записи
                'description': 'Без записи'
            }
        }

        # Статистика для анализа
        self.generation_stats = {
            Priority.EMERGENCY: 0,
            Priority.BY_APPOINTMENT: 0,
            Priority.WITHOUT_APPOINTMENT: 0
        }

    def generate_next_arrival(self) -> float:
        """
        Генерирует следующее время прибытия пациента
        """
        # 1. Выбираем тип пациента
        patient_type = self._select_patient_type()
        self.generation_stats[patient_type] += 1

        # 2. Реалистичный интервал прибытия
        settings = self.arrival_settings[patient_type]
        interval = random.uniform(settings['min_interval'], settings['max_interval'])

        next_arrival_time = self.simulation_core.current_time + interval

        # 3. Создаем событие прибытия пациента
        source_id = self._priority_to_source_id(patient_type)
        arrival_event = PatientArrivalEvent(
            time=next_arrival_time,
            patient_id=self.next_patient_id,
            source_id=source_id
        )

        # 4. Планируем событие
        self.simulation_core.schedule_event(arrival_event)

        # 5. Красивый вывод
        patient_name = NameGenerator.generate_patient_name()
        print(f"Запланирован пациент {self.next_patient_id}: {patient_name} "
              f"({patient_type}) в время {next_arrival_time:.2f}")

        # 6. Подготавливаем следующий ID
        self.next_patient_id += 1

        return next_arrival_time

    def _select_patient_type(self) -> Priority:
        """Выбирает тип пациента по реалистичным вероятностям"""
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
        print("Запуск генерации пациентов с реалистичными интервалами...")
        print("Ожидаемое распределение:")
        for priority, settings in self.arrival_settings.items():
            print(f"   • {settings['description']}: {settings['probability'] * 100:.0f}% "
                  f"(интервал {settings['min_interval']}-{settings['max_interval']} мин)")

        # Генерируем первого пациента
        self.generate_next_arrival()

    def get_generation_stats(self) -> Dict:
        """Возвращает статистику генерации"""
        total = sum(self.generation_stats.values())
        if total == 0:
            return {}

        return {
            'total_generated': total,
            'emergency_count': self.generation_stats[Priority.EMERGENCY],
            'appointment_count': self.generation_stats[Priority.BY_APPOINTMENT],
            'walkin_count': self.generation_stats[Priority.WITHOUT_APPOINTMENT],
            'emergency_percent': (self.generation_stats[Priority.EMERGENCY] / total) * 100,
            'appointment_percent': (self.generation_stats[Priority.BY_APPOINTMENT] / total) * 100,
            'walkin_percent': (self.generation_stats[Priority.WITHOUT_APPOINTMENT] / total) * 100
        }