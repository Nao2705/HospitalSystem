
"""Здесь задаем параметры системы массового обслуживания больницы."""

# Настройки генерации пациентов
PATIENT_GENERATION_SETTINGS = {
    'EMERGENCY': {
        'min_interval': 45.0,  # 45-120 минут между неотложками
        'max_interval': 120.0,
        'probability': 0.15,  # 15% - неотложные случаи
        'description': 'Неотложная помощь'
    },
    'BY_APPOINTMENT': {
        'min_interval': 10.0,  # 10-25 минут между записями
        'max_interval': 25.0,
        'probability': 0.45,  # 45% - по записи (основной поток)
        'description': 'По записи'
    },
    'WITHOUT_APPOINTMENT': {
        'min_interval': 5.0,  # 5-15 минут между без записи
        'max_interval': 15.0,
        'probability': 0.40,  # 40% - без записи
        'description': 'Без записи'
    }
}


DEFAULT_NUM_DOCTORS = 3
DEFAULT_BUFFER_CAPACITY = 5
DEFAULT_MEAN_SERVICE_TIME = 15.0

# Настройки отображения
DISPLAY_SETTINGS = {
    'table_width': 100,
    'max_events_display': 8,
    'min_service_time': 0.5  # Минимальное время обслуживания
}

# Настройки статистики
STATISTICS_SETTINGS = {
    'confidence_t_alpha': 1.643,  # для α=0.9
    'relative_accuracy_delta': 0.1,  # относительная точность 10%
    'min_patients_for_accuracy': 100
}

# Соответствие source_id и приоритетов
SOURCE_ID_MAPPING = {
    1: 'EMERGENCY',
    2: 'BY_APPOINTMENT',
    3: 'WITHOUT_APPOINTMENT'
}

# Описания для отображения
DISPLAY_DESCRIPTIONS = {
    'sources': {
        1: "Неотложка",
        2: "По записи",
        3: "Без записи"
    },
    'statuses': {
        'free': "СВОБОДЕН",
        'busy': "ЗАНЯТ"
    }
}