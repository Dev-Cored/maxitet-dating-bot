from sqlalchemy.orm import registry, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session, async_sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy import (
create_engine,
Column,
Integer,
Text,
ForeignKey,
TIMESTAMP,
Identity,
BOOLEAN
)
import asyncio
import json
import generators as gen


# Читать ==> https://habr.com/ru/companies/amvera/articles/850470/
## Допилить просмотр анкет

db_url = 'sqlite+aiosqlite:///maxitet_dating.db'
#=================================================================================================================
# Объявление сессий


engine = create_async_engine(db_url, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

#=================================================================================================================
# Регистрация и инициализация
class Profile(Base):
    __tablename__ = 'profiles'
    key = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    user_name = Column(Text)
    user_age = Column(Integer)
    user_gender = Column(Integer)
    user_city = Column(Text)
    user_course = Column(Integer)
    user_direction = Column(Text)
    text = Column(Text)
    media = Column(Text)
    search_for = Column(Text)
    recently_watched = Column(Text)
    enabled = Column(BOOLEAN)
    likes = Column(Integer)
    reports = Column(Integer)

class Report(Base):
    __tablename__ = 'reports'
    key = Column(Integer, primary_key=True)
    intruder_id = Column(Integer)
    prosecutor_id = Column(Integer)
    text = Column(Text)
    date = Column(TIMESTAMP)

class SentMatch(Base):
    __tablename__ = 'sent_matches'
    key = Column(Integer, primary_key=True)
    liked_by = Column(Integer)
    liked_to = Column(Integer)
    watched = Column(BOOLEAN)
    date = Column(TIMESTAMP)

#=================================================================================================================
# Команды базы данных

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_user_profile(session, user_id):
    result = await session.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalars().one_or_none()


async def add_user(session, user_id, user_name, user_age, user_gender, user_city, user_course, user_direction, text, media):
    profile = Profile(user_id=user_id, user_name=user_name, user_age=user_age, user_gender=user_gender,
                              user_course=user_course, user_direction=user_direction, user_city=user_city, text=text,
                              media=media)
    session.add(profile)
    await session.commit()
    return profile


async def get_form_by_filter(session, user_profile):
    user_prefs = user_profile.search_for
    user_city = user_profile.user_city
    user_age = user_profile.user_age

    filters = [Profile.user_age == user_age]

    if user_city == "Онлайн":
        pass
    else:
        filters.append(or_(Profile.user_city == user_city, Profile.user_city == "Онлайн"))

    if user_prefs in ("М", "Ж"):
        filters.append(Profile.user_gender == user_prefs)
    else:
        pass

    result = await session.execute(
        select(Profile).where(*filters)
    )
    return result.scalars().all()


async def check_history_watches(session, user_id_history, form_id_to_check):
    user_profile = await get_user_profile(session, user_id_history)
    user_history_watched = user_profile.recently_watched

    if form_id_to_check == user_profile.key:
        return False

    if user_history_watched is None:
        recently_watched_list = gen.deserialize_deque("[]")
    else:
        recently_watched_list = gen.deserialize_deque(user_history_watched)

    if form_id_to_check not in recently_watched_list:
        recently_watched_list.appendleft(form_id_to_check)
        user_profile.recently_watched = str(gen.serialize_deque(recently_watched_list))
        await session.commit()
        return True
    return False

async def switch_profile(session, user_id):
    profile = await get_user_profile(session, user_id)


#=================================================================================================================

async def main():
    await init_db()


if __name__ == '__main__':
    asyncio.run(main())