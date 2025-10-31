import uuid
from collections import defaultdict
import os, datetime
from aiogram import F, Router
from aiogram import types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from settings import TG_TOKEN, MONGODB_LINK
import keyboards as kb
from functions import *

import motor.motor_asyncio, pymongo, settings

router = Router()
cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_LINK)
collection = cluster.tm_bot.users

class Register(StatesGroup):
    year_nabor = State()
    fakultet = State()
    kafedra = State()
    position = State()
    podgruppa = State()
    last_name = State()
    name = State()
    middle_name = State()
    phone_number = State()

class Doklad(StatesGroup):
    video = State()
    geo_location = State()

# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await search_or_save_user(collection, message.from_user, message.chat)
    check_user = await check_point(collection, message.from_user)
    if check_user == 0:
        await message.answer('Добрый день, {}!\nНачните работу с АСУ'.format(message.from_user.first_name), reply_markup=kb.start_keyboard)
    if check_user == 1:
        await message.answer('Добрый день, {}!\nНачните работу с АСУ'.format(message.from_user.first_name),
                             reply_markup=kb.kursant_keyboard)

@router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    check_user = await check_point_menu(collection, user_data['id'])
    if check_user == 1:
        await callback.message.answer('Добрый день!\nНачните работу с АСУ', reply_markup=kb.kursant_keyboard)
    await state.clear()







#Начало регистрации
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
    await state.set_state(Register.podgruppa)
    await message.answer('Если у Вашей кафедры есть подгруппа, выберите свою.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.podgruppa_keyboard)
@router.message(Register.podgruppa)
async def register_kafedra(message: types.Message, state: FSMContext):

    if message.text == "На моей кафедре нет подгрупп":
        await state.update_data(podgruppa="")
    else:
        await state.update_data(podgruppa=message.text)

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
    await state.update_data(id=message.chat.id)
    user_data = await state.get_data()
    user_data["kafedra"] = int(user_data['fakultet']) * 100 + (int(user_data['year_nabor']) % 10) * 10 + int(user_data['kafedra'])

    await message.answer('Формируем данные...', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f'Год набора: {user_data["year_nabor"]}\n'
                         f'Факультет: {user_data["fakultet"]}\n'
                         f'Учебная группа: {str(user_data["kafedra"]) + user_data["podgruppa"]}\n'
                         f'Должность: {user_data["position"]}\n'
                         f'Фамилия: {user_data["last_name"]}\n'
                         f'Имя: {user_data["name"]}\n'
                         f'Отчество: {user_data["middle_name"]}\n'
                         f'Номер телефона: {user_data["phone_number"]}\n', reply_markup=kb.access_keyboard)

@router.callback_query(F.data == 'registration_ok')
async def registration_ok(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Регистрация успешна. Приступим к работе.', reply_markup=kb.back_keyboard)
    user_data = await state.get_data()
    await save_kursant_anketa(collection, user_data)
#Конец регистрации









#Доклад о состоянии дел. Начало
@router.callback_query(F.data == 'doklad')
async def doklad(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отправьте видеозаметку ("кружок") с докладом о состоянии дел. Например "Дома, без происшествий".',
                                   reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Doklad.video)

@router.message(Doklad.video, F.video_note)
async def video(message: types.Message, state: FSMContext, bot: Bot):
    uid = str(uuid.uuid4())
    await state.update_data(uid=uid)
    #video_number = 0  # Number video file
    #while (os.path.isfile(f"video{video_number}.mp4")):  # If the file exists, add one to the number
    #    video_number += 1
    #await bot.download_file(file.file_path,
    #                        f"video{video_number}.mp4") # Download video and save output in file "video.mp4"
    kursant_lastname = await lastname(collection, message.chat.id)
    print(kursant_lastname)
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        r = " morning"
    else:
        r = " evening"
    time = time.strftime("%d.%m.%Y")
    file_id = message.video_note.file_id  # Get file id
    file = await bot.get_file(file_id)
    file = await bot.download_file(file.file_path, f"{kursant_lastname + " " + uid}.mp4")
    filename = kursant_lastname + " " + uid + ".mp4"
    group = await get_group(collection, message.chat.id)
    try:
        os.replace(filename, "Report/"  + group + "/" + time + r +"/" + filename)
    except FileNotFoundError:
        os.makedirs("Report/"  + group + "/" + time + r +"/")
        os.replace(filename, "Report/"  + group + "/" + time + r +"/" + filename)
    await state.update_data(id=message.chat.id)
    await state.set_state(Doklad.geo_location)
    await message.answer('Отправьте свою геолокацию!', reply_markup=kb.geo_keyboard)

@router.message(Doklad.geo_location, F.location)
async def geo_location(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await save_user_location(collection, user_data, message.location)
    await message.answer('Координаты получены. Уникальный код доклада: {}. Пригодится в случае технических неполадок. Запишите его!'.format(user_data['uid']),  reply_markup=types.ReplyKeyboardRemove())
    await message.answer('Спасибо, доклад принят!', reply_markup=kb.back_keyboard)
