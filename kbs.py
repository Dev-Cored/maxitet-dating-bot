from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def menu():
    kb = [
        [types.KeyboardButton(text='1'),
        types.KeyboardButton(text='2'),
        types.KeyboardButton(text='3'),
        types.KeyboardButton(text='4')]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выбери действие...',
        one_time_keyboard=True)
    return keyboard

def cancel_button():
    kb = [
        [types.KeyboardButton(text="🚨Отмена❌")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def gender_keyboard():
    kb = [
        [types.KeyboardButton(text='🔵М'),
         types.KeyboardButton(text='🔴Ж')
         ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Укажи свой пол...',
        one_time_keyboard=True
    )
    return keyboard

def select_course():
    kb = [
        [types.KeyboardButton(text='1'),
        types.KeyboardButton(text='2'),
        types.KeyboardButton(text='3'),
        types.KeyboardButton(text='4')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Введи свой курс...',
        one_time_keyboard=True
    )
    return keyboard

def select_direction():
    kb = [
        [types.KeyboardButton(text='⌨️ Программирование')],
        [types.KeyboardButton(text='✨ Дизайн')],
        [types.KeyboardButton(text='📰 Маркетинг')],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Введи свое направление...',
        one_time_keyboard=True
    )
    return keyboard

def select_city():
    kb = [
        [
            types.KeyboardButton(text='МСК'),
            types.KeyboardButton(text='СПБ'),
            types.KeyboardButton(text='ЕКБ'),
            types.KeyboardButton(text='НСК')
        ],
        [
            types.KeyboardButton(text='Онлайн')
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери город...",
        one_time_keyboard=True
    )
    return keyboard


def profile_actions():
    kb = [
        [
            types.KeyboardButton(text='1'),
            types.KeyboardButton(text='2'),
            types.KeyboardButton(text='3')
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Введи номер действия...",
        one_time_keyboard=True
    )
    return keyboard

def change_profile_menu():
    kb = [
        [
            types.KeyboardButton(text='1'),
            types.KeyboardButton(text='2'),
            types.KeyboardButton(text='3'),
            types.KeyboardButton(text='4'),
        ],
        [
            types.KeyboardButton(text='🚨Отмена❌'),
        ]

    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите, что хотите изменить...",
        one_time_keyboard=True
    )
    return keyboard