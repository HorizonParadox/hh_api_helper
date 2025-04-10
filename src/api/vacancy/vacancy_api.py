import asyncio
import random
from typing import List, Tuple
import aiohttp
from src.api.vacancy.shemas import VacancyShort, VacancyDetail, VacanciesResponse
from src.api.utils import keep_only_latin_words_and_digits, parse_salary, get_datetime_type


# "area": ["1", "2019", "2", "2024", "2371", "53"],
# ["113", "5", "40", "9", "16", "28", "1001", "48", "97"]
MAX_CONCURRENT_REQUESTS = 5
RETRY_COUNT = 3

# Семафор для ограничения одновременных запросов
SEM = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

def get_search_params(page: int) -> dict:
    return {
        "text": "name:Python", # Строка поиска, например, text=Python developer
        "specialization": ["1.221", "1.475", "1.25", "1.82"], # id спец-ии (или список ID), напр. 1.221 программист
        "area": ["113", "40", "1001", "97"],  # id региона (или список ID), например, area=1 для Москвы
        "experience": "between1And3", # Опыт работы: noExperience, between1And3, between3And6, moreThan6
        "employment": "full", # Тип занятости: full, part, project, volunteer, probation
        "schedule": ["fullDay", "remote"], # График работы: fullDay, shift, flexible, remote, flyInFlyOut
        "period": 30, # Период публикации вакансии в днях: 1, 3, 7, 14, 30
        "page": page, # Номер страницы результатов (начиная с 0)
        "per_page": 100 # Количество вакансий на странице (максимум 100)
    }


async def fetch_page(session: aiohttp.ClientSession, page: int) -> Tuple[List["VacancyShort"], int]:
    url = "https://api.hh.ru/vacancies"
    params = get_search_params(page)

    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json()
        parsed = VacanciesResponse(**data)
        print(f"[+] Загружена страница {page + 1} из {parsed.pages}")
        return parsed.items, parsed.pages


async def fetch_vacancy_detail(session: aiohttp.ClientSession, vacancy_id: str) -> "VacancyDetail":

    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    async with session.get(url) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return VacancyDetail(
            id=data["id"],
            name=data["name"],
            description=keep_only_latin_words_and_digits(data.get("description", "")),
            key_skills=[s["name"] for s in data.get("key_skills", [])],
            area=data["area"]["name"],
            employer=data["employer"]["name"] if data.get("employer") else "",
            published_at=get_datetime_type(data["published_at"]),
            alternate_url=data["alternate_url"],
            salary=parse_salary(data.get("salary"))
        )

async def safe_fetch_vacancy_detail(session: aiohttp.ClientSession, vacancy_id: str, retries: int = RETRY_COUNT):
    async with SEM:
        for attempt in range(1, retries + 1):
            try:
                await asyncio.sleep(random.uniform(0.1, 0.3))  # задержка между запросами
                return await fetch_vacancy_detail(session, vacancy_id)
            except aiohttp.ClientResponseError as e:
                if e.status == 403 and attempt < retries:
                    print(f"[!] 403 для вакансии {vacancy_id}, повтор {attempt}")
                    await asyncio.sleep(2)
                else:
                    print(f"[!] Ошибка {e.status} при получении вакансии {vacancy_id}")
                    return None