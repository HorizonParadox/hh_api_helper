from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VacancyDTO(BaseModel):
    vacancy: Optional[str]
    location: Optional[str]
    stack: Optional[str]
    key_words: Optional[str]
    salary: Optional[int]
    employer: Optional[str]
    published_at: Optional[datetime]
    url: Optional[str]
    id: int
