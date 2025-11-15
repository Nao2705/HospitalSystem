"""
Главный файл для запуска имитационной модели системы массового обслуживания больницы.

Архитектура программных систем - Вариант 8
Система моделирует работу приемного отделения клиники с:
- Разными приоритетами пациентов (неотложная помощь, по записи, без записи)
- Буферизацией с вытеснением (Д1О32, Д1О4)
- Приоритетным обслуживанием (Д2Б4, Д2П2)
- Экспоненциальным временем обслуживания (П31)
"""

import sys
import argparse
from core.simulation_core import SimulationCore


def print_welcome():
    """Выводит приветственное сообщение и описание системы"""
    welcome_text = """
    СИМУЛЯЦИОННАЯ МОДЕЛЬ ПОЛИКЛИНИКИ
    ====================================

    Архитектура программных систем - Вариант 8

    ОПИСАНИЕ СИСТЕМЫ:
    • Источник: бесконечный (ИБ) с равномерным законом (И32)
    • Приборы: врачи с экспоненциальным временем обслуживания (П31)
    • Буферизация: со сдвигом заявок (Д1О32)
    • Отказ: последняя поступившая заявка (Д1О4)
    • Выбор приоритета: по номеру источника (Д2Б4)
    • Выбор врача: по кольцу (Д2П2)

    ТИПЫ ПАЦИЕНТОВ:
    1. Неотложная помощь (высший приоритет) - 15%
    2. По записи (средний приоритет) - 45%  
    3. Без записи (низший приоритет) - 40%
    """
    print(welcome_text)


def run_simulation(num_doctors: int, buffer_capacity: int, simulation_time: float, mean_service_time: float):
    """
    Запускает симуляцию с заданными параметрами

    Args:
        num_doctors: Количество врачей
        buffer_capacity: Вместимость буфера ожидания
        simulation_time: Время симуляции в минутах
        mean_service_time: Среднее время приема у врача
    """
    print(f"ЗАПУСК СИМУЛЯЦИИ С ПАРАМЕТРАМИ:")
    print(f"   • Количество врачей: {num_doctors}")
    print(f"   • Вместимость буфера: {buffer_capacity}")
    print(f"   • Время симуляции: {simulation_time} мин")
    print(f"   • Среднее время приема: {mean_service_time} мин")
    print()

    try:
        # Создаем и инициализируем систему
        simulation = SimulationCore()

        # Настраиваем врачей с заданным средним временем обслуживания
        simulation.doctors = []
        for i in range(1, num_doctors + 1):
            from entities.doctor import Doctor
            doctor = Doctor(
                doctor_id=i,
                mean_service_time=mean_service_time
            )
            simulation.doctors.append(doctor)

        # Создаем остальные компоненты
        from services.waiting_room import WaitingRoom
        from services.dispatcher import Dispatcher
        from services.statistics import Statistics
        from core.patient_generator import PatientGenerator

        simulation.waiting_room = WaitingRoom(capacity=buffer_capacity)
        simulation.statistics = Statistics()
        simulation.dispatcher = Dispatcher(
            doctors=simulation.doctors,
            waiting_room=simulation.waiting_room,
            simulation_core=simulation
        )
        simulation.patient_generator = PatientGenerator(simulation)

        # Запускаем симуляцию
        simulation.run(simulation_time)

        # Выводим итоговый отчет
        simulation.generate_final_report()

        return simulation

    except Exception as e:
        print(f"ОШИБКА ПРИ ЗАПУСКЕ СИМУЛЯЦИИ: {e}")
        return None


def main():
    """Основная функция приложения"""
    parser = argparse.ArgumentParser(
        description='Имитационная модель системы массового обслуживания больницы',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-d', '--doctors',
        type=int,
        default=3,
        help='Количество врачей (по умолчанию: 3)'
    )

    parser.add_argument(
        '-b', '--buffer',
        type=int,
        default=5,
        help='Вместимость буфера ожидания (по умолчанию: 5)'
    )

    parser.add_argument(
        '-t', '--time',
        type=float,
        default=480.0,
        help='Время симуляции в минутах (по умолчанию: 480 - 8 часов)'
    )

    parser.add_argument(
        '-s', '--service-time',
        type=float,
        default=15.0,
        help='Среднее время приема у врача в минутах (по умолчанию: 15)'
    )

    parser.add_argument(
        '--no-welcome',
        action='store_true',
        help='Не показывать приветственное сообщение'
    )

    # Парсим аргументы командной строки
    args = parser.parse_args()

    # Проверяем валидность параметров
    if args.doctors <= 0:
        print("Ошибка: Количество врачей должно быть положительным числом")
        sys.exit(1)

    if args.buffer <= 0:
        print("Ошибка: Вместимость буфера должна быть положительным числом")
        sys.exit(1)

    if args.time <= 0:
        print("Ошибка: Время симуляции должно быть положительным числом")
        sys.exit(1)

    if args.service_time <= 0:
        print("Ошибка: Среднее время приема должно быть положительным числом")
        sys.exit(1)

    # Выводим приветственное сообщение
    if not args.no_welcome:
        print_welcome()

    # Запускаем симуляцию
    simulation = run_simulation(
        num_doctors=args.doctors,
        buffer_capacity=args.buffer,
        simulation_time=args.time,
        mean_service_time=args.service_time
    )

    # Завершаем работу
    if simulation:
        print("\nСИМУЛЯЦИЯ УСПЕШНО ЗАВЕРШЕНА")
    else:
        print("\nСИМУЛЯЦИЯ ЗАВЕРШИЛАСЬ С ОШИБКАМИ")
        sys.exit(1)


def quick_start():
    """
    Функция для быстрого запуска с параметрами по умолчанию
    Полезно для тестирования и отладки
    """
    print("БЫСТРЫЙ СТАРТ С ПАРАМЕТРАМИ ПО УМОЛЧАНИЮ")
    print("=" * 50)

    simulation = run_simulation(
        num_doctors=3,
        buffer_capacity=5,
        simulation_time=120.0,  # 2 часа для быстрого теста
        mean_service_time=15.0
    )

    return simulation


if __name__ == "__main__":
    # Если запускается напрямую, а не как модуль
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹СИМУЛЯЦИЯ ПРЕРВАНА ПОЛЬЗОВАТЕЛЕМ")
    except Exception as e:
        print(f"\nНЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
        sys.exit(1)