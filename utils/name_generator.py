import random
from typing import List


class NameGenerator:
    """Универсальный генератор имен для пациентов и врачей"""

    # Базы данных имен
    MALE_FIRST_NAMES = [
        "Александр", "Алексей", "Андрей", "Артем", "Борис", "Вадим", "Василий", "Виктор",
        "Владимир", "Вячеслав", "Геннадий", "Георгий", "Дмитрий", "Евгений", "Иван",
        "Игорь", "Кирилл", "Константин", "Максим", "Михаил", "Никита", "Николай",
        "Олег", "Павел", "Петр", "Роман", "Сергей", "Станислав", "Степан", "Юрий"
    ]

    FEMALE_FIRST_NAMES = [
        "Александра", "Алина", "Анастасия", "Ангелина", "Анна", "Валентина", "Валерия",
        "Вера", "Вероника", "Виктория", "Галина", "Дарья", "Евгения", "Екатерина",
        "Елена", "Ирина", "Ксения", "Лариса", "Любовь", "Людмила", "Марина", "Мария",
        "Надежда", "Наталья", "Оксана", "Ольга", "Полина", "Светлана", "София", "Татьяна"
    ]

    LAST_NAMES = [
        "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев",
        "Михайлов", "Новиков", "Федоров", "Морозов", "Волков", "Алексеев", "Лебедев",
        "Семенов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев", "Орлов",
        "Андреев", "Макаров", "Никитин", "Захаров"
    ]

    # Фиксированные имена врачей (приборов)
    DOCTOR_NAMES = [
        "Иванов А.С.",
        "Петрова М.И.",
        "Сидоров В.К.",
        "Козлова Е.П.",
        "Васильев Д.Н."
    ]

    FEMALE_SUFFIXES = {
        'ов': 'ова', 'ев': 'ева', 'ин': 'ина', 'ский': 'ская', 'ой': 'ая'
    }

    @classmethod
    def generate_patient_name(cls) -> str:
        """Генерирует случайное имя для пациента"""
        # Случайно выбираем пол
        is_female = random.choice([True, False])

        if is_female:
            first_name = random.choice(cls.FEMALE_FIRST_NAMES)
        else:
            first_name = random.choice(cls.MALE_FIRST_NAMES)

        last_name = random.choice(cls.LAST_NAMES)

        # Склоняем фамилию для женщин
        if is_female:
            last_name = cls._make_female_last_name(last_name)

        return f"{last_name} {first_name}"

    @classmethod
    def get_doctor_name(cls, doctor_id: int) -> str:
        """
        Возвращает фиксированное имя врача по ID.
        Если ID превышает количество имен, используется запасной вариант.
        """
        if 1 <= doctor_id <= len(cls.DOCTOR_NAMES):
            return cls.DOCTOR_NAMES[doctor_id - 1]
        else:
            return f"Врач #{doctor_id}"

    @classmethod
    def get_available_doctors_count(cls) -> int:
        """Возвращает количество доступных фиксированных имен врачей"""
        return len(cls.DOCTOR_NAMES)

    @classmethod
    def _make_female_last_name(cls, last_name: str) -> str:
        """Склоняет фамилию для женского рода"""
        for male_suffix, female_suffix in cls.FEMALE_SUFFIXES.items():
            if last_name.endswith(male_suffix):
                return last_name[:-len(male_suffix)] + female_suffix
        return last_name + "а"  # fallback