from typing import Any

from src.utils import format_date


class Job:
    def __init__(self, **kwargs: dict) -> None:
        self.title = kwargs.get("name", "Не указано название")
        self.url = kwargs.get("alternate_url", "Не указан URL")
        self.area = kwargs["address"]["raw"] if kwargs["address"] else kwargs["area"]["name"]
        self.address = self.area if self.area else "Не указан адрес"
        self.publication_date = format_date(str(kwargs.get("published_at", "Не указана дата публикации")))
        self.experience = kwargs["experience"].get("name", "Не указано опыт работы")
        self.schedule = kwargs["schedule"].get("name", "Не указана график работы")
        self.employment = kwargs["employment"].get("name", "Не указана тип занятости")
        self.salary = kwargs["salary"] if "salary" in kwargs else None
        self.salary_to = self.salary.get("to", "Не указано зарплата") if self.salary else None
        self.salary_from = self.salary.get("from", "Не указано от зарплаты") if self.salary else None
        self.salary_currency = self.salary.get("currency", "Не указана валюта") if self.salary else None
        self.snippet: str = kwargs["snippet"].get("requirement") or "Не указано требования вакансии"
        self.requirement = self.snippet.replace("<highlighttext>", "").replace("</highlighttext>", "")
        self.snippet2: str = kwargs["snippet"].get("responsibility") or "Не указано описание вакансии"
        self.description = self.snippet2.replace("<highlighttext>", "").replace("</highlighttext>", "")

    def __str__(self) -> str:
        return (
            f"{" Вакансия ":=^100}\n"
            f"Вакансия: {self.title}\n"
            f"URL: {self.url}\n"
            f"Адрес: {self.address}\n"
            f"Дата публикации: {self.publication_date}\n"
            f"Опыт работы: {self.experience}\n"
            f"График работы: {self.schedule}\n"
            f"Тип занятости: {self.employment}\n"
            "Зарплата: "
            + (f"от {self.salary_from}" if self.salary_from else "")
            + (" - " if self.salary_to and self.salary_from else "")
            + (f"до {self.salary_to}" if self.salary_to else "")
            + (f" ({self.salary_currency})" if self.salary_currency else "Зарплата не указана")
            + "\n"
            f"Требования: {self.requirement}\n"
            f"Описание: {self.description}\n"
            f"{" Конец ":=^100}\n"
        )

    def __lt__(self, other: Any) -> Any:
        return self.get_salary() < other.get_salary()

    def __le__(self, other: Any) -> Any:
        return self.get_salary() <= other.get_salary()

    def __gt__(self, other: Any) -> Any:
        return self.get_salary() > other.get_salary()

    def __ge__(self, other: Any) -> Any:
        return self.get_salary() >= other.get_salary()

    def __eq__(self, other: Any) -> Any:
        return self.get_salary() == other.get_salary()

    def __ne__(self, other: Any) -> Any:
        return self.get_salary() != other.get_salary()

    def get_salary(self) -> int:
        """
        Возвращает зарплату в виде целого числа
        """
        if self.salary_to == "Не указано зарплата" or self.salary_to is None:
            if self.salary_from == "Не указано зарплата" or self.salary_from is None:
                return 0
            return int(self.salary_from)
        return int(self.salary_to)

    def to_json(self) -> dict:
        """
        Возвращает словарь с данными о вакансии
        """
        return {
            "name": self.title,
            "alternate_url": self.url,
            "address": self.address,
            "published_at": self.publication_date,
            "experience": self.experience,
            "schedule": self.schedule,
            "employment": self.employment,
            "salary": {"to": self.salary_to, "from": self.salary_from, "currency": self.salary_currency},
            "snippet": {"requirement": self.requirement, "responsibility": self.description},
        }

    def to_dict(self) -> dict:
        """
        Возвращает словарь с данными о вакансии
        """
        return {
            "name": self.title,
            "alternate_url": self.url,
            "address": self.address,
            "published_at": self.publication_date,
            "experience": self.experience,
            "schedule": self.schedule,
            "employment": self.employment,
            "salary_to": self.salary_to,
            "salary_from": self.salary_from,
            "salary_currency": self.salary_currency,
            "requirement": self.requirement,
            "description": self.description,
        }
