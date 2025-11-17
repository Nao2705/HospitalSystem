import heapq
import sys
from typing import List, Dict, Optional
from entities.doctor import Doctor
from services.waiting_room import WaitingRoom
from services.dispatcher import Dispatcher
from services.statistics import Statistics
from core.patient_generator import PatientGenerator
from entities.priority import Priority
from events.service_end_event import ServiceEndEvent
from config.settings import (
    DEFAULT_NUM_DOCTORS, DEFAULT_BUFFER_CAPACITY, DEFAULT_MEAN_SERVICE_TIME,
    DISPLAY_SETTINGS, DISPLAY_DESCRIPTIONS
)


class SimulationCore:
    """Главный класс управления имитационной моделью.
    Запускает и координирует все компоненты системы."""

    def __init__(self):
        self.current_time = 0.0
        self.event_queue = []
        self.doctors: List[Doctor] = []
        self.waiting_room: WaitingRoom = None
        self.dispatcher: Dispatcher = None
        self.patient_generator: PatientGenerator = None
        self.statistics: Statistics = None
        self.running = False
        self.next_patient_id = 1
        self.step_by_step = True  # Всегда пошаговый режим
        self.total_simulation_time = 0.0
        self.should_stop = False
        self.event_counter = 0
        self.step_count = 0

    def initialize_system(self, num_doctors: int = DEFAULT_NUM_DOCTORS,
                          buffer_capacity: int = DEFAULT_BUFFER_CAPACITY,
                          mean_service_time: float = DEFAULT_MEAN_SERVICE_TIME):
        """Инициализирует все компоненты системы"""
        print("ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ МАССОВОГО ОБСЛУЖИВАНИЯ")
        print("=" * 50)

        # Создаем врачей
        self.doctors = []
        for i in range(1, num_doctors + 1):
            doctor = Doctor(
                doctor_id=i,
                mean_service_time=mean_service_time
            )
            self.doctors.append(doctor)
            print(f"Создан врач: {doctor.name}")

        # Создаем буфер ожидания
        self.waiting_room = WaitingRoom(capacity=buffer_capacity)
        print(f"Создан буфер ожидания на {buffer_capacity} мест")

        # Создаем статистику
        self.statistics = Statistics()
        print("Система статистики инициализирована")

        # Создаем диспетчер
        self.dispatcher = Dispatcher(
            doctors=self.doctors,
            waiting_room=self.waiting_room,
            simulation_core=self
        )
        print("Диспетчер инициализирован")

        # Создаем генератор пациентов
        self.patient_generator = PatientGenerator(self)
        print("Генератор пациентов готов к работе")

        print("=" * 50)
        print("СИСТЕМА ГОТОВА К РАБОТЕ")
        print()


    def schedule_event(self, event):
        """Добавляет событие в приоритетную очередь с учетом коллизий времени"""
        event.event_id = self.event_counter
        self.event_counter += 1
        heapq.heappush(self.event_queue, event)

    def schedule_next_arrival(self):
        """Планирует следующее прибытие пациента"""
        self.patient_generator.generate_next_arrival()

    def get_next_patient_id(self) -> int:
        """Возвращает следующий ID пациента и увеличивает счетчик"""
        patient_id = self.next_patient_id
        self.next_patient_id += 1
        return patient_id

    def find_doctor_by_id(self, doctor_id: int) -> Optional[Doctor]:
        """Находит врача по ID"""
        for doctor in self.doctors:
            if doctor.id == doctor_id:
                return doctor
        return None

    def display_step_state(self, current_event=None):
        """Отображает состояние системы в пошаговом режиме с таблицами"""
        self.step_count += 1

        table_width = DISPLAY_SETTINGS['table_width']
        print(f"\n{'=' * table_width}")
        print(f"ШАГ {self.step_count} - Время: {self.current_time:.2f} мин")
        print(f"{'=' * table_width}")

        if current_event:
            print(f"ОБРАБАТЫВАЕМОЕ СОБЫТИЕ: {current_event}")
            print(f"{'-' * table_width}")

        # Таблица 1: Календарь событий
        print("ТАБЛИЦА 1 - КАЛЕНДАРЬ СОБЫТИЙ")
        print(f"{'Событие':<25} {'Время':<10} {'Пациент':<10} {'Врач':<10}")
        print(f"{'-' * 55}")

        if self.event_queue:
            next_events = heapq.nsmallest(DISPLAY_SETTINGS['max_events_display'], self.event_queue)
            for event in next_events:
                if hasattr(event, 'patient_id'):
                    patient_info = f"P{event.patient_id}"
                else:
                    patient_info = "-"

                if hasattr(event, 'doctor_id'):
                    doctor_info = f"D{event.doctor_id}"
                else:
                    doctor_info = "-"

                event_type = event.__class__.__name__
                print(f"{event_type:<25} {event.time:<10.2f} {patient_info:<10} {doctor_info:<10}")
        else:
            print("Нет запланированных событий")

        print(f"{'-' * table_width}")

        # Таблица 2: Буфер ожидания
        print("ТАБЛИЦA 2 - БУФЕР ОЖИДАНИЯ")
        print(f"{'Позиция':<10} {'Время':<10} {'Источник':<10} {'Заявка':<10} {'Приоритет':<15}")
        print(f"{'-' * 55}")

        buffer_info = self.waiting_room.get_queue_info()
        for i, patient in enumerate(buffer_info):
            if patient is not None:
                source_desc = DISPLAY_DESCRIPTIONS['sources'].get(patient.source_id, f"И{patient.source_id}")
                print(
                    f"{i + 1:<10} {patient.arrival_time:<10.2f} {source_desc:<10} P{patient.id:<9} {str(patient.priority):<15}")
            else:
                print(f"{i + 1:<10} {'0.0':<10} {'0':<10} {'0':<10} {'-':<15}")

        print(f"Занято мест: {self.waiting_room.size}/{self.waiting_room.capacity}")
        print(f"{'-' * table_width}")

        # ТАБЛИЦА 3: Приборы (Врачи)
        print("ТАБЛИЦA 3 - ПРИБОРЫ (ВРАЧИ)")
        print(f"{'Врач':<15} {'Состояние':<15} {'Пациент':<15} {'Время начала':<15} {'Прогноз конца':<15}")
        print(f"{'-' * 75}")

        for doctor in self.doctors:
            if doctor.is_busy and doctor.current_patient:
                status = DISPLAY_DESCRIPTIONS['statuses']['busy']
                patient_name = f"P{doctor.current_patient.id}"
                start_time = f"{doctor.current_patient.service_start_time:.2f}"

                # ИСПРАВЛЕННЫЙ РАСЧЕТ: используем реальное время окончания из события
                service_end_time = None
                for event in self.event_queue:
                    if (hasattr(event, 'doctor_id') and event.doctor_id == doctor.id and
                            isinstance(event, ServiceEndEvent)):
                        service_end_time = event.time
                        break

                if service_end_time:
                    end_time = f"{service_end_time:.2f}"
                else:
                    end_time = "расчет..."

            else:
                status = DISPLAY_DESCRIPTIONS['statuses']['free']
                patient_name = "-"
                start_time = "-"
                end_time = "-"

            print(f"{doctor.name:<15} {status:<15} {patient_name:<15} {start_time:<15} {end_time:<15}")

        print(f"{'-' * table_width}")

        # Таблица 4: Указатели и статистика
        print("ТАБЛИЦА 4 - УКАЗАТЕЛИ И СТАТИСТИКА")
        print(f"{'Параметр':<30} {'Значение':<20}")
        print(f"{'-' * 50}")

        # Указатели
        print(f"{'Следующий врач (Д2П2)':<30} #{self.dispatcher.next_doctor_index + 1:<20}")

        # Статистика
        stats = self.statistics
        total_arrived = stats.total_patients_arrived
        total_served = stats.total_patients_served
        total_rejected = stats.total_patients_rejected

        print(f"{'Всего пациентов':<30} {total_arrived:<20}")
        print(f"{'Обслужено':<30} {total_served:<20}")
        print(f"{'Отказов':<30} {total_rejected:<20}")

        if total_arrived > 0:
            rejection_rate = (total_rejected / total_arrived) * 100
            print(f"{'Процент отказов':<30} {rejection_rate:.2f}%")

        # Статистика по приоритетам
        print(f"{'--- По приоритетам ---':<30} {'':<20}")
        for priority in [Priority.EMERGENCY, Priority.BY_APPOINTMENT, Priority.WITHOUT_APPOINTMENT]:
            arrived = stats.patients_by_priority[priority]
            served = stats.served_by_priority[priority]
            rejected = stats.rejected_by_priority[priority]

            if arrived > 0:
                rejection_rate = (rejected / arrived) * 100
                print(f"{str(priority):<30} {f'прибыло {arrived}, отказов {rejected} ({rejection_rate:.1f}%)':<20}")

        print(f"{'=' * table_width}")

    def run(self):
        """Запускает симуляцию в пошаговом режиме БЕЗ ограничений по времени"""
        print("РЕЖИМ ПОШАГОВОГО ВЫПОЛНЕНИЯ")
        print("Нажимайте Enter для перехода к следующему событию")
        print("Введите 'q' для выхода из симуляции")
        print("=" * 100)

        self.running = True
        self.step_count = 0

        # Запускаем генерацию пациентов
        self.patient_generator.start_generation()

        # Главный цикл симуляции - БЕЗ ограничений по времени
        while self.event_queue and self.running:
            # Извлекаем следующее событие
            event = heapq.heappop(self.event_queue)
            self.current_time = event.get_time()

            # Отображаем состояние ДО обработки события
            self.display_step_state(event)

            # Ждем команду пользователя
            try:
                user_input = input("\nНажмите Enter для обработки события или 'q' для выхода: ")
                if user_input.lower() == 'q':
                    self.running = False
                    break
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Ошибка ввода: {e}")
                self.running = False
                break

            # Обрабатываем событие
            event.process_event(self)

            # Обновляем общее время симуляции
            self.total_simulation_time = max(self.total_simulation_time, self.current_time)

        # Завершение симуляции
        self.running = False
        if not self.event_queue:
            print("\nСобытия закончились - симуляция завершена")

        # Финальное состояние
        self.display_step_state()
        self.generate_final_report()

        print("\n" + "=" * 100)
        print("СИМУЛЯЦИЯ ЗАВЕРШЕНА")
        print("=" * 100)

    def generate_final_report(self):
        """Генерирует итоговый отчет"""
        print("\n" + "=" * 100)
        print("ИТОГОВЫЙ ОТЧЕТ СИСТЕМЫ")
        print("=" * 100)

        stats = self.statistics
        gen_stats = self.patient_generator.get_generation_stats()

        # Итоговая таблица
        print("\nТАБЛИЦА 5 - ИТОГОВАЯ СТАТИСТИКА")
        print(f"{'Параметр':<25} {'Всего':<10} {'Неотложка':<12} {'По записи':<12} {'Без записи':<12}")
        print(f"{'-' * 71}")

        # Сгенерировано
        if gen_stats:
            print(f"{'Сгенерировано':<25} {gen_stats['total_generated']:<10} "
                  f"{gen_stats['emergency_count']:<12} {gen_stats['appointment_count']:<12} "
                  f"{gen_stats['walkin_count']:<12}")

        # Прибыло
        print(f"{'Прибыло':<25} {stats.total_patients_arrived:<10} "
              f"{stats.patients_by_priority[Priority.EMERGENCY]:<12} "
              f"{stats.patients_by_priority[Priority.BY_APPOINTMENT]:<12} "
              f"{stats.patients_by_priority[Priority.WITHOUT_APPOINTMENT]:<12}")

        # Обслужено
        print(f"{'Обслужено':<25} {stats.total_patients_served:<10} "
              f"{stats.served_by_priority[Priority.EMERGENCY]:<12} "
              f"{stats.served_by_priority[Priority.BY_APPOINTMENT]:<12} "
              f"{stats.served_by_priority[Priority.WITHOUT_APPOINTMENT]:<12}")

        # Отказы
        print(f"{'Отказов':<25} {stats.total_patients_rejected:<10} "
              f"{stats.rejected_by_priority[Priority.EMERGENCY]:<12} "
              f"{stats.rejected_by_priority[Priority.BY_APPOINTMENT]:<12} "
              f"{stats.rejected_by_priority[Priority.WITHOUT_APPOINTMENT]:<12}")

        # Проценты отказов
        print(f"{'% отказов':<25} ", end="")
        if stats.total_patients_arrived > 0:
            total_reject_pct = (stats.total_patients_rejected / stats.total_patients_arrived) * 100
            print(f"{total_reject_pct:<10.2f}", end="")
        else:
            print(f"{'0.00':<10}", end="")

        for priority in [Priority.EMERGENCY, Priority.BY_APPOINTMENT, Priority.WITHOUT_APPOINTMENT]:
            arrived = stats.patients_by_priority[priority]
            rejected = stats.rejected_by_priority[priority]
            if arrived > 0:
                reject_pct = (rejected / arrived) * 100
                print(f"{reject_pct:<12.2f}", end="")
            else:
                print(f"{'0.00':<12}", end="")
        print()

        print(f"{'-' * 71}")

        # Статистика по врачам
        print(f"\nСТАТИСТИКА ПО ВРАЧАМ:")
        print(f"{'Врач':<15} {'Принято пациентов':<20} {'% от общего':<15}")
        print(f"{'-' * 50}")

        # Распределение пациентов по врачам
        total_served = stats.total_patients_served
        if total_served > 0:
            patients_per_doctor = total_served // len(self.doctors)
            remainder = total_served % len(self.doctors)

            for i, doctor in enumerate(self.doctors):
                patients_served = patients_per_doctor
                if i < remainder:
                    patients_served += 1

                percentage = (patients_served / total_served) * 100
                print(f"{doctor.name:<15} {patients_served:<20} {percentage:<15.2f}%")
        else:
            for doctor in self.doctors:
                print(f"{doctor.name:<15} {0:<20} {0:<15.2f}%")

        print(f"\nОбщее время симуляции: {self.total_simulation_time:.2f} мин")
        print(f"Количество шагов: {self.step_count}")
        print("=" * 100)

    def get_system_state(self) -> dict:
        """Возвращает текущее состояние системы"""
        return {
            'current_time': self.current_time,
            'events_in_queue': len(self.event_queue),
            'doctors_state': [str(doctor) for doctor in self.doctors],
            'waiting_room_state': self.waiting_room.get_state_description(),
            'statistics': self.statistics.get_current_state()
        }

    def __str__(self) -> str:
        state = self.get_system_state()
        return (f"SimulationCore(time={self.current_time:.2f}, "
                f"events={state['events_in_queue']}, "
                f"doctors={len(self.doctors)}, "
                f"buffer={state['waiting_room_state']})")