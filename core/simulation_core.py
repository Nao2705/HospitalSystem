import heapq
from typing import List
from entities.doctor import Doctor
from services.waiting_room import WaitingRoom
from services.dispatcher import Dispatcher
from services.statistics import Statistics
from core.patient_generator import PatientGenerator


class SimulationCore:
    """
    Главный класс управления имитационной моделью.
    Координирует все компоненты системы.
    """

    def __init__(self):
        self.current_time = 0.0
        self.event_queue = []
        self.doctors: List[Doctor] = []
        self.waiting_room: WaitingRoom = None
        self.dispatcher: Dispatcher = None
        self.patient_generator: PatientGenerator = None
        self.statistics: Statistics = None
        self.running = False

        # Счетчик для ID пациентов (дублируется в patient_generator для согласованности)
        self.next_patient_id = 1

    def initialize_system(self, num_doctors: int = 3, buffer_capacity: int = 5):
        """Инициализирует все компоненты системы"""
        print("ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ МАССОВОГО ОБСЛУЖИВАНИЯ")
        print("=" * 50)

        # 1. Создаем врачей
        self.doctors = []
        for i in range(1, num_doctors + 1):
            doctor = Doctor(
                doctor_id=i,
                mean_service_time=15.0  # Среднее время приема 15 минут
            )
            self.doctors.append(doctor)
            print(f"Создан врач: {doctor.name}")

        # 2. Создаем буфер ожидания
        self.waiting_room = WaitingRoom(capacity=buffer_capacity)
        print(f"Создан буфер ожидания на {buffer_capacity} мест")

        # 3. Создаем статистику
        self.statistics = Statistics()
        print("Система статистики инициализирована")

        # 4. Создаем диспетчер
        self.dispatcher = Dispatcher(
            doctors=self.doctors,
            waiting_room=self.waiting_room,
            simulation_core=self
        )
        print("Диспетчер инициализирован")

        # 5. Создаем генератор пациентов
        self.patient_generator = PatientGenerator(self)
        print("   👥 Генератор пациентов готов к работе")

        print("=" * 50)
        print("СИСТЕМА ГОТОВА К РАБОТЕ")
        print()

    def schedule_event(self, event):
        """Добавляет событие в приоритетную очередь"""
        heapq.heappush(self.event_queue, event)

    def schedule_next_arrival(self):
        """Планирует следующее прибытие пациента"""
        self.patient_generator.generate_next_arrival()

    def get_next_patient_id(self) -> int:
        """Возвращает следующий ID пациента и увеличивает счетчик"""
        patient_id = self.next_patient_id
        self.next_patient_id += 1
        return patient_id

    def find_doctor_by_id(self, doctor_id: int) -> Doctor:
        """Находит врача по ID"""
        for doctor in self.doctors:
            if doctor.id == doctor_id:
                return doctor
        return None

    def run(self, simulation_time: float):
        """
        Запускает симуляцию на указанное время
        """
        print(f"ЗАПУСК СИМУЛЯЦИИ НА {simulation_time} ЕДИНИЦ ВРЕМЕНИ")
        print("=" * 50)

        self.running = True

        # Запускаем генерацию пациентов
        self.patient_generator.start_generation()

        # Главный цикл симуляции
        while self.event_queue and self.current_time <= simulation_time:
            # Извлекаем следующее событие
            event = heapq.heappop(self.event_queue)
            self.current_time = event.get_time()

            if self.current_time > simulation_time:
                break

            # Обрабатываем событие
            event.process_event(self)

        # Завершение симуляции
        self.running = False
        print("\n" + "=" * 50)
        print("СИМУЛЯЦИЯ ЗАВЕРШЕНА")
        print("=" * 50)

    def get_system_state(self) -> dict:
        """Возвращает текущее состояние системы"""
        return {
            'current_time': self.current_time,
            'events_in_queue': len(self.event_queue),
            'doctors_state': [str(doctor) for doctor in self.doctors],
            'waiting_room_state': self.waiting_room.get_state_description(),
            'statistics': self.statistics.get_current_state()
        }

    def generate_final_report(self):
        """Генерирует итоговый отчет"""
        print("\nИТОГОВЫЙ ОТЧЕТ СИСТЕМЫ")
        print("=" * 50)

        # Отчет статистики
        stats_report = self.statistics.generate_report()
        for key, value in stats_report.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")

        # Статистика генерации
        gen_stats = self.patient_generator.get_generation_stats()
        if gen_stats:
            print(f"\nСТАТИСТИКА ГЕНЕРАЦИИ ПАЦИЕНТОВ:")
            print(f"   Всего сгенерировано: {gen_stats['total_generated']}")
            print(f"   Неотложная помощь: {gen_stats['emergency_count']} ({gen_stats['emergency_percent']:.1f}%)")
            print(f"   По записи: {gen_stats['appointment_count']} ({gen_stats['appointment_percent']:.1f}%)")
            print(f"   Без записи: {gen_stats['walkin_count']} ({gen_stats['walkin_percent']:.1f}%)")

        print("=" * 50)

    def __str__(self) -> str:
        state = self.get_system_state()
        return (f"SimulationCore(time={self.current_time:.2f}, "
                f"events={state['events_in_queue']}, "
                f"doctors={len(self.doctors)}, "
                f"buffer={state['waiting_room_state']})")