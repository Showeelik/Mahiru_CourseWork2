from abc import ABC, abstractmethod
from typing import List
from src.api.hh_api import JobAPI
from src.models.job import Job
from src.utils import AreaFileWorker, JSONFileWorker, CSVFileWorker, ExcelFileWorker, TextFileWorker
from src.utils import find_city


class Interaction(ABC):
    @abstractmethod
    def interact(self):
        pass

class SearchInteraction(Interaction):
    def __init__(self, api: JobAPI):
        self.api = api

    def interact(self) -> List[dict]:
        area = input("Выберите регион: ")

        city_id = find_city(AreaFileWorker().load_data(), area)
        query = input("Введите поисковый запрос: ")

        jobs_data = self.api.load_vacancies(query, area=city_id)
        return jobs_data

class UserInteraction(Interaction):
    def __init__(self, storage: list):
        self.storage = storage

    def interact(self):
        print("Получить топ N вакансий по зарплате")

        N = int(input("Введите количество вакансий: "))
        

        jobs = [Job(**job_data) for job_data in self.storage]
        top_jobs = sorted(jobs, reverse=True)[:N]

        for job in top_jobs:
            print(job)
        
        input("Для продолжения нажмите Enter\n")

        FileInteraction(top_jobs).interact()


class FileInteraction(Interaction):
    def __init__(self, data: List[Job]):
        self.data = data
        self.jobs = [job.to_dict() for job in self.data]
        self.file_name = "vacancies"
        self.file_dir = None
        self.storage = JSONFileWorker(self.file_name)

    def interact(self):
        while True:
            
            choice = input("Cохранить вакансию в файл? (Y/N) ")
            
            if choice == "N":
                break

            elif choice == "Y":
                while True:
                    print("1. Название файла (не обязательно, по умолчанию: vacancies).")
                    print("2. Выбрать формат файла (не обязательно, по умолчанию: JSON).")
                    print("3. Путь сохранения файла (не обязательно, по умолчанию в директорий data).")
                    print("4. Продолжить")
                    print("5. Назад")
                    choice = input("Выберите опцию: ")

                    if choice == "1":
                        self.file_name = input("Название файла: ")

                    elif choice == "2":
                        while True:
                            print("1. JSON (по умолчанию)")
                            print("2. CSV")
                            print("3. EXCEL")
                            print("4. TXT")
                            print("5. Назад")

                            choice = input("Выберите опцию: ")

                            if choice == "1":
                                self.storage = JSONFileWorker(self.file_name)
                                self.jobs = [job.to_json() for job in self.data]
                                break

                            elif choice == "2":
                                self.storage = CSVFileWorker(self.file_name)
                                self.jobs = [job.to_dict() for job in self.data]
                                break

                            elif choice == "3":
                                self.storage = ExcelFileWorker(self.file_name)
                                self.jobs = [job.to_dict() for job in self.data]
                                break

                            elif choice == "4":
                                self.storage = TextFileWorker(self.file_name)
                                self.jobs = [job.to_dict() for job in self.data]
                                break

                            elif choice == "5":
                                break

                            else:
                                print("Неверный выбор, попробуйте еще раз.")

                    elif choice == "3":
                        self.file_dir = input("Путь сохранения файла (Полный путь, пример: C:/Users/User/Downloads): ")

                    elif choice == "4":
                        if self.file_dir:
                            self.storage.save_data(self.jobs, self.file_dir)
                        else:
                            self.storage.save_data(self.jobs)

                        print(f"Ваканси{'я' if len(self.jobs) == 1 else 'и'} добавлен{'а' if len(self.jobs) == 1 else 'ы'} в файл.")
                        break

                    elif choice == "5":
                        break


