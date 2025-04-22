from email.policy import default

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


import db
import generators as gen
import kbs as kb

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


@router_profile.message(Command('my_profile'))
async def my_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer("Вот так выглядит твой профиль:")
    profile = db.get_profile(user_id)
    print(profile)
    profile_text = gen.profile(profile)
    try:
        await message.answer_photo(
            photo=profile['profile_media'],
            caption=profile_text,
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        if "can't use file of type Video as Photo" in str(e):
            await message.answer_video(
                video=profile['profile_media'],
                caption=profile_text,
                parse_mode=ParseMode.HTML
            )
        else:
            raise e

    await message.answer("""
💠 Выберите действие:
1 - Изменить профиль 👤
2 - Изменить фото/видео 🖼🎥
3 - Смотреть анкеты 🔎
    """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

@router_profile.message(States_Profile.waiting_for_commands, F.text == '1')
async def waiting_for_command(message: types.Message, state: FSMContext):
    await message.answer("""
Выбери, что хочешь изменить:

1 - Имя
2 - Возраст
3 - Направление и курс
4 - Текст анкеты
    """, reply_markup=kb.change_profile_menu())
    await state.set_state(States_Profile.waiting_for_profile_actions)

@router_profile.message(States_Profile.waiting_for_profile_actions)
async def waiting_for_profile_action(message: types.Message, state: FSMContext):
    try:
        action = int(message.text)
    except ValueError:
        return await message.answer("🚨 Неверный формат! Нажми на кнопку для ввода!", reply_markup=kb.change_profile_menu())

    if action >= 1 and action <= 4:
        if action == 1:
            await message.answer("Введи новое имя:")
            await state.set_state(States_Profile.waiting_for_new_name)
        elif action == 2:
            await message.answer("Введи новый возраст:")
            await state.set_state(States_Profile.waiting_for_new_age)
        elif action == 3:
            await message.answer("Введи новое направление:", reply_markup=kb.select_direction())
            await state.set_state(States_Profile.waiting_for_new_direction)
        elif action == 4:
            await message.answer("""
Введи новый текст профиля.
Тут напиши о себе, чего ищешь в анкетах, к примеру <b>девушку/парня</b> или <b>верных друзей</b>. Ссылки в профиле запрещены:
            """, parse_mode=ParseMode.HTML)
    else:
        return await message.answer("🚨 Неверный формат! Нажми на кнопку для ввода!",
                                    reply_markup=kb.change_profile_menu())


@router_profile.message(States_Profile.waiting_for_new_name)
async def waiting_for_new_name(message: types.Message, state: FSMContext):
    new_name = message.text
    user_id = message.from_user.id

    db.set_name(user_id, new_name)
    await message.answer("✅Готово! Теперь твой профиль выглядит так:")
    profile = db.get_profile(user_id)
    print(profile)
    profile_text = gen.profile(profile)
    try:
        await message.answer_photo(
            photo=profile['profile_media'],
            caption=profile_text,
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        if "can't use file of type Video as Photo" in str(e):
            await message.answer_video(
                video=profile['profile_media'],
                caption=profile_text,
                parse_mode=ParseMode.HTML
            )
        else:
            raise e

    await message.answer("""
    💠 Выберите действие:
    1 - Изменить профиль 👤
    2 - Изменить фото/видео 🖼🎥
    3 - Смотреть анкеты 🔎
        """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

@router_profile.message(States_Profile.waiting_for_new_age)
async def waiting_for_new_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
    except ValueError:
        return await message.answer("🚨 Неверный формат! Введи число!")

@router_profile.message(States_Profile.waiting_for_commands, F.text == '2')
async def waiting_for_new_media(message: types.Message, state: FSMContext):
    await message.answer("Отправь новое фото/видео 🖼🎥", reply_markup=kb.cancel_button())
    await state.set_state(States_Profile.waiting_for_new_media)

@router_profile.message(States_Profile.waiting_for_new_media, F.photo)
async def waiting_for_new_media_photo(message: types.Message, state: FSMContext):
    media_id = message.photo[-1].file_id
    user_id = message.from_user.id

    db.set_media(media_id, user_id)
    await message.answer("✅Готово! Теперь твой профиль выглядит так:")

    profile = db.get_profile(user_id)
    #print(profile)
    profile_text = gen.profile(profile)
    try:
        await message.answer_photo(
            photo=profile['profile_media'],
            caption=profile_text,
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        if "can't use file of type Video as Photo" in str(e):
            await message.answer_video(
                video=profile['profile_media'],
                caption=profile_text,
                parse_mode=ParseMode.HTML
            )
        else:
            raise e

    await message.answer("""
    💠 Выберите действие:
    1 - Изменить профиль 👤
    2 - Изменить фото/видео 🖼🎥
    3 - Смотреть анкеты 🔎
        """,
                         reply_markup=kb.profile_actions()
                         )
    await state.set_state(States_Profile.waiting_for_commands)

@router_profile.message(States_Profile.waiting_for_new_media, F.video)
async def waiting_for_new_media_video(message: types.Message, state: FSMContext):
    media_id = message.video.file_id
    user_id = message.from_user.id

    db.set_media(media_id, user_id)
    await message.answer("✅Готово! Теперь твой профиль выглядит так:")

    profile = db.get_profile(user_id)
    #print(profile)
    profile_text = gen.profile(profile)
    try:
        await message.answer_photo(
            photo=profile['profile_media'],
            caption=profile_text,
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        if "can't use file of type Video as Photo" in str(e):
            await message.answer_video(
                video=profile['profile_media'],
                caption=profile_text,
                parse_mode=ParseMode.HTML
            )
        else:
            raise e

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