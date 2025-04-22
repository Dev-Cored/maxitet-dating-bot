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

router_reg = Router()

class States_Reg(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_course = State()
    waiting_for_direction = State()
    waiting_for_city = State()
    waiting_for_text = State()
    waiting_for_media = State()

    menu_enter = State()


@router_reg.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username

    await state.clear()

    is_reg = db.check_registred(user_id)

    if is_reg:
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

    else:
        await message.answer("""
👋 Приветствую! Давай заполним анкету, чтобы ты смог смотреть другие! Начнем с имени: 
        """)
        await state.set_state(States_Reg.waiting_for_name)

@router_reg.message(States_Reg.waiting_for_name)
async def enter_name(message: types.Message, state: FSMContext):
    new_name = message.text
    await state.update_data(name=new_name)

    await message.answer("""
📅 Теперь введи свой возраст:
    """)
    await state.set_state(States_Reg.waiting_for_age)

@router_reg.message(States_Reg.waiting_for_age)
async def enter_age(message: types.Message, state: FSMContext):
    new_age = message.text
    await state.update_data(age=new_age)

    await message.answer("""
🔵🔴 Теперь твой пол:
    """, reply_markup=kb.gender_keyboard())
    await state.set_state(States_Reg.waiting_for_gender)

@router_reg.message(States_Reg.waiting_for_gender)
async def enter_gender(message: types.Message, state: FSMContext):
    new_gender = message.text
    if new_gender == "🔵М":
        new_gender = 'М'
        await state.update_data(gender=new_gender)
        await message.answer("Теперь введи свое направление: ", reply_markup=kb.select_direction())
        await state.set_state(States_Reg.waiting_for_direction)

    elif new_gender == '🔴Ж':
        new_gender = 'Ж'
        await state.update_data(gender=new_gender)
        await message.answer("Теперь введи свое направление: ", reply_markup=kb.select_direction())
        await state.set_state(States_Reg.waiting_for_direction)

    else:
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.gender_keyboard())

@router_reg.message(States_Reg.waiting_for_direction)
async def enter_course(message: types.Message, state: FSMContext):
    new_direction = message.text

    if new_direction == '⌨️ Программирование':
        new_direction == 'Программирование'
        await state.update_data(direction=new_direction)
        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )
        await state.set_state(States_Reg.waiting_for_course)
    elif new_direction == '✨ Дизайн':
        new_direction == 'Дизайн'
        await state.update_data(direction=new_direction)
        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )
        await state.set_state(States_Reg.waiting_for_course)
    elif new_direction == '📰 Маркетинг':
        new_direction = 'Маркетинг'
        await state.update_data(direction=new_direction)
        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )
        await state.set_state(States_Reg.waiting_for_course)
    else:
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.select_direction())

@router_reg.message(States_Reg.waiting_for_course)
async def enter_course(message: types.Message, state: FSMContext):
    try:
        new_course = int(message.text)
        print(new_course)
    except ValueError:
        print("Поймана ошибка")
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.select_course())

    if new_course >= 1 and new_course <= 4:
        print(new_course)
        await state.update_data(course=new_course)
        await message.answer("📄 А теперь самое важное - текст профиля. Тут напиши о себе, чего ищешь в анкетах, к примеру <b>девушку/парня</b> или <b>верных друзей</b>. Ссылки в профиле запрещены:", parse_mode=ParseMode.HTML)
        await state.set_state(States_Reg.waiting_for_text)
    else:
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.select_course())


@router_reg.message(States_Reg.waiting_for_text)
async def enter_text(message: types.Message, state: FSMContext):
    new_text = html.escape(message.text)
    await state.update_data(text=new_text)

    await message.answer("🏙 Здесь введи свой город:", reply_markup=kb.select_city())
    await state.set_state(States_Reg.waiting_for_city)
    await message.answer("""
❗️ При выборе пункта 'Онлайн' вы будете попадаться всем городам, но вам будут попадаться только такие же на онлайне.
💡 Этот параметр, как и любой другой, можно изменить в любой момент.
""")


@router_reg.message(States_Reg.waiting_for_city)
async def enter_city(message: types.Message, state: FSMContext):
    new_city = message.text

    await state.update_data(city=new_city)
    await message.answer("🌠 Вот теперь отправь 📷фото/видео🎥 для профиля:")
    await state.set_state(States_Reg.waiting_for_media)


@router_reg.message(States_Reg.waiting_for_media, F.photo)
async def enter_photo(message: types.Message, state: FSMContext):
    media_id = message.photo[-1].file_id
    user_id = message.from_user.id
    user_name = message.from_user.username

    data = await state.get_data()
    new_name = data['name']
    new_age = data['age']
    new_gender = data['gender']
    new_direction = data['direction']
    new_course = data['course']
    new_text = data['text']
    new_city = data['city']
    new_media = media_id

    db.set_profile(user_id, user_name, new_name, new_age, new_gender, new_direction, new_course, new_city, new_text, new_media)
    await state.clear()
    await message.answer("Вот так выглядит твой профиль:")
    profile = db.get_profile(user_id)
    profile_text = gen.profile(profile)
    await message.answer_photo(photo=profile['profile_media'],
                               caption=profile_text,
                               parse_mode=ParseMode.HTML)
    await message.answer("""
Выберите действие:
1 - Смотреть другие анкеты
2 - Изменить фото/видео профиля
3 - Изменить текст профиля
4 - Заполнить анкету заново
    """, reply_markup=kb.menu())


@router_reg.message(States_Reg.waiting_for_media, F.video)
async def enter_video(message: types.Message, state: FSMContext):
    media_id = message.video.file_id
    user_id = message.from_user.id
    user_name = message.from_user.username

    data = await state.get_data()
    new_name = data['name']
    new_age = data['age']
    new_gender = data['gender']
    new_direction = data['direction']
    new_course = data['course']
    new_text = data['text']
    new_city = data['city']
    new_media = media_id

    db.set_profile(user_id, user_name, new_name, new_age, new_gender, new_direction, new_course, new_city, new_text, new_media)
    await state.clear()
    await message.answer("Вот так выглядит твой профиль:")
    profile = db.get_profile(user_id)
    profile_text = gen.profile(profile)
    await message.answer_photo(photo=profile['profile_media'],
                               caption=profile_text,
                               parse_mode=ParseMode.HTML)


@router_reg.message(States_Reg.waiting_for_media)
async def enter_media(message: types.Message, state: FSMContext):
    text = message.text

    await message.answer("🚨 Неверный формат! Отправьте фото или видео!")