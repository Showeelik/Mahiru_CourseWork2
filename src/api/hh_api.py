from abc import ABC, abstractmethod
from typing import Any, Dict, Union

import requests

from src.utils import setup_logger

logger = setup_logger(__name__)


class JobAPI(ABC):

    @abstractmethod
    def load_vacancies(self, keyword: str, page: int = 0, per_page: int = 20, area: int = 1) -> list[dict[Any, Any]]:
        pass


class HHAPI(JobAPI):
    def __init__(self) -> None:
        self.url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params: Dict[str, Union[str, int]] = {
            "text": "",
            "page": 0,
            "per_page": 100,
            "area": 1,
            "only_with_salary": "true",
        }
        self.vacancies: list[dict[Any, Any]] = []

    def load_vacancies(self, keyword: str, page: int = 0, per_page: int = 20, area: int = 1) -> list[dict[Any, Any]]:
        """
        Загружает вакансии по ключевому слову

        ----------------
        * Аргументы:
            * keyword (str): Ключевое слово
            * page (int): Номер страницы
            * per_page (int): Количество вакансий на странице
            * area (int): ID региона

        ----------------
        * Возвращается:
            * List[Dict]: Список словарей с информацией о вакансиях
        """

        logger.info(f"Поиск вакансий по ключевому слову: {keyword}")

        self.params["text"] = keyword
        self.params["page"] = page
        self.params["per_page"] = per_page
        self.params["area"] = area

        # Извлекать новые данные из API
        while int(self.params["page"]) < 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            response.raise_for_status()
            vacancies = response.json().get("items", [])
            self.vacancies.extend(vacancies)
            self.params["page"] = int(self.params["page"]) + 1

        logger.info(f"Выбранные {len(self.vacancies)} вакансии")
        return self.vacancies
