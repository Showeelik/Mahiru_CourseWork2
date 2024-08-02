import requests
from typing import List, Dict

from abc import ABC, abstractmethod


class JobAPI(ABC):
    
    @abstractmethod
    def load_vacancies(self, keyword: str, page: int = 0, per_page: int = 20, area: int = 1) -> List[Dict]:
        pass


class HHAPI(JobAPI):
    def __init__(self):
        self.url = 'https://api.hh.ru/vacancies'
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {'text': '', 'page': 0, 'per_page': 100, 'area': 1}
        self.vacancies = []

    def load_vacancies(self, keyword: str, page: int = 0, per_page: int = 20, area: int = 1) -> List[Dict]:

        self.params['text'] = keyword
        self.params['page'] = page
        self.params['per_page'] = per_page
        self.params['area'] = area


        # Fetch new data from API
        while self.params['page'] < 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            response.raise_for_status()
            vacancies = response.json().get('items', [])
            self.vacancies.extend(vacancies)
            self.params['page'] += 1
        
        return self.vacancies

