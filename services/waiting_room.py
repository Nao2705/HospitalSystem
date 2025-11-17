from typing import Optional, List
from entities.patient import Patient
from entities.priority import Priority


class WaitingRoom:
    """Буфер - зона ожидания для пациентов с реализацией Д1О32 и Д1О4"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.patients: List[Patient] = []  # Динамический список пациентов
        self.size = 0

    def is_full(self) -> bool:
        """Проверяет, полон ли буфер"""
        return self.size >= self.capacity

    def is_empty(self) -> bool:
        """Проверяет, пуст ли буфер"""
        return self.size == 0

    def get_total_patients(self) -> int:
        """Возвращает текущее количество пациентов в буфере"""
        return self.size

    def get_queue_info(self) -> List[Patient]:
        """Возвращает информацию об очереди"""
        return self.patients.copy()

    def add_patient(self, patient: Patient) -> tuple[bool, Optional[Patient]]:
        """
        Добавляет пациента в буфер по правилу Д1О32

        Returns:
            tuple[bool, Optional[Patient]]:
                - True если пациент добавлен, False если получен отказ
                - Вытесненный пациент (если был)
        """
        if self.is_full():
            # БУФЕР ПОЛОН - применяем Д1О4 (вытеснение самого свежего)
            rejected_patient = self._replace_last_patient(patient)
            return True, rejected_patient  # Новый пациент добавлен, старый вытеснен
        else:
            # Есть свободное место
            self._add_to_end(patient)
            return True, None  # Пациент добавлен, вытеснения не было

    def _replace_last_patient(self, patient: Patient) -> Patient:
        """Выполняет замену самого свежего пациента (Д1О4) и возвращает вытесненного"""
        if self.size == 0:
            raise Exception("Буфер пуст, но пытаемся вытеснить пациента!")

        # Находим самого "свежего" пациента (с наибольшим временем прибытия)
        latest_index = -1
        latest_arrival_time = -1.0

        for i, current_patient in enumerate(self.patients):
            if current_patient.arrival_time > latest_arrival_time:
                latest_arrival_time = current_patient.arrival_time
                latest_index = i

        if latest_index != -1:
            # Выбиваем самого свежего пациента
            rejected_patient = self.patients[latest_index]

            # Заменяем его новым пациентом
            self.patients[latest_index] = patient

            print(f"-- ВЫТЕСНЕНИЕ: Пациент {rejected_patient.name} (прибыл: {rejected_patient.arrival_time:.2f}) "
                  f"выбит из буфера, {patient.name} (прибыл: {patient.arrival_time:.2f}) занял его место")

            return rejected_patient

        raise Exception("Не удалось найти пациента для вытеснения!")

    def _add_to_end(self, patient: Patient) -> bool:
        """Добавляет пациента в конец буфера"""
        self.patients.append(patient)
        self.size += 1
        print(f"{patient.name} поставлен в буфер. Теперь в буфере: {self.size}/{self.capacity}")
        return True

    def get_next_patient(self) -> Optional[Patient]:
        """
        Выбирает следующего пациента для обслуживания по приоритету Д2Б4

        Return:
            Optional[Patient]: Пациент с наивысшим приоритетом или None
        """
        if self.is_empty():
            return None

        # Ищем пациента с максимальным приоритетом (минимальное значение Enum)
        selected_patient = None
        selected_index = -1
        highest_priority = Priority.WITHOUT_APPOINTMENT  # Начинаем с низшего

        for i, patient in enumerate(self.patients):
            # Сравниваем приоритеты (меньшее значение = высший приоритет)
            if patient.priority.value < highest_priority.value:
                highest_priority = patient.priority
                selected_patient = patient
                selected_index = i
            # Если приоритеты равны, выбираем того, кто раньше пришел
            elif (patient.priority == highest_priority and
                  selected_patient is not None and
                  patient.arrival_time < selected_patient.arrival_time):
                selected_patient = patient
                selected_index = i

        if selected_patient is not None and selected_index != -1:
            # Удаляем пациента из буфера
            self._remove_patient(selected_index)
            print(f"Выбран для приема: {selected_patient.name} "
                  f"(приоритет: {str(selected_patient.priority)}, прибыл: {selected_patient.arrival_time:.2f})")
            return selected_patient

        return None

    def _remove_patient(self, index: int) -> None:
        """Удаляет пациента по индексу"""
        if 0 <= index < len(self.patients):
            removed_patient = self.patients.pop(index)
            self.size -= 1
            print(f"Пациент {removed_patient.name} удален из буфера. Осталось: {self.size}/{self.capacity}")

    def get_state_description(self) -> str:
        """Возвращает текстовое описание текущего состояния буфера"""
        if self.is_empty():
            return "Буфер пуст"

        occupied_slots = []
        for i, patient in enumerate(self.patients):
            occupied_slots.append(f"{i + 1}: {patient.name} ({patient.priority}, прибыл: {patient.arrival_time:.2f})")

        return f"Буфер [{self.size}/{self.capacity}]: " + ", ".join(occupied_slots)

    def __str__(self) -> str:
        return self.get_state_description()