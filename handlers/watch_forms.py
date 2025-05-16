#Импорт библиотек
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import or_f, and_f
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto
from aiogram.enums import ParseMode
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest
import html
from sqlalchemy import select
import json
from collections import deque
import random as r
import datetime

#Импорт зависимостей
from db import AsyncSessionLocal, Profile, Report, SentMatch, get_user_profile, get_form_by_filter, check_history_watches
import generators as gen
import kbs as kb
from .profile import States_Profile
from .start_handler import send_profile

#Роутер
router_forms = Router()

#Статусы
class FormStates(StatesGroup):

    waiting_for_preferences = State()
    waiting_for_form_action = State()
    waiting_for_report = State()
    waiting_for_like_action = State()

#Функции



#Отправка анкеты к просмотру
async def send_form_for_watch(session, state, user_id_for):
    await state.clear()
    user_profile_for = await get_user_profile(session, user_id_for)

    forms_to_send = await get_form_by_filter(session, user_profile_for)

    for form in forms_to_send:
        is_allow_to_send = await check_history_watches(session, user_profile_for.user_id, form.key)

        if is_allow_to_send:
            await state.update_data(form_user_id=form.user_id)
            await state.set_state(FormStates.waiting_for_form_action)

            profile_text = gen.profile(form)
            from bot import bot
            try:
                await bot.send_photo(
                    user_profile_for.user_id,
                    photo=form.media,
                    caption=profile_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb.form_actions()
                )
            except TelegramBadRequest as e:
                if "can't use file of type Video as Photo" in str(e):
                    await bot.send_video(
                        user_profile_for.user_id,
                        video=form.media,
                        caption=profile_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=kb.form_actions()
                    )
                else:
                    raise e

            return


    from bot import bot
    await bot.send_message(user_id_for, "Непредвиденная ошибка! Не удалось обнаружить анкеты для показа")



#Добавление лайка в бд
async def send_like(session, state, user_id_by, user_id_to):
    like = SentMatch(liked_by=user_id_by, liked_to=user_id_to, watched=False, date=datetime.datetime.now())
    liked_profile = await get_user_profile(session, user_id_to)
    liked_profile.likes = liked_profile.likes + 1
    session.add(like)
    await session.commit()


    from bot import bot
    await bot.send_message(user_id_to,
                           f"""
Тебя лайкнуло {liked_profile.likes} человек.
Введите:
1 - Чтобы посмотреть
2 - Смотреть анкеты дальше
3 - Я не хочу больше показывать свою анкету
""", reply_markup=kb.incoming_like_actions())
    await state.set_state(FormStates.waiting_for_like_action)


#=================================================================================================================

@router_forms.message(Command('search'))
async def search_form(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        if profile is not None:
            search_for = profile.search_for
            if search_for is None:
                await message.answer("Давай выберем, кого ты будешь искать: ", reply_markup=kb.preferences_keyboard())
                await state.set_state(FormStates.waiting_for_preferences)
            else:
                await send_form_for_watch(session, state, user_id)

        else:
            await message.answer("Воспользуйтесь командой /start, чтобы зарегистрироваться и приступить к просмотру анкет.")


@router_forms.message(FormStates.waiting_for_preferences)
async def get_user_preferences(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    prefs = message.text

    if prefs == "🔵Парней":
        prefs = "М"
    elif prefs == "🔴Девушек":
        prefs = "Ж"
    elif prefs == "Всех":
        prefs = "ВСЕХ"
    else:
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.preferences_keyboard())

    async with AsyncSessionLocal() as session:
        user_profile = await get_user_profile(session, user_id)
        user_profile.search_for = prefs
        await session.commit()
        await send_form_for_watch(session, state, user_id)


@router_forms.message(FormStates.waiting_for_form_action)
async def get_form_action(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    form_action = message.text
    form_data = await state.get_data()
    async with AsyncSessionLocal() as session:
        if form_action == "👎":
            return await send_form_for_watch(session, state, user_id)
        elif form_action == "💤Выйти":
            from .profile import StatesGroup
            profile = await get_user_profile(session, user_id)

            if profile is not None:
                await send_profile(user_id, profile)
                await message.answer("""
💠 Выберите действие:
1 - Изменить профиль 👤
2 - Изменить фото/видео 🖼🎥
3 -  
4 - Смотреть анкеты 🔎
                """,
                                     reply_markup=kb.profile_actions()
                                     )
                await state.set_state(States_Profile.waiting_for_commands)
        elif form_action == "📢Репорт🚨":
            await message.answer("Выберите тип жалобы: ", reply_markup=kb.report_buttons())
            await state.set_state(FormStates.waiting_for_report)
        elif form_action == "💝":
            await send_like(session, user_id, form_data['form_user_id'])
            await send_form_for_watch(session, state, user_id)
        else:
            await message.answer("🚨 Неверный формат! Нажми на кнопку для ввода!", reply_markup=kb.form_actions())

@router_forms.message(FormStates.waiting_for_report)
async def get_report(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    report_text = message.text
    data = await state.get_data()
    form_user_id = data['form_user_id']

    async with AsyncSessionLocal() as session:
        report = Report(intruder_id=user_id, prosecutor_id=form_user_id, text=report_text, date=datetime.datetime.now())
        session.add(report)
        await session.commit()

    await message.answer("Успешно! Репорт отправлен! Переход к просмотру анкет:")
    await send_form_for_watch(session, state, user_id)

@router_forms.message(FormStates.waiting_for_like_action)
async def like_action(message: types.Message, state: FSMContext):
    try:
        action = message.text
    except ValueError:
        return await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.incoming_like_actions())

    if action == 1:
        pass # тут получить лайки
