from typing import Optional, List
from entities.patient import Patient
from entities.priority import Priority


class WaitingRoom:
    """Буфер - зона ожидания для пациентов с реализацией Д1О32 и Д1О4"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.patients: List[Optional[Patient]] = [None] * capacity
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

    def get_queue_info(self) -> List[Optional[Patient]]:
        """Возвращает информацию об очереди"""
        return self.patients.copy()

    def add_patient(self, patient: Patient) -> bool:
        """
        Добавляет пациента в буфер по правилу Д1О32

        Returns:
            bool: True если пациент добавлен, False если получен отказ
        """
        if self.is_full():
            return self._replace_last_patient(patient)
        else:
            return self._add_to_first_free(patient)

    def _replace_last_patient(self, patient: Patient) -> bool:
        """
        Д1О4 - выбивает последнюю заявку и ставит новую

        Returns:
            bool: True если замена произошла
        """
        if self.size == 0:
            return False

        # Находим самого "свежего" пациента (с максимальным временем прихода)
        last_index = -1
        latest_arrival_time = -1.0

        for i in range(self.capacity):
            if self.patients[i] is not None:
                if self.patients[i].arrival_time > latest_arrival_time:
                    latest_arrival_time = self.patients[i].arrival_time
                    last_index = i

        if last_index != -1:
            # Выбиваем последнего пациента
            rejected_patient = self.patients[last_index]
            self.patients[last_index] = patient

            print(f"Пациент {rejected_patient.name} выбит из буфера, "
                  f"{patient.name} занял место {last_index + 1}")

            # Возвращаем True - пациент добавлен (хоть и с вытеснением)
            return True

        return False

    def _add_to_first_free(self, patient: Patient) -> bool:
        """Добавляет пациента в первое свободное место (Д1О32)"""
        for i in range(self.capacity):
            if self.patients[i] is None:
                self.patients[i] = patient
                self.size += 1
                print(f"{patient.name} поставлен в буфер на место {i + 1}")
                return True
        return False

    def get_next_patient(self) -> Optional[Patient]:
        """
        Выбирает следующего пациента для обслуживания по приоритету Д2Б4

        Returns:
            Optional[Patient]: Пациент с наивысшим приоритетом или None
        """
        if self.is_empty():
            return None

        # Ищем пациента с максимальным приоритетом (минимальное значение Enum)
        selected_patient = None
        selected_index = -1
        highest_priority = Priority.WITHOUT_APPOINTMENT  # Начинаем с низшего

        for i in range(self.capacity):
            if self.patients[i] is not None:
                patient = self.patients[i]
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
            # Удаляем пациента и сдвигаем очередь
            self._remove_and_shift(selected_index)
            print(f"Выбран для приема: {selected_patient.name} "
                  f"(приоритет: {selected_patient.priority})")
            return selected_patient

        return None

    def _remove_and_shift(self, index: int) -> None:
        """
        Д1О32 - удаляет пациента и сдвигает остальных
        """
        if index < 0 or index >= self.capacity or self.patients[index] is None:
            return

        # Сдвигаем всех пациентов справа на одну позицию влево
        for i in range(index, self.capacity - 1):
            self.patients[i] = self.patients[i + 1]

        # Последнее место становится пустым
        self.patients[self.capacity - 1] = None
        self.size -= 1

    def get_state_description(self) -> str:
        """Возвращает текстовое описание текущего состояния буфера"""
        if self.is_empty():
            return "Буфер пуст"

        occupied_slots = []
        for i in range(self.capacity):
            if self.patients[i] is not None:
                patient = self.patients[i]
                occupied_slots.append(f"{i + 1}: {patient.name} ({patient.priority})")

        return f"Буфер [{self.size}/{self.capacity}]: " + ", ".join(occupied_slots)

    def __str__(self) -> str:
        return self.get_state_description()