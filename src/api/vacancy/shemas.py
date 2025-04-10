from datetime import datetime
from typing import List
from pydantic import BaseModel, field_validator
from src.api.utils import strip_html_tags


class Area(BaseModel):
    id: str
    name: str


class Employer(BaseModel):
    id: str
    name: str


class VacancyShort(BaseModel):
    id: str
    name: str
    area: Area
    employer: Employer
    published_at: str
    alternate_url: str


class VacanciesResponse(BaseModel):
    items: List[VacancyShort]
    page: int
    pages: int
    per_page: int
    found: int


class VacancyDetail(BaseModel):
    id: str
    name: str
    description: str
    key_skills: List[str]
    area: str
    employer: str
    published_at: datetime
    alternate_url: str
    salary: int | None

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return strip_html_tags(value)
