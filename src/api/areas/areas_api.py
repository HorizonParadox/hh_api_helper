import asyncio
from typing import List

import aiohttp

from src.api.areas.areas_schema import ParentArea, ModelItem, Model


async def fetch_areas(session: aiohttp.ClientSession) -> Model:
    url = "https://api.hh.ru/areas"

    async with session.get(url) as resp:
        resp.raise_for_status()
        data = await resp.json()
        parsed = Model(RootModel=data)
        return parsed


async def fetch_all_areas() -> Model:
    async with aiohttp.ClientSession() as session:
        areas = await fetch_areas(session)
        return areas


# get_areas = asyncio.run(fetch_all_areas())
# for country in get_areas.RootModel:
#     print(f"\n{country.name}: {country.id}")
#     for town in country.areas:
#         if town.parent_id=="1001":
#             print(f"{town.name}")
