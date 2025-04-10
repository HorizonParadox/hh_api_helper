import asyncio
import os
import sys
from typing import List

import aiohttp

from src.api.vacancy.shemas import VacancyDetail
from src.api.vacancy.vacancy_api import fetch_page, fetch_vacancy_detail, safe_fetch_vacancy_detail
from src.database.models import JobsOrm
from src.database.orm import AsyncORM

sys.path.insert(1, os.path.join(sys.path[0], '..'))


async def fetch_all_vacancies(existing_vacancy_ids: set) -> List[VacancyDetail]:
    async with aiohttp.ClientSession() as session:
        # Загружаем первую страницу
        items, total_pages = await fetch_page(session, 0)
        all_vacancies = items

        # Загружаем остальные страницы
        tasks = [fetch_page(session, page) for page in range(1, total_pages)]
        results = await asyncio.gather(*tasks)

        for result_items, _ in results:
            all_vacancies.extend(result_items)

        print(f"\n[*] Всего найдено вакансий: {len(all_vacancies)}")

        # Фильтруем вакансии, исключая уже существующие в базе данных
        new_vacancies = [v for v in all_vacancies if v.id not in existing_vacancy_ids]

        # Запрашиваем детальную информацию только по новым вакансиям
        detail_tasks = [safe_fetch_vacancy_detail(session, v.id) for v in new_vacancies]
        results = await asyncio.gather(*detail_tasks)
        detailed_vacancies = [r for r in results if r]

        return detailed_vacancies


async def collect_and_store_vacancies():
    # Получаем список идентификаторов вакансий, уже имеющихся в базе данных
    existing_vacancy_ids = await AsyncORM.get_existing_vacancy_ids()

    vacancies = await fetch_all_vacancies(existing_vacancy_ids)
    orm_vacancies = []
    for vacancy in vacancies:
        orm_vacancies.append(
            JobsOrm(
                vacancy=vacancy.name,
                location=vacancy.area,
                stack=", ".join(vacancy.key_skills),
                key_words=vacancy.description,
                salary=vacancy.salary,
                employer=vacancy.employer,
                published_at=vacancy.published_at,
                url=vacancy.alternate_url,
                vacancy_id=vacancy.id
            )
        )

    await AsyncORM.upsert_jobs(orm_vacancies)

    for v in vacancies:
        print(f"\n🔹 {v.name} — {v.area} — {v.employer}")
        print(f"Зарплата: {v.salary or 'не указана'}")
        print(f"URL: {v.alternate_url}")
        print(f"Навыки: {', '.join(v.key_skills) if v.key_skills else '—'}")
        print(f"Описание: {v.description}\n")


if __name__ == "__main__":
    asyncio.run(collect_and_store_vacancies())

# await AsyncORM.select_workers()
# await AsyncORM.update_worker()
# await AsyncORM.insert_additional_resumes()
