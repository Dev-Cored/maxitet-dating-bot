#Импорт библиотек
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
from sqlalchemy import select


#Импорт зависимостей
from db import AsyncSessionLocal, Profile, Report, get_user_profile, add_user
import generators as gen
import kbs as kb

#Роутер
router_reg = Router()

#Статусы
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

###Функции
#Отправка профиля
async def send_profile(user_id, profile, reply_markup=None):
    from bot import bot
    await bot.send_message(user_id ,"Вот так выглядит твой профиль:")
    profile_text = gen.profile(profile)
    try:
        await bot.send_photo(
            user_id,
            photo=profile.media,
            caption=profile_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except TelegramBadRequest as e:
        if "can't use file of type Video as Photo" in str(e):
            await bot.send_video(
                user_id,
                video=profile.media,
                caption=profile_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            raise e

#Обработчик команды старт
@router_reg.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        profile = await get_user_profile(session, user_id)

    await state.clear()

    if profile is not None:
        await send_profile(user_id, profile)
        await message.answer("Используй команду /my_profile чтобы открыть профиль и продолжить использование бота.")
    else:
        await message.answer("👋 Приветствую! Давай заполним анкету, чтобы ты смог смотреть другие! Начнем с имени: ")
        await state.set_state(States_Reg.waiting_for_name)

#Получение имени
@router_reg.message(States_Reg.waiting_for_name)
async def enter_name(message: types.Message, state: FSMContext):
    new_name = message.text
    await state.update_data(name=new_name)

    await message.answer("📅 Теперь введи свой возраст:")
    await state.set_state(States_Reg.waiting_for_age)

#Получение возраста
@router_reg.message(States_Reg.waiting_for_age)
async def enter_age(message: types.Message, state: FSMContext):
    new_age = message.text
    await state.update_data(age=new_age)

    await message.answer("🔵🔴 Теперь твой пол:", reply_markup=kb.gender_keyboard())
    await state.set_state(States_Reg.waiting_for_gender)

#Получение пола
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

#Получение направления
@router_reg.message(States_Reg.waiting_for_direction)
async def enter_course(message: types.Message, state: FSMContext):
    new_direction = message.text

    if new_direction == '⌨️ Программирование':
        new_direction = 'Программирование'
        await state.update_data(direction=new_direction)
        await message.answer(
            "🏅 Сейчас введи свой курс:",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.select_course()
        )
        await state.set_state(States_Reg.waiting_for_course)
    elif new_direction == '✨ Дизайн':
        new_direction = 'Дизайн'
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

#Получение курса
@router_reg.message(States_Reg.waiting_for_course)
async def enter_course(message: types.Message, state: FSMContext):
    try:
        new_course = int(message.text)
        print(new_course)
    except ValueError:
        print("Поймана ошибка")
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.select_course())
        return

    if new_course >= 1 and new_course <= 4:
        print(new_course)
        await state.update_data(course=new_course)
        await message.answer("📄 А теперь самое важное - текст профиля. Тут напиши о себе, чего ищешь в анкетах, к примеру <b>девушку/парня</b> или <b>верных друзей</b>. Ссылки в профиле запрещены:", parse_mode=ParseMode.HTML)
        await state.set_state(States_Reg.waiting_for_text)
    else:
        await message.answer("🚨 Неверный формат! Нажмите на кнопку для ввода!", reply_markup=kb.select_course())

#Получение города
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

#Запрос на получение фото
@router_reg.message(States_Reg.waiting_for_city)
async def enter_city(message: types.Message, state: FSMContext):
    new_city = message.text

    await state.update_data(city=new_city)
    await message.answer("🌠 Вот теперь отправь 📷фото/видео🎥 для профиля:")
    await state.set_state(States_Reg.waiting_for_media)

#Обраьотка получения фото
@router_reg.message(States_Reg.waiting_for_media, F.photo)
async def enter_photo(message: types.Message, state: FSMContext):
    media_id = message.photo[-1].file_id
    user_id = message.from_user.id

    data = await state.get_data()
    new_name = data['name']
    new_age = data['age']
    new_gender = data['gender']
    new_direction = data['direction']
    new_course = data['course']
    new_city = data['city']
    new_text = data['text']
    new_media = media_id

    async with AsyncSessionLocal() as session:
        async with session.begin():
            profile = await add_user(session=session, user_id=user_id, user_name=new_name, user_age=new_age, user_gender=new_gender,
                              user_course=new_course, user_direction=new_direction, user_city=new_city, text=new_text,
                              media=new_media)
    await state.clear()
    await send_profile(user_id, profile)
    await message.answer("Используй команду /my_profile чтобы открыть профиль и продолжить использование бота.")

#Обработка получения видео
@router_reg.message(States_Reg.waiting_for_media, F.video)
async def enter_video(message: types.Message, state: FSMContext):
    media_id = message.video.file_id
    user_id = message.from_user.id

    data = await state.get_data()
    new_name = data['name']
    new_age = data['age']
    new_gender = data['gender']
    new_direction = data['direction']
    new_course = data['course']
    new_text = data['text']
    new_city = data['city']
    new_media = media_id


    async with AsyncSessionLocal() as session:
        async with session.begin():
            profile = await add_user(session=session, user_id=user_id, user_name=new_name, user_age=new_age, user_gender=new_gender,
                              user_course=new_course, user_direction=new_direction, user_city=new_city, text=new_text,
                              media=new_media)
    await state.clear()
    await send_profile(user_id, profile)
    await message.answer("Используй команду /my_profile чтобы открыть профиль и продолжить использование бота.")

#Обработка неверного формата
@router_reg.message(States_Reg.waiting_for_media)
async def enter_media(message: types.Message, state: FSMContext):
    text = message.text
    await message.answer("🚨 Неверный формат! Отправьте фото или видео!")

