from aiogram import Bot, Dispatcher, Router, F, types
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


from db import AsyncSessionLocal, Profile, Report, SentMatch, get_user_profile
import generators as gen
import kbs as kb
from .start_handler import send_profile

router_profile = Router()

class States_Profile(StatesGroup):
    waiting_for_commands = State()
    waiting_for_new_media = State()

    waiting_for_profile_actions = State()
    waiting_for_new_name = State()
    waiting_for_new_age = State()
    waiting_for_new_direction = State()
    waiting_for_new_course = State()
    waiting_for_new_text = State()
    waiting_for_new_city = State()
    waiting_for_new_gender = State()

#=================================================================================================================
# Профиль

@router_profile.message(Command('my_profile'))
async def my_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)

        if profile is not None:
            await send_profile(user_id, profile)
            await message.answer("""
💠 Выберите действие:
1 - Изменить профиль 👤
2 - Изменить фото/видео 🖼🎥
3 - Смотреть анкеты 🔎
    """,
                             reply_markup=kb.profile_actions()
                             )
            await state.set_state(States_Profile.waiting_for_commands)
        else:
            await message.answer("Воспользуйтесь командой /start, чтобы зарегистрироваться и приступить к просмотру анкет.")


# 1 - Изменение профиля
@router_profile.message(States_Profile.waiting_for_commands, F.text == '1')
async def waiting_for_command(message: types.Message, state: FSMContext):
    await message.answer("""
Выбери, что хочешь изменить:

1 - Имя
2 - Возраст
3 - Направление и курс
4 - Город
5 - Текст анкеты
    """, reply_markup=kb.change_profile_menu())
    await state.set_state(States_Profile.waiting_for_profile_actions)


# Изменение профиля
@router_profile.message(States_Profile.waiting_for_profile_actions)
async def waiting_for_profile_action(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        action = int(message.text)
    except ValueError:
        return await message.answer("🚨 Неверный формат! Нажми на кнопку для ввода!", reply_markup=kb.change_profile_menu())

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)

    if action >= 1 and action <= 5:
        if action == 1:
            await message.answer("Введи новое имя:", reply_markup=kb.button_text(profile.user_name))
            await state.set_state(States_Profile.waiting_for_new_name)
        elif action == 2:
            await message.answer("Введи новый возраст:", reply_markup=kb.button_text(profile.user_age))
            await state.set_state(States_Profile.waiting_for_new_age)
        elif action == 3:
            await message.answer("Введи новое направление:", reply_markup=kb.select_direction())
            await state.set_state(States_Profile.waiting_for_new_direction)
        elif action == 4:
            await message.answer("Введи свой город: ", reply_markup=kb.select_city())
            await state.set_state(States_Profile.waiting_for_new_city)
        elif action == 5:
            await message.answer("Введи новый пол🤨: ", reply_markup=kb.gender_keyboard())
            await state.set_state(States_Profile.waiting_for_new_gender)
        elif action == 6:
            await message.answer("""
Введи новый текст профиля.
Тут напиши о себе, чего ищешь в анкетах, к примеру <b>девушку/парня</b> или <b>верных друзей</b>. Ссылки в профиле запрещены:
                                    """, parse_mode=ParseMode.HTML, reply_markup=kb.button_text(profile.text))
            await state.set_state(States_Profile.waiting_for_new_text)
    else:
        return await message.answer("🚨 Неверный формат! Нажми на кнопку для ввода!",
                                    reply_markup=kb.change_profile_menu())


# Новое имя
@router_profile.message(States_Profile.waiting_for_new_name)
async def waiting_for_new_name(message: types.Message, state: FSMContext):
    new_name = message.text
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.user_name = new_name
        await session.commit()

    await message.answer("✅Готово! Теперь твой профиль выглядит так:")
    await send_profile(user_id, profile)
    await message.answer("""
    💠 Выберите действие:
    1 - Изменить профиль 👤
    2 - Изменить фото/видео 🖼🎥
    3 - Отключите мою анкету
    4 - Смотреть анкеты 🔎
        """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)


# Новый возраст
@router_profile.message(States_Profile.waiting_for_new_age)
async def waiting_for_new_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        age = int(message.text)
    except ValueError:
        return await message.answer("🚨 Неверный формат! Введи число!")

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.user_age = age
        await session.commit()

    await message.answer("✅Готово! Теперь твой профиль выглядит так:")
    await send_profile(user_id, profile)
    await message.answer("""
        💠 Выберите действие:
        1 - Изменить профиль 👤
        2 - Изменить фото/видео 🖼🎥
        3 - Отключите мою анкету
        4 - Смотреть анкеты 🔎
            """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)


# Новое направление
@router_profile.message(States_Profile.waiting_for_new_direction)
async def waiting_for_new_direction(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_direction = message.text

    if new_direction == '⌨️ Программирование':
        new_direction = 'Программирование'

        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )

    elif new_direction == '✨ Дизайн':
        new_direction = 'Дизайн'
        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )

    elif new_direction == '📰 Маркетинг':
        new_direction = 'Маркетинг'
        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )

    else:
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.select_direction())
        new_direction = None
        return

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.user_direction = new_direction
        await session.commit()

    await message.answer("✅Готово! Теперь введи свой курс:", reply_markup=kb.select_course())
    await state.set_state(States_Profile.waiting_for_new_course)


# Новый курс
@router_profile.message(States_Profile.waiting_for_new_course)
async def waiting_for_new_course(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        course = int(message.text)
    except ValueError:
        return await message.answer("🚨 Неверный формат! Введи число!")

    if course >= 1 and course <= 4:
        async with AsyncSessionLocal() as session:
            profile = await get_user_profile(session, user_id)
            profile.user_course = course
            await session.commit()

        await message.answer("✅Готово! Теперь твой профиль выглядит так:")
        await send_profile(user_id, profile)
        await message.answer("""
            💠 Выберите действие:
            1 - Изменить профиль 👤
            2 - Изменить фото/видео 🖼🎥
            3 - Отключите мою анкету
            4 - Смотреть анкеты 🔎
                """,
                             reply_markup=kb.profile_actions()
                             )
        await state.set_state(States_Profile.waiting_for_commands)
    else:
        return await message.answer("🚨 Неверный формат! Введи число!")


# Новый город
@router_profile.message(States_Profile.waiting_for_new_city)
async def waiting_for_new_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.city = city
        await session.commit()

    await message.answer("✅Готово! Теперь твой профиль выглядит так:")
    await send_profile(user_id, profile)
    await message.answer("""
        💠 Выберите действие:
        1 - Изменить профиль 👤
        2 - Изменить фото/видео 🖼🎥
        3 - Отключите мою анкету
        4 - Смотреть анкеты 🔎
            """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

# Новый пол 🤨
@router_profile.message(States_Profile.waiting_for_new_gender)
async def waiting_for_new_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_gender = message.text

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        if new_gender == "🔵М":
            new_gender = 'М'
            profile.gender = new_gender

        elif new_gender == '🔴Ж':
            new_gender = 'Ж'
            profile.gender = new_gender

        else:
            await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.gender_keyboard())
            return

    await message.answer("✅Готово! Теперь твой профиль выглядит так:")
    await send_profile(user_id, profile)
    await message.answer("""
        💠 Выберите действие:
        1 - Изменить профиль 👤
        2 - Изменить фото/видео 🖼🎥
        3 - Отключите мою анкету
        4 - Смотреть анкеты 🔎
            """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

# Новый текст профиля
@router_profile.message(States_Profile.waiting_for_new_text)
async def waiting_for_new_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.text = text
        await session.commit()

    await message.answer("✅Готово! Теперь твой профиль выглядит так:")
    await send_profile(user_id, profile)
    await message.answer("""
        💠 Выберите действие:
        1 - Изменить профиль 👤
        2 - Изменить фото/видео 🖼🎥
        3 - Отключите мою анкету
        4 - Смотреть анкеты 🔎
            """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)


# Новое медиа
@router_profile.message(States_Profile.waiting_for_commands, F.text == '2')
async def waiting_for_new_media(message: types.Message, state: FSMContext):
    await message.answer("Отправь новое фото/видео 🖼🎥", reply_markup=kb.cancel_button())
    await state.set_state(States_Profile.waiting_for_new_media)

@router_profile.message(States_Profile.waiting_for_new_media, F.photo)
async def waiting_for_new_media_photo(message: types.Message, state: FSMContext):
    media_id = message.photo[-1].file_id
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.media = media_id
        await session.commit()
    await message.answer("✅Готово! Теперь твой профиль выглядит так:")

    await send_profile(user_id, profile)

    await message.answer("""
    💠 Выберите действие:
    1 - Изменить профиль 👤
    2 - Изменить фото/видео 🖼🎥
    3 - Отключите мою анкету
    4 - Смотреть анкеты 🔎
        """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

@router_profile.message(States_Profile.waiting_for_new_media, F.video)
async def waiting_for_new_media_video(message: types.Message, state: FSMContext):
    media_id = message.video.file_id
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)
        profile.media = media_id
        await session.commit()
    await message.answer("✅Готово! Теперь твой профиль выглядит так:")

    await send_profile(user_id, profile)

    await message.answer("""
    💠 Выберите действие:
    1 - Изменить профиль 👤
    2 - Изменить фото/видео 🖼🎥
    3 - Смотреть анкеты 🔎
        """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

@router_profile.message(States_Profile.waiting_for_new_media)
async def waiting_for_new_media_text(message: types.Message, state: FSMContext):
    text = message.text

    if text == "🚨Отмена❌":
        await message.answer("""
💠 Выберите действие:
1 - Изменить профиль 👤
2 - Изменить фото/видео 🖼🎥
3 - Смотреть анкеты 🔎
        """, reply_markup=kb.profile_actions())
        await state.set_state(States_Profile.waiting_for_commands)
    else:
        await message.answer("🚨 Неверный формат! Отправьте фото или видео!", reply_markup=kb.cancel_button())



# Включение/выключение профиля
@router_profile.message(States_Profile.waiting_for_commands, F.text == '3')
async def switch_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:



# Просмотр анкет
from .watch_forms import FormStates, send_form_for_watch

@router_profile.message(States_Profile.waiting_for_commands, F.text == '4')
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
