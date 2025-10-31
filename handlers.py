from collections import defaultdict

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


import keyboards as kb
from functions import *

import motor.motor_asyncio, pymongo, settings
from settings import MONGODB_LINK

router = Router()

cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_LINK)
collection = cluster.tm_bot.users

class Register(StatesGroup):
    year_nabor = State()
    fakultet = State()
    kafedra = State()
    position = State()
    last_name = State()
    name = State()
    middle_name = State()
    phone_number = State()


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await search_or_save_user(collection, message.from_user, message.chat)
    check_user = await check_point(collection, message.from_user)
    print(check_user)
    await message.answer('Добрый день, {}!\nНачните работу с АСУ'.format(message.from_user.first_name), reply_markup=kb.start_keyboard)

@router.callback_query(F.data == 'registration')
async def registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите из выпавшего списка год поступления в академию. '
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.year_nabor_keyboard)
    await state.set_state(Register.year_nabor)

@router.message(Register.year_nabor)
async def register_year_nabor(message: types.Message, state: FSMContext):
    await state.update_data(year_nabor=message.text)
    await state.set_state(Register.fakultet)
    await message.answer('Выберите из выпавшего списка факультет.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.fakultet_keyboard)

@router.message(Register.fakultet)
async def register_fakultet(message: types.Message, state: FSMContext):
    await state.update_data(fakultet=message.text)
    await state.set_state(Register.kafedra)
    await message.answer('Выберите из выпавшего списка номер кафедры, на которой обучаетесь.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.kafedra_keyboard)

@router.message(Register.kafedra)
async def register_kafedra(message: types.Message, state: FSMContext):
    await state.update_data(kafedra=message.text)
    await state.set_state(Register.position)
    await message.answer('Выберите из выпавшего списка должность.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.position_keyboard)

@router.message(Register.position)
async def register_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(Register.last_name)
    await message.answer('Введите свою фамилию', reply_markup=types.ReplyKeyboardRemove())

@router.message(Register.last_name)
async def register_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Register.name)
    await message.answer('Введите свое имя')

@router.message(Register.name)
async def register_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.middle_name)
    await message.answer('Введите свое отчество')

@router.message(Register.middle_name)
async def register_middle_name(message: types.Message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    await state.set_state(Register.phone_number)
    await message.answer('Отправьте свой номер', reply_markup=kb.get_number_keyboard)

@router.message(Register.phone_number, F.contact)
async def register_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    user_data = await state.get_data()
    await message.answer(f'Год набора: {user_data["year_nabor"]}\n'
                         f'Факультет: {user_data["fakultet"]}\n'
                         f'Кафедра: {user_data["kafedra"]}\n'
                         f'Должность: {user_data["position"]}\n'
                         f'Фамилия: {user_data["last_name"]}\n'
                         f'Имя: {user_data["name"]}\n'
                         f'Отчетство: {user_data["middle_name"]}\n'
                         f'Номер телефона: {user_data["phone_number"]}\n', reply_markup=types.ReplyKeyboardRemove())
    await save_kursant_anketa(collection, message.from_user, user_data)
    await state.clear()
