from sqlalchemy import insert, select, and_, delete, tuple_
from src.database.database import async_session_factory
from src.database.models import JobsOrm
from src.database.schemas import VacancyDTO
from sqlalchemy.dialects.postgresql import insert


class AsyncORM:
    @staticmethod
    async def insert_jobs(jobs: list[JobsOrm]):
        async with async_session_factory() as session:
            session.add_all(jobs)
            await session.flush()
            await session.commit()

    @staticmethod
    async def get_existing_vacancy_ids() -> set:
        async with async_session_factory() as session:
            query = select(JobsOrm.vacancy_id)
            result = await session.execute(query)
            result_dto = {row[0] for row in result.fetchall()}
            return result_dto

    @staticmethod
    async def select_jobs():
        async with async_session_factory() as session:
            query = select(JobsOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
            workers_dto = [VacancyDTO.model_validate(worker, from_attributes=True) for worker in workers]
            return workers_dto

    @staticmethod
    async def upsert_jobs(jobs: list[JobsOrm]):
        async with async_session_factory() as session:
            select_query = select(JobsOrm.vacancy_id)
            result = await session.execute(select_query)

            existing_ids = set(row[0] for row in result.all())

            new_jobs = [job for job in jobs if job.vacancy_id not in existing_ids]

            if new_jobs:
                session.add_all(new_jobs)
                await session.commit()

    @staticmethod
    async def upsertdel_jobs(jobs: list[JobsOrm]):
        async with async_session_factory() as session:
            job_vacancy = [job.vacancy for job in jobs]
            job_employer = [job.employer for job in jobs]

            db_jobs_query = await session.execute(
                select(JobsOrm.vacancy, JobsOrm.employer)
            )
            db_jobs = set(db_jobs_query.all())

            incoming_jobs = set(zip(job_vacancy, job_employer))

            common_jobs = db_jobs & incoming_jobs

            new_jobs = [
                job for job in jobs
                if (job.vacancy, job.employer) not in common_jobs
            ]

            to_delete = db_jobs - incoming_jobs
            if to_delete:
                await session.execute(
                    delete(JobsOrm).where(
                        tuple_(JobsOrm.vacancy, JobsOrm.employer).in_(to_delete)
                    )
                )

            if new_jobs:
                session.add_all(new_jobs)

            await session.commit()
