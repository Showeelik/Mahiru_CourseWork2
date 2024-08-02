from abc import ABC, abstractmethod
from typing import Any, List, Optional

from src.api.hh_api import JobAPI
from src.models.job import Job
from src.utils import (AreaFileWorker, CSVFileWorker, ExcelFileWorker, FileWorker, JSONFileWorker, TextFileWorker,
                       filter_jobs_by_salary_range, find_city, get_integer_input, setup_logger)

logger = setup_logger(__name__)


class Interaction(ABC):
    @abstractmethod
    def interact(self) -> List[dict]:
        pass


class SearchInteraction(Interaction):
    def __init__(self, api: JobAPI):
        self.api = api

    def interact(self) -> List[dict]:
        """
        Поиск вакансий по ключевому слову
        """

        area = input("Выберите регион (По умолчанию Москва): ")
        logger.info(f"Выбран регион поиска: {area if area else 'Москва'}")
        city_id = find_city(AreaFileWorker().load_data(), area)

        query = input("Введите поисковый запрос: ")
        logger.info(f"Поиск по ключевому слову: {query}")

        salary_range = (
            input("Введите диапазон зарплаты. Формат: мин - макс (через пробел) или макс (необязательно): ") or None
        )

        print("Ищем вакансии...")

        jobs_data = self.api.load_vacancies(query, area=city_id if city_id else 1)

        if salary_range:
            filter_jobs = filter_jobs_by_salary_range(jobs_data, salary_range)
            if filter_jobs is None:
                logger.info("Вакансий не найдено.")
                return []
            logger.info(f"Найдено {len(filter_jobs)} вакансий.")
            return filter_jobs

        logger.info(f"Найдено {len(jobs_data)} вакансий.")

        return jobs_data


class UserInteraction(Interaction):
    def __init__(self, storage: List[dict]) -> None:
        self.storage = storage

    def interact(self) -> Any:
        """
        Вывод вакансий
        """
        while True:
            print("1. Получить топ N вакансий по зарплате")
            print("2. Получить вакансии по ключевому слову по описанию")
            print("3. Назад")

            choice = input("Выберите опцию: ")

            if choice == "1":
                N = get_integer_input("Введите количество вакансий: ")

                if N == 0:
                    N = len(self.storage)

                logger.info(f"Топ {N} вакансий по зарплате выбрано пользователь.")

                jobs = [Job(**job_data) for job_data in self.storage]
                filtered_jobs = self.sorted_jobs(jobs)[:N]

                for job in filtered_jobs:
                    print(job)

            elif choice == "2":
                query = input("Введите поисковый запрос: ")

                logger.info(f"Поиск по ключевому слову по описанию: {query}")

                print("Ищем вакансии...")
                jobs = [Job(**job_data) for job_data in self.storage]
                sorted_jobs = self.sorted_jobs(jobs)
                filtered_jobs = self.filter_jobs_by_keyword(sorted_jobs, query)

                if len(filtered_jobs) == 0:
                    print("Ничего не найдено.")
                    continue

                for job in filtered_jobs:
                    print(job)

            elif choice == "3":
                logger.info("Назад.")
                break

            else:
                print("Неверная опция.")
                continue

            input("Для продолжения нажмите Enter\n")

            FileInteraction(filtered_jobs).interact()

            break

    def filter_jobs_by_keyword(self, jobs: List[Job], keyword: str) -> List[Job]:
        """
        Фильтрация вакансий по ключевому слову
        """
        return [job for job in jobs if keyword.lower() in (job.description or "").lower()]

    def sorted_jobs(self, jobs: List[Job], reverse: bool = True) -> List[Job]:
        """
        Сортировка вакансий по зарплате
        """

        return sorted(jobs, reverse=reverse)


class FileInteraction(Interaction):
    def __init__(self, data: List[Job]) -> None:
        self.data = data
        self.file_name = "vacancies"
        self.file_dir = None
        self.storage: Optional[FileWorker] = None

    def interact(self) -> Any:
        """
        Сохранение вакансий в файл
        """
        while True:

            choice = input("Cохранить вакансию в файл? (Y/N) ")

            if choice.lower() == "n":
                logger.info("Вакансии не сохранены.")
                break

            elif choice.lower() == "y":
                while True:
                    print("1. Название файла (не обязательно, по умолчанию: vacancies).")
                    print("2. Выбрать формат файла (не обязательно, по умолчанию: JSON).")
                    print("3. Продолжить")
                    print("4. Назад")
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

                        if not self.storage:
                            self.storage = JSONFileWorker(self.file_name)
                            self.jobs = [job.to_json() for job in self.data]

                        if self.file_dir:
                            self.storage.save_data(self.jobs, self.file_dir)
                        else:
                            self.storage.save_data(self.jobs)

                        logger.info(
                            f"Вакансии сохранены в файл {self.file_name}, в папке {self.file_dir}, "
                            f"формат {self.storage.__class__.__name__[:-10]}."
                        )
                        print(
                            f"Ваканси{'я' if len(self.jobs) == 1 else 'и'} "
                            f"добавлен{'а' if len(self.jobs) == 1 else 'ы'} в файл."
                        )
                        break
                    elif choice == "4":
                        break
                break
