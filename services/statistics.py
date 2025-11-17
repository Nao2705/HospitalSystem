import math
from typing import Dict, List, Tuple, Optional
from entities.patient import Patient
from entities.priority import Priority
from config.settings import STATISTICS_SETTINGS


class Statistics:
    """Сбор и анализ статистики работы системы."""

    def __init__(self):
        # Основная статистика
        self.total_patients_arrived = 0
        self.total_patients_served = 0
        self.total_patients_rejected = 0
        self.total_wait_time = 0.0
        self.total_service_time = 0.0

        # Статистика по врачам
        self.doctors_stats: Dict[int, Dict] = {}  # doctor_id -> {served_count, total_service_time}

        # Статистика по приоритетам
        self.patients_by_priority: Dict[Priority, int] = {
            Priority.EMERGENCY: 0,
            Priority.BY_APPOINTMENT: 0,
            Priority.WITHOUT_APPOINTMENT: 0
        }

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

        self.wait_times_by_priority: Dict[Priority, List[float]] = {
            Priority.EMERGENCY: [],
            Priority.BY_APPOINTMENT: [],
            Priority.WITHOUT_APPOINTMENT: []
        }

        self.service_times_by_priority: Dict[Priority, List[float]] = {
            Priority.EMERGENCY: [],
            Priority.BY_APPOINTMENT: [],
            Priority.WITHOUT_APPOINTMENT: []
        }

        self.generation_stats = {
            Priority.EMERGENCY: 0,
            Priority.BY_APPOINTMENT: 0,
            Priority.WITHOUT_APPOINTMENT: 0
        }

    def initialize_doctor_stats(self, doctor_id: int):
        """Инициализирует статистику для врача"""
        if doctor_id not in self.doctors_stats:
            self.doctors_stats[doctor_id] = {
                'served_count': 0,
                'total_service_time': 0.0,
                'busy_time': 0.0
            }

    def record_service_end_by_doctor(self, doctor_id: int, service_time: float):
        """Записывает статистику обслуживания для врача"""
        self.initialize_doctor_stats(doctor_id)
        self.doctors_stats[doctor_id]['served_count'] += 1
        self.doctors_stats[doctor_id]['total_service_time'] += service_time
        self.doctors_stats[doctor_id]['busy_time'] += service_time

    def get_doctor_stats(self, doctor_id: int) -> Dict:
        """Возвращает статистику по врачу"""
        self.initialize_doctor_stats(doctor_id)
        return self.doctors_stats[doctor_id]

    def record_patient_generation(self, priority: Priority):
        """Регистрирует генерацию пациента"""
        self.generation_stats[priority] += 1

    def record_patient_arrival(self, patient: Patient) -> None:
        """Регистрирует прибытие пациента"""
        self.total_patients_arrived += 1
        self.patients_by_priority[patient.priority] += 1
        print(f"Статистика: Прибыл пациент {patient.id} ({str(patient.priority)})")

    def record_service_start(self, patient: Patient) -> None:
        """Регистрирует начало обслуживания"""
        if patient.service_start_time is not None and patient.arrival_time is not None:
            wait_time = patient.service_start_time - patient.arrival_time
            self.total_wait_time += wait_time
            self.wait_times_by_priority[patient.priority].append(wait_time)
            print(f" Статистика: Начало обслуживания пациента {patient.id}, "
                  f"время ожидания: {wait_time:.2f}")

    def record_service_end(self, patient: Patient) -> None:
        """Регистрирует окончание обслуживания"""
        self.total_patients_served += 1
        self.served_by_priority[patient.priority] += 1

        if patient.service_start_time is not None and patient.service_end_time is not None:
            service_time = patient.service_end_time - patient.service_start_time
            self.total_service_time += service_time
            self.service_times_by_priority[patient.priority].append(service_time)

        print(f" Статистика: Обслужен пациент {patient.id} ({str(patient.priority)})")

    def record_patient_rejection(self, patient: Patient) -> None:
        """Регистрирует отказ пациенту"""
        self.total_patients_rejected += 1
        self.rejected_by_priority[patient.priority] += 1
        print(f"Статистика: Отказ пациенту {patient.id} ({str(patient.priority)}), "
              f"время прибытия: {patient.arrival_time:.2f}")

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

    def calculate_variance(self, data: List[float]) -> float:
        """Вычисляет дисперсию"""
        if len(data) < 2:
            return 0.0
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        return variance

    def calculate_standard_deviation(self, data: List[float]) -> float:
        """Вычисляет стандартное отклонение"""
        variance = self.calculate_variance(data)
        return math.sqrt(variance) if variance > 0 else 0.0

    def calculate_confidence_interval(self, probability: float, n: int) -> Tuple[float, float]:
        """Вычисляет доверительный интервал"""
        if n == 0:
            return (0.0, 0.0)

        t_alpha = STATISTICS_SETTINGS['confidence_t_alpha']
        margin = t_alpha * math.sqrt(probability * (1 - probability) / n)
        return (max(0, probability - margin), min(1, probability + margin))

    def calculate_required_n(self, current_probability: float) -> int:
        """Вычисляет необходимое количество заявок для заданной точности"""
        if current_probability == 0:
            return STATISTICS_SETTINGS['min_patients_for_accuracy']

        t_alpha = STATISTICS_SETTINGS['confidence_t_alpha']
        delta = STATISTICS_SETTINGS['relative_accuracy_delta']

        n = (t_alpha ** 2 * (1 - current_probability)) / (current_probability * delta ** 2)
        return max(STATISTICS_SETTINGS['min_patients_for_accuracy'], int(n))

    def get_average_wait_time(self, priority: Optional[Priority] = None) -> float:
        """Возвращает среднее время ожидания"""
        if priority:
            wait_times = self.wait_times_by_priority[priority]
            return sum(wait_times) / len(wait_times) if wait_times else 0.0
        else:
            return self.total_wait_time / self.total_patients_served if self.total_patients_served > 0 else 0.0

    def get_average_service_time(self, priority: Optional[Priority] = None) -> float:
        """Возвращает среднее время обслуживания"""
        if priority:
            service_times = self.service_times_by_priority[priority]
            return sum(service_times) / len(service_times) if service_times else 0.0
        else:
            return self.total_service_time / self.total_patients_served if self.total_patients_served > 0 else 0.0

    def get_rejection_rate(self, priority: Optional[Priority] = None) -> float:
        """Возвращает процент отказов"""
        if priority:
            arrived = self.patients_by_priority[priority]
            rejected = self.rejected_by_priority[priority]
            return (rejected / arrived * 100) if arrived > 0 else 0.0
        else:
            return (
                        self.total_patients_rejected / self.total_patients_arrived * 100) if self.total_patients_arrived > 0 else 0.0

    def generate_detailed_report(self, total_simulation_time: float, doctors_count: int) -> Dict:
        """Генерирует детальный отчет согласно требованиям"""

        # Таблица 1: Характеристики источников ВС
        sources_table = []
        for priority in [Priority.EMERGENCY, Priority.BY_APPOINTMENT, Priority.WITHOUT_APPOINTMENT]:
            arrived = self.patients_by_priority[priority]
            served = self.served_by_priority[priority]
            rejected = self.rejected_by_priority[priority]

            # Вероятность отказа
            p_reject = rejected / arrived if arrived > 0 else 0

            # Среднее время пребывания
            wait_times = self.wait_times_by_priority[priority]
            service_times = self.service_times_by_priority[priority]

            avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
            avg_service = sum(service_times) / len(service_times) if service_times else 0
            avg_total = avg_wait + avg_service

            # Дисперсии
            var_wait = self.calculate_variance(wait_times)
            var_service = self.calculate_variance(service_times)

            # Доверительный интервал для вероятности отказа
            conf_interval = self.calculate_confidence_interval(p_reject, arrived) if arrived > 0 else (0, 0)

            sources_table.append({
                'source_id': priority.value,
                'priority': str(priority),
                'total_arrived': arrived,
                'total_served': served,
                'total_rejected': rejected,
                'p_reject': p_reject,
                'p_reject_percent': p_reject * 100,
                'avg_total_time': avg_total,
                'avg_wait_time': avg_wait,
                'avg_service_time': avg_service,
                'variance_wait': var_wait,
                'variance_service': var_service,
                'std_wait': self.calculate_standard_deviation(wait_times),
                'std_service': self.calculate_standard_deviation(service_times),
                'confidence_interval': conf_interval,
                'required_n_for_accuracy': self.calculate_required_n(p_reject) if arrived > 0 else 0
            })

        # Общая статистика системы
        total_reject_rate = self.total_patients_rejected / self.total_patients_arrived if self.total_patients_arrived > 0 else 0
        total_conf_interval = self.calculate_confidence_interval(total_reject_rate, self.total_patients_arrived)

        # Статистика использования системы
        system_utilization = {}
        for doctor_id, stats in self.doctors_stats.items():
            utilization = (stats['busy_time'] / total_simulation_time * 100) if total_simulation_time > 0 else 0
            system_utilization[doctor_id] = {
                'served_count': stats['served_count'],
                'total_service_time': stats['total_service_time'],
                'utilization_percent': utilization,
                'avg_service_time_per_patient': stats['total_service_time'] / stats['served_count'] if stats[
                                                                                                           'served_count'] > 0 else 0
            }

        # Средняя загрузка системы
        avg_system_utilization = sum(stats['utilization_percent'] for stats in system_utilization.values()) / len(
            system_utilization) if system_utilization else 0

        return {
            'sources_characteristics': sources_table,
            'system_characteristics': {
                'total_simulation_time': total_simulation_time,
                'total_patients_arrived': self.total_patients_arrived,
                'total_patients_served': self.total_patients_served,
                'total_patients_rejected': self.total_patients_rejected,
                'total_reject_rate': total_reject_rate * 100,
                'confidence_interval': total_conf_interval,
                'avg_wait_time': self.get_average_wait_time(),
                'avg_service_time': self.get_average_service_time(),
                'system_utilization': avg_system_utilization,
                'doctors_utilization': system_utilization
            },
            'generation_stats': self.get_generation_stats()
        }

    def generate_report(self) -> Dict:
        """Генерирует сводный отчет (ОР1)"""
        if self.total_patients_arrived == 0:
            return {"message": "Нет данных для отчета"}

        avg_wait_time = self.get_average_wait_time()
        avg_service_time = self.get_average_service_time()
        total_reject_rate = self.get_rejection_rate()

        # Подробная статистика по приоритетам
        priority_details = {}
        for priority in [Priority.EMERGENCY, Priority.BY_APPOINTMENT, Priority.WITHOUT_APPOINTMENT]:
            arrived = self.patients_by_priority[priority]
            served = self.served_by_priority[priority]
            rejected = self.rejected_by_priority[priority]
            avg_wait = self.get_average_wait_time(priority)
            avg_service = self.get_average_service_time(priority)
            reject_rate = self.get_rejection_rate(priority)

            priority_details[str(priority)] = {
                "прибыло": arrived,
                "обслужено": served,
                "отказано": rejected,
                "среднее_время_ожидания": avg_wait,
                "среднее_время_обслуживания": avg_service,
                "процент_отказов": reject_rate
            }

        report = {
            "Общее_количество_пациентов": self.total_patients_arrived,
            "Обслужено_пациентов": self.total_patients_served,
            "Отказано_пациентов": self.total_patients_rejected,
            "Процент_отказов": total_reject_rate,
            "Среднее_время_ожидания": avg_wait_time,
            "Среднее_время_обслуживания": avg_service_time,
            "Общее_время_ожидания": self.total_wait_time,
            "Общее_время_обслуживания": self.total_service_time,
            "Распределение_по_приоритетам": priority_details
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
            f" Неотложная помощь: прибыло {self.patients_by_priority[Priority.EMERGENCY]}, "
            f"обслужено {self.served_by_priority[Priority.EMERGENCY]}, "
            f"отказано {self.rejected_by_priority[Priority.EMERGENCY]}",
            f" По записи: прибыло {self.patients_by_priority[Priority.BY_APPOINTMENT]}, "
            f"обслужено {self.served_by_priority[Priority.BY_APPOINTMENT]}, "
            f"отказано {self.rejected_by_priority[Priority.BY_APPOINTMENT]}",
            f" Без записи: прибыло {self.patients_by_priority[Priority.WITHOUT_APPOINTMENT]}, "
            f"обслужено {self.served_by_priority[Priority.WITHOUT_APPOINTMENT]}, "
            f"отказано {self.rejected_by_priority[Priority.WITHOUT_APPOINTMENT]}"
        ]

        # Добавляем статистику по времени, если есть данные
        if self.total_patients_served > 0:
            state.extend([
                "",
                "Статистика времени:",
                f" Среднее время ожидания: {self.get_average_wait_time():.2f} мин",
                f" Среднее время обслуживания: {self.get_average_service_time():.2f} мин"
            ])

        return "\n".join(state)

    def reset_statistics(self):
        """Сбрасывает всю статистику"""
        self.__init__()

    def get_summary(self) -> Dict:
        """Возвращает краткую сводку статистики"""
        return {
            'total_arrived': self.total_patients_arrived,
            'total_served': self.total_patients_served,
            'total_rejected': self.total_patients_rejected,
            'rejection_rate': self.get_rejection_rate(),
            'avg_wait_time': self.get_average_wait_time(),
            'avg_service_time': self.get_average_service_time(),
            'emergency_stats': {
                'arrived': self.patients_by_priority[Priority.EMERGENCY],
                'served': self.served_by_priority[Priority.EMERGENCY],
                'rejected': self.rejected_by_priority[Priority.EMERGENCY],
                'rejection_rate': self.get_rejection_rate(Priority.EMERGENCY)
            },
            'appointment_stats': {
                'arrived': self.patients_by_priority[Priority.BY_APPOINTMENT],
                'served': self.served_by_priority[Priority.BY_APPOINTMENT],
                'rejected': self.rejected_by_priority[Priority.BY_APPOINTMENT],
                'rejection_rate': self.get_rejection_rate(Priority.BY_APPOINTMENT)
            },
            'walkin_stats': {
                'arrived': self.patients_by_priority[Priority.WITHOUT_APPOINTMENT],
                'served': self.served_by_priority[Priority.WITHOUT_APPOINTMENT],
                'rejected': self.rejected_by_priority[Priority.WITHOUT_APPOINTMENT],
                'rejection_rate': self.get_rejection_rate(Priority.WITHOUT_APPOINTMENT)
            }
        }

    def __str__(self) -> str:
        return self.get_current_state()