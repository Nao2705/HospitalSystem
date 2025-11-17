import math
import random
from typing import Optional
from entities.patient import Patient
from utils.name_generator import NameGenerator
from config.settings import DISPLAY_SETTINGS


class Doctor:
    """Прибор - дежурный врач, экспоненциальный закон распределения времени обслуживания"""
    
    def __init__(self, doctor_id: int, mean_service_time: float):
        self.id = doctor_id
        self.name = NameGenerator.get_doctor_name(doctor_id)  # Фиксированное имя врача
        self.is_busy = False
        self.current_patient: Optional[Patient] = None
        self.mean_service_time = mean_service_time
    
    def get_id(self) -> int:
        return self.id
    
    def get_current_patient(self) -> Optional[Patient]:
        return self.current_patient
    
    def generate_service_time(self) -> float:
        """Генерирует время обслуживания по экспоненциальному закону"""
        u = random.random()
        u = max(0.000001, min(0.999999, u))  # Защита от 0 и 1
        service_time = -self.mean_service_time * math.log(1 - u)
        return max(service_time, DISPLAY_SETTINGS['min_service_time'])
    
    def start_service(self, patient: Patient, current_time: float) -> float:
        """Начинает обслуживание пациента"""
        if self.is_busy:
            raise Exception(f"Врач {self.name} уже занят!")
        
        self.is_busy = True
        self.current_patient = patient
        patient.service_start_time = current_time
        
        service_duration = self.generate_service_time()
        service_end_time = current_time + service_duration
        
        print(f"Врач {self.name} начал прием {patient.name} в {current_time:.2f}")
        print(f"Прием займет {service_duration:.2f}, закончится в {service_end_time:.2f}")
        
        return service_end_time
    
    def end_service(self, current_time: float) -> Patient:
        """Завершает обслуживание и возвращает пациента"""
        if not self.is_busy:
            raise Exception(f"Врач {self.name} не занят!")
        
        patient = self.current_patient
        patient.service_end_time = current_time
        
        self.is_busy = False
        self.current_patient = None
        
        print(f"Врач {self.name} завершил прием {patient.name} в {current_time:.2f}")
        
        return patient
    
    def __str__(self) -> str:
        status = "занят" if self.is_busy else "свободен"
        patient_info = f", принимает {self.current_patient.name}" if self.current_patient else ""
        return f"Врач {self.name} ({status}{patient_info})"