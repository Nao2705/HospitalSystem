from typing import Dict, List
from entities.patient import Patient
from entities.priority import Priority


class Statistics:
    """
    Сбор и анализ статистики работы системы.
    Соответствует Statistics из твоей схемы.
    """

    def __init__(self):
        self.total_patients_arrived = 0
        self.total_patients_served = 0
        self.total_patients_rejected = 0
        self.total_wait_time = 0.0
        self.patients_by_priority: Dict[Priority, int] = {
            Priority.EMERGENCY: 0,
            Priority.BY_APPOINTMENT: 0,
            Priority.WITHOUT_APPOINTMENT: 0
        }

        # Дополнительная статистика для анализа
        self.served_by_priority: Dict[Priority, int] = {
            Priority.EMERGENCY: 0,
            Priority.BY_APPOINTMENT: 0,
            Priority.WITHOUT_APPOINTMENT: 0
        }
        self.rejected_by_priority: Dict[Priority, int] = {
            Priority.EMERGENCY: 0,
            Priority.BY_APPOINTMENT: 0,
            Priority.WITHOUT_APPOINTMENT: 0
        }
        self.wait_times: List[float] = []

    def record_patient_arrival(self, patient: Patient) -> None:
        """Регистрирует прибытие пациента"""
        self.total_patients_arrived += 1
        self.patients_by_priority[patient.priority] += 1
        print(f"Статистика: Прибыл пациент {patient.id} ({patient.priority})")

    def record_service_start(self, patient: Patient) -> None:
        """Регистрирует начало обслуживания"""
        if patient.service_start_time is not None and patient.arrival_time is not None:
            wait_time = patient.service_start_time - patient.arrival_time
            self.total_wait_time += wait_time
            self.wait_times.append(wait_time)
            print(f" Статистика: Начало обслуживания пациента {patient.id}, "
                  f"время ожидания: {wait_time:.2f}")

    def record_service_end(self, patient: Patient) -> None:
        """Регистрирует окончание обслуживания"""
        self.total_patients_served += 1
        self.served_by_priority[patient.priority] += 1
        print(f" Статистика: Обслужен пациент {patient.id} ({patient.priority})")

    def record_patient_rejection(self, patient: Patient) -> None:
        """Регистрирует отказ пациенту"""
        self.total_patients_rejected += 1
        self.rejected_by_priority[patient.priority] += 1
        print(f"Статистика: Отказ пациенту {patient.id} ({patient.priority})")

    def generate_report(self) -> Dict:
        """Генерирует сводный отчет (ОР1)"""
        if self.total_patients_arrived == 0:
            return {"message": "Нет данных для отчета"}

        avg_wait_time = (self.total_wait_time / self.total_patients_served
                         if self.total_patients_served > 0 else 0)

        report = {
            "Общее количество пациентов": self.total_patients_arrived,
            "Обслужено пациентов": self.total_patients_served,
            "Отказано пациентов": self.total_patients_rejected,
            "Процент отказов": (self.total_patients_rejected / self.total_patients_arrived) * 100,
            "Среднее время ожидания": avg_wait_time,
            "Распределение по приоритетам": {
                "Неотложная помощь": {
                    "прибыло": self.patients_by_priority[Priority.EMERGENCY],
                    "обслужено": self.served_by_priority[Priority.EMERGENCY],
                    "отказано": self.rejected_by_priority[Priority.EMERGENCY]
                },
                "По записи": {
                    "прибыло": self.patients_by_priority[Priority.BY_APPOINTMENT],
                    "обслужено": self.served_by_priority[Priority.BY_APPOINTMENT],
                    "отказано": self.rejected_by_priority[Priority.BY_APPOINTMENT]
                },
                "Без записи": {
                    "прибыло": self.patients_by_priority[Priority.WITHOUT_APPOINTMENT],
                    "обслужено": self.served_by_priority[Priority.WITHOUT_APPOINTMENT],
                    "отказано": self.rejected_by_priority[Priority.WITHOUT_APPOINTMENT]
                }
            }
        }

        return report

    def get_current_state(self) -> str:
        """Возвращает текущее состояние системы (ОД2)"""
        state = [
            "=== ТЕКУЩЕЕ СОСТОЯНИЕ СИСТЕМЫ ===",
            f"Всего пациентов: {self.total_patients_arrived}",
            f"Обслужено: {self.total_patients_served}",
            f"Отказано: {self.total_patients_rejected}",
            f"В ожидании: {self.total_patients_arrived - self.total_patients_served - self.total_patients_rejected}",
            "",
            "По приоритетам:",
            f"  Неотложная помощь: {self.patients_by_priority[Priority.EMERGENCY]}",
            f"  По записи: {self.patients_by_priority[Priority.BY_APPOINTMENT]}",
            f"  Без записи: {self.patients_by_priority[Priority.WITHOUT_APPOINTMENT]}"
        ]

        return "\n".join(state)

    def __str__(self) -> str:
        return self.get_current_state()
