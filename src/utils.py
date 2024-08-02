import os
import logging
import logging.handlers
import datetime
import pandas as pd
import json
from config import AREAS_DIR, DATA_DIR, LOGS_DIR

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional


class CustomFormatter(logging.Formatter):

    """
    ## Кастомный формат логгера
    """

    LEVEL_COLORS = [
        (logging.DEBUG, '\x1b[32;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31;1m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]
    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {color}%(levelname)-10s\x1b[0m \x1b[35m%(name)s\x1b[0m -> %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        for level, color in LEVEL_COLORS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Переопределите функцию обратной трассировки, чтобы она всегда печаталась красным цветом
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Удаление слоя кэша
        record.exc_text = None
        return output


def setup_logger(module_name:str) -> logging.Logger:
    """
    ### Настройка логгера

    ----------------
    * Аргументы:
        * module_name (str): Имя модуля.

    ----------------
    * Возвращается:
        * logging.Logger: Логгер.
    """
    # Cоздание логгера
    library, _, _ = module_name.partition('.py')
    logger = logging.getLogger(library)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)

        # Укажите название к журналу в папке logs
        log_name = f'{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
        log_path = os.path.join(LOGS_DIR, log_name)
        # Создайте обработчик файлов с обычным форматером (без ANSI)
        log_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=2,
        )
        log_handler.setFormatter(logging.Formatter(  # Используйте форматер по умолчанию
            '%(asctime)s %(levelname)-8s %(name)s -> %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))

        # Добавляем обработчики в логгер
        logger.addHandler(log_handler)

    return logger

def format_date(input_string: str) -> str:
    """
    ### Преобразует дату в формате "XXXX-XX-XXTXX:XX:XX+XXXX" в "XX.XX.XXXX XX:XX:XX" (YYYY-MM-DD HH:MM:SS).

    ----------------
    * Аргументы:
        * input_string (str): Дата в формате "XXXX-XX-XXTXX:XX:XX+XXXX".

    ----------------
    * Возвращается:
        * str: Дата в формате "XX.XX.XXXX XX:XX:XX" (YYYY-MM-DD HH:MM:SS)"".
    """
    return input_string[8:10] + "." + input_string[5:7] + "." + input_string[0:4] + " " + input_string[11:19]

def find_city(data: List[Dict], city_name: str) -> Optional[int]:
    """
    Функция для поиска города по названию

    ----------------
    * Аргументы:
        * data (List[Dict]): Список словарей, содержащих информацию о городах и регионах
        * city_name (str): Название города
    
    ----------------
    * Возвращается:
        * Optional[int]: ID города, если найден, иначе None
    """
    for item in data:
        if item['name'].lower() == city_name.lower():
            return item['id']
        if item['areas']:
            result = find_city(item['areas'], city_name)
            if result is not None:
                return result
    return None

def get_integer_input(prompt: str) -> int:
    """
    ### Возвращает целое число, введенное пользователем

    ----------------
    * Аргументы:
        * prompt (str): Подсказка для ввода

    ----------------
    * Возвращается:
        * int: Целое число
    """
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            return 0

def filter_jobs_by_salary_range(jobs: List[Dict], salary_input: str) -> Optional[List[Dict]]:
    """
    ### Фильтрует вакансии по заданному диапазону зарплат или по одному значению.

    ----------------
    * Аргументы:
        * jobs (List[Job]): Список объектов вакансий
        * salary_input (str): Заданный диапазон зарплат
    
    ----------------
    * Возвращается:
        * Optional[List[Job]]: Список вакансий, удовлетворяющих заданному диапазону зарплат 
        или по одному значению (если ввод был одним числом). 
    """
    try:
        # Удаляем пробелы и разделяем по дефису
        salary_parts = list(map(int, salary_input.replace(' ', '').split('-')))
        
        # Если введено одно значение, устанавливаем его как максимальную зарплату, минимальная = 0
        if len(salary_parts) == 1:
            min_salary = 0
            max_salary = salary_parts[0]
        elif len(salary_parts) == 2:
            min_salary, max_salary = salary_parts
        else:
            raise ValueError("Некорректный ввод диапазона зарплат")
    except ValueError:
        print("Некорректный формат диапазона зарплат. Пожалуйста, используйте формат 'мин - макс' или одно значение.")
        return None

    filtered_jobs = []
    for job in jobs:
        salary_target = job["salary"]["to"] or job["salary"]["from"]
        if min_salary <= salary_target <= max_salary:
            filtered_jobs.append(job)
        
    return filtered_jobs

class FileWorker(ABC):
    def __init__(self, file_name: str):
        self.file_name = file_name

    @abstractmethod
    def save_data(self, data: List[Dict]) -> None:
        pass
    
    @abstractmethod
    def load_data(self) -> List[Dict]:
        pass

class JSONFileWorker(FileWorker):


    def save_data(self, data: List[Dict], directory: str = DATA_DIR) -> None:
        """
        Сохраняет данные в JSON-файл
        
        ----------------
        * Аргументы:
            * data (List[Dict]): Список словарей, содержащих информацию о вакансиях
            * directory (str): Путь к директории
        
        ----------------
        * Возвращается:
            * None
        """
        with open(os.path.join(directory, self.file_name + '.json'), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    
    def load_data(self, directory: str = DATA_DIR) -> List[Dict]:
        """
        Загружает данные из JSON-файла

        ----------------
        * Аргументы:
            * directory (str): Путь к директории
        
        ----------------
        * Возвращается:
            * List[Dict]: Список словарей, содержащих информацию о вакансиях
        """
        with open(os.path.join(directory, self.file_name + '.json'), 'r', encoding='utf-8') as file:
            return json.load(file)

class ExcelFileWorker(FileWorker):


    def save_data(self, data: List[Dict], directory: str = DATA_DIR) -> None:
        """
        Сохраняет данные в Excel-файл
        
        ----------------
        * Аргументы:
            * data (List[Dict]): Список словарей, содержащих информацию о вакансиях
            * directory (str): Путь к директории
        
        ----------------
        * Возвращается:
            * None
        """
        df = pd.DataFrame(data)
        df.to_excel(os.path.join(directory, self.file_name + '.xlsx'), index=False)
        

    
    def load_data(self, directory: str = DATA_DIR) -> List[Dict]:
        """
        Загружает данные из Excel-файла

        ----------------
        * Аргументы:
            * directory (str): Путь к директории
        
        ----------------
        * Возвращается:
            * List[Dict]: Список словарей, содержащих информацию о вакансиях
        """
        return pd.read_excel(os.path.join(directory, self.file_name + '.xlsx')).to_dict(orient='records')

class CSVFileWorker(FileWorker):

    def save_data(self, data: List[Dict], directory: str = DATA_DIR) -> None:
        """
        Сохраняет данные в CSV-файл

        ----------------
        * Аргументы:
            * data (List[Dict]): Список словарей, содержащих информацию о вакансиях
            * directory (str): Путь к директории
        
        ----------------
        * Возвращается:
            * None
        """
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(directory, self.file_name + '.csv'), index=False)

    
    def load_data(self, directory: str = DATA_DIR) -> List[Dict]:
        """
        Загружает данные из CSV-файла

        ----------------
        * Аргументы:
            * directory (str): Путь к директории

        ----------------
        * Возвращается:
            * List[Dict]: Список словарей, содержащих информацию о вакансиях
        """
        return pd.read_csv(os.path.join(directory, self.file_name + '.csv')).to_dict(orient='records')

class TextFileWorker(FileWorker):

    
    def save_data(self, data: List[Dict], directory: str = DATA_DIR) -> None:
        """
        Сохраняет данные в текстовый файл

        ----------------
        * Аргументы:
            * data (List[Dict]): Список словарей, содержащих информацию о вакансиях
            * directory (str): Путь к директории

        ----------------
        * Возвращается:
            * None
        """
        with open(os.path.join(directory, self.file_name + '.txt'), 'w', encoding='utf-8') as file:
            for item in data:
                file.write(json.dumps(item, ensure_ascii=False) + '\n')
    
            
    def load_data(self, directory: str = DATA_DIR) -> List[Dict]:
        """
        Загружает данные из текстового файла

        ----------------
        * Аргументы:
            * directory (str): Путь к директории

        ----------------
        * Возвращается:
            * List[Dict]: Список словарей, содержащих информацию о вакансиях
        """
        with open(os.path.join(directory, self.file_name + '.txt'), 'r', encoding='utf-8') as file:
            return [json.loads(line) for line in file]
        
class AreaFileWorker():
    def __init__(self):
        self.file_path = AREAS_DIR
        
    def load_data(self) -> List[Dict]:
        """
        Загружает данные город из HH JSON-файла

        ----------------
        * Аргументы:
            * None

        ----------------
        * Возвращается:
            * List[Dict]: Список словарей, содержащих информацию о городах и регионах
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

