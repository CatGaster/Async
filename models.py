import os

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import Column, Integer, String, JSON



POSTGRES_USER = os.getenv["POSTGRES_USER", "postgres"]
POSTGRES_PASSWORD = os.getenv["POSTGRES_PASSWORD", "postgres"]
POSTGRES_DB_NAME = os.getenv["POSTGRES_DB_NAME","asyn_db"]
POSTGRES_HOST = os.getenv["POSTGRES_HOST", "127.0.0.1"]
POSTGRES_PORT = os.getenv["POSTGRES_PORT", "5431"]


DNS = "postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PG_HOST}:{POSTGRES_PORT}:{POSTGRES_DB_NAME}"

engine = create_async_engine(DNS)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass


class SWPeople(Base):

    __tablename__ = "STAR_WARS_people"

    person_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    films: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    skin_color: Mapped[str] = mapped_column(String)
    hair_color: Mapped[str] = mapped_column(String)
    eye_color: Mapped[str] = mapped_column(String)
    birth_year: Mapped[str] = mapped_column(String)
    height: Mapped[str] = mapped_column(String)
    mass: Mapped[str] = mapped_column(String)
    homeworld: Mapped[str] = mapped_column(String)
    species: Mapped[str] = mapped_column(String)
    starships: Mapped[str] = mapped_column(String)
    vehicles: Mapped[str] = mapped_column(String)

async def init_db_async():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
