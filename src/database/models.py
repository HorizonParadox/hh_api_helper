import datetime
from sqlalchemy import text
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from typing import Annotated

intpk = Annotated[int, mapped_column(primary_key=True)]
published_time = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class Base(DeclarativeBase):
    pass


class JobsOrm(Base):
    __tablename__ = "python_jobs"

    id: Mapped[intpk]
    vacancy: Mapped[str]
    location: Mapped[str]
    stack: Mapped[str]
    key_words: Mapped[str]
    salary: Mapped[int]
    employer: Mapped[str]
    published_at: Mapped[published_time]
    url: Mapped[str]
    vacancy_id: Mapped[str]
    created_at: Mapped[created_at]
