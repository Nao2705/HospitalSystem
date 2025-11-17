import sys
import argparse
from core.simulation_core import SimulationCore


def print_intro():
    intro_text = """
    Hospital System Simulator
====================================

ОПИСАНИЕ МОДЕЛИ:
- Источник: бесконечный (ИБ) с равномерным законом (И32)
- Приборы: врачи с экспоненциальным временем обслуживания (П31)
- Буферизация: со сдвигом заявок (Д1О32)
- Отказ: последняя поступившая заявка (Д1О4)
- Выбор приоритета: по номеру источника (Д2Б4)
- Выбор врача: по кольцу (Д2П2)

ТИПЫ ПАЦИЕНТОВ:
1. Неотложная помощь (высший приоритет) - 15%
2. По записи (средний приоритет) - 45%
3. Без записи (низший приоритет) - 40%

РЕЖИМ РАБОТЫ:
- ТОЛЬКО ПОШАГОВЫЙ РЕЖИМ: подробное отображение каждого события
- Введите любой символ для перехода к следующему шагу
- Введите 'q' для выхода и просмотра итоговой статистики
"""
    print(intro_text)


def run_simulation(num_doctors: int, buffer_capacity: int, mean_service_time: float):
    """Запускает симуляцию с заданными параметрами БЕЗ ограничения по времени"""
    print(f"ЗАПУСК СИМУЛЯЦИИ С ПАРАМЕТРАМИ:")
    print(f" - Количество врачей: {num_doctors}")
    print(f" - Вместимость буфера: {buffer_capacity}")
    print(f" - Среднее время приема: {mean_service_time} мин")
    print(f" - Режим: ПОШАГОВЫЙ (без ограничения времени)")
    print()

    try:
        # Создаем и инициализируем систему
        simulation = SimulationCore()
        simulation.initialize_system(num_doctors=num_doctors, buffer_capacity=buffer_capacity)

        # Настраиваем среднее время обслуживания врачей
        for doctor in simulation.doctors:
            doctor.mean_service_time = mean_service_time

        # Запускаем симуляцию (БЕЗ ограничения по времени)
        simulation.run()

        return simulation

    except Exception as e:
        print(f"!!! ОШИБКА ПРИ ЗАПУСКЕ СИМУЛЯЦИИ: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Основная функция приложения"""
    parser = argparse.ArgumentParser(
        description="Имитационная модель системы массового обслуживания больницы (только пошаговый режим)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-d', '--doctors',
        type=int,
        default=3,
        help="Количество врачей"
    )

    parser.add_argument(
        '-b', '--buffer',
        type=int,
        default=2,
        help="Вместимость буфера ожидания"
    )

    parser.add_argument(
        '-s', '--service-time',
        type=float,
        default=35.0,
        help="Среднее время приема у врача в минутах"
    )

    parser.add_argument(
        '--no-welcome',
        action='store_true',
        help="Не показывать приветственное сообщение"
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

    if args.service_time <= 0:
        print("Ошибка: Среднее время приема должно быть положительным числом")
        sys.exit(1)


    if not args.no_welcome:
        print_intro()


    simulation = run_simulation(
        num_doctors=args.doctors,
        buffer_capacity=args.buffer,
        mean_service_time=args.service_time
    )

    # Завершаем работу
    if simulation:
        print("\nСИМУЛЯЦИЯ УСПЕШНО ЗАВЕРШЕНА")
    else:
        print("\nСИМУЛЯЦИЯ ЗАВЕРШИЛАСЬ С ОШИБКАМИ")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nСИМУЛЯЦИЯ ПРЕРВАНА ПОЛЬЗОВАТЕЛЕМ")
    except Exception as e:
        print(f"\nНЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

