from typing import List, Optional
from entities.doctor import Doctor
from entities.patient import Patient
from services.waiting_room import WaitingRoom
from events.service_end_event import ServiceEndEvent


class Dispatcher:
    """Диспетчер - связующее звено между пациентами, буфером и врачами"""

    def __init__(self, doctors: List[Doctor], waiting_room: WaitingRoom, simulation_core):
        self.doctors = doctors
        self.waiting_room = waiting_room
        self.simulation_core = simulation_core
        self.next_doctor_index = 0  # для кольцевого выбора (Д2П2)

    def on_patient_arrival(self, patient: Patient, current_time: float) -> bool:
        """Обработка новоприбывшего пациента"""
        print(f"Время {current_time:.2f}: Прибыл {patient} (приоритет: {patient.priority})")

        # Пытаемся добавить пациента в буфер
        success, rejected_patient = self.waiting_room.add_patient(patient)

        if success:
            if rejected_patient is None:
                # Пациент добавлен БЕЗ вытеснения
                print(f"{patient.name} направлен в зону ожидания")
            else:
                # Пациент добавлен с вытеснением - регистрируем отказ для вытесненного
                print(f"!!! {patient.name} вытеснил {rejected_patient.name} из буфера")
                self.simulation_core.statistics.record_patient_rejection(rejected_patient)

            # После добавления в буфер пытаемся сразу назначить на обслуживание
            self._try_assign_patient_from_buffer(current_time)
            return True
        else:
            # Доп обработка - по логике не должно произойти
            print(f"!!! КРИТИЧЕСКАЯ ОШИБКА: {patient.name} не удалось добавить в буфер")
            self.simulation_core.statistics.record_patient_rejection(patient)
            return False

    def on_doctor_became_free(self, doctor_id: int, current_time: float) -> None:
        """Вызывается когда врач освободился"""
        print(f"Время {current_time:.2f}: Врач {doctor_id} освободился")
        self._try_assign_patient_from_buffer(current_time)

    def _try_assign_patient_from_buffer(self, current_time: float) -> None:
        """Пытается назначить пациента из буфера свободному врачу.
        Выбирает пациента по высшему приоритету и врача по Д2П2 (кольцевой)."""
        # Ищем свободного врача
        free_doctor = self._find_free_doctor()
        if free_doctor is None:
            print("Нет свободных врачей - пациенты продолжают ждать")
            return

        # Выбираем пациента с высшим приоритетом из буфера
        next_patient = self.waiting_room.get_next_patient()
        if next_patient is None:
            print("В зоне ожидания нет пациентов")
            return

        # Назначаем пациента врачу
        try:
            service_end_time = free_doctor.start_service(next_patient, current_time)

            # Регистрируем начало обслуживания в статистике
            self.simulation_core.statistics.record_service_start(next_patient)

            # Создаем событие окончания обслуживания
            service_end_event = ServiceEndEvent(
                time=service_end_time,
                doctor_id=free_doctor.id,
                patient_id=next_patient.id
            )
            self.simulation_core.schedule_event(service_end_event)

            print(f"Назначен {next_patient.name} врачу {free_doctor.name}")

        except Exception as e:
            print(f"!!! Ошибка при назначении пациента: {e}")
            # Если не удалось назначить, возвращаем пациента в буфер
            self.waiting_room.add_patient(next_patient)

    def _find_free_doctor(self) -> Optional[Doctor]:
        """Находит свободного врача по кольцевому алгоритму"""
        if not self.doctors:
            return None

        # Проверяем врачей начиная с next_doctor_index по кругу
        for i in range(len(self.doctors)):
            doctor_index = (self.next_doctor_index + i) % len(self.doctors)
            doctor = self.doctors[doctor_index]

            # ИСПРАВЛЕНИЕ: используем свойство is_busy вместо метода get_is_busy()
            if not doctor.is_busy:
                # Обновляем индекс для следующего выбора
                self.next_doctor_index = (doctor_index + 1) % len(self.doctors)
                return doctor

        return None  # все врачи заняты

    def get_system_state(self) -> dict:
        """Возвращает текущее состояние системы"""
        free_doctors = [d for d in self.doctors if not d.is_busy]
        busy_doctors = [d for d in self.doctors if d.is_busy]

        return {
            'free_doctors': len(free_doctors),
            'busy_doctors': len(busy_doctors),
            'patients_in_buffer': self.waiting_room.get_total_patients(),
            'buffer_capacity': self.waiting_room.capacity,
            'next_doctor_index': self.next_doctor_index,
            'free_doctors_list': [f"{d.name} (ID: {d.id})" for d in free_doctors],
            'busy_doctors_list': [f"{d.name} с {d.current_patient.name}" for d in busy_doctors if d.current_patient]
        }

    def __str__(self) -> str:
        state = self.get_system_state()
        return (f"Диспетчер: {state['free_doctors']}/{len(self.doctors)} врачей свободно, "
                f"{state['patients_in_buffer']}/{state['buffer_capacity']} в буфере")