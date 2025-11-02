import uuid, zipfile
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

class Address(StatesGroup):
    put_address = State()
    get_dop_address = State()
    begin = State()
    get_address = State()

class Address_me(StatesGroup):
    get_address_me = State()

# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    await search_or_save_user(collection, message.from_user, message.chat)
    kursant = await collection.find_one({"user_id": message.from_user.id})
    try:
        info = await info_account(collection, message.from_user.id)
    except Exception as e:
        print(e)
    check_user = await check_point(collection, message.from_user)
    user_status = await bot.get_chat_member(chat_id='-1001371757648', user_id=message.from_user.id)
    if user_status.status != 'left':
        if check_user == 0:
            await message.answer(f'Добрый день, {message.from_user.first_name}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n',
                                 reply_markup=kb.start_keyboard, parse_mode='HTML')
        if check_user == 1:
            await message.answer(f'Добрый день, {kursant['Present']['user_name']}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n{info}',
                                 reply_markup=kb.kursant_keyboard, parse_mode='HTML')
        if check_user == 2:
            await message.answer(f'Добрый день, {kursant['Present']['user_name']}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n{info}',
                                 reply_markup=kb.komandir_keyboard, parse_mode='HTML')
        if check_user == 3:
            await message.answer(f'Добрый день, {kursant['Present']['user_name']}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n{info}',
                                 reply_markup=kb.nachalnik_keyboard, parse_mode='HTML')
    else:
        await message.answer("Сначала войдите в канал бота по ссылке https://t.me/+A3OPN5aJdoExOTJi или по ссылке https://t.me/+CJYR3Skxip5iM2U6\nЗатем нажмите на /start")


@router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await search_or_save_user_menu(collection, callback.from_user)
    kursant = await collection.find_one({"user_id": callback.from_user.id})
    try:
        info = await info_account(collection, callback.from_user.id)
    except Exception as e:
        print(e)
    check_user = await check_point_menu(collection, callback.from_user.id)
    user_status = await bot.get_chat_member(chat_id='-1001371757648', user_id=callback.from_user.id)
    if user_status.status != 'left':
        if check_user == 0:
            await callback.message.answer('Добрый день, {}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать. '.format(callback.from_user.first_name),
                                 reply_markup=kb.start_keyboard, parse_mode='HTML')
        if check_user == 1:
            await callback.message.answer(f'Добрый день, {kursant['Present']['user_name']}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n{info}', parse_mode='HTML', reply_markup=kb.kursant_keyboard)
        if check_user == 2:
            await callback.message.answer(f'Добрый день, {kursant['Present']['user_name']}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n{info}', parse_mode='HTML', reply_markup=kb.komandir_keyboard)
        if check_user == 3:
            await callback.message.answer(f'Добрый день, {kursant['Present']['user_name']}!\nБот находится в тестовом режиме, по всем вопросам и предложениям со скриншотами и видеозаписями экрана обращайтесь к @maksshirk. Иногда перезагружаю бот. В трудных ситуациях Вам поможет команда /start в чат. Спасибо за терпение! Этот бот поможет сократить большое количество нервов и сил, а также время для обобщения докладов командованию. И возможно выполнит и более полезную задачу, о которой лучше не писать, но кому нужно могу рассказать.\n{info}', parse_mode='HTML', reply_markup=kb.nachalnik_keyboard)
        await state.clear()
    else:
        await callback.message.answer("Сначала войдите в канал бота по ссылке https://t.me/+A3OPN5aJdoExOTJi или по ссылке https://t.me/+CJYR3Skxip5iM2U6\nЗатем нажмите на /start")

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

    if message.text == "На моей кафедре/в управлении нет подгрупп":
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
    await message.answer('Отправьте свой номер через кнопку ниже. Если её нет или она пропала, нажмите на "шоколадку" слева от кнопки "отправить"', reply_markup=kb.get_number_keyboard)
@router.message(Register.phone_number, F.contact)
async def register_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    await state.update_data(id=message.chat.id)
    user_data = await state.get_data()
    if user_data['kafedra'] != "Управление факультета":
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
    time = datetime.datetime.now()
    if 8 <= time.hour <= 9 or 21 <= time.hour <= 22:
        await callback.message.answer('Отправьте видеозаметку ("кружок") с докладом о состоянии дел. Например "Дома, без происшествий".',
                                       reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Doklad.video)
    else:
        await callback.message.answer('Доклад принимается утром с 8:00 до 9:00 по МСК и вечером с 21:00 до 22:00 по МСК!', reply_markup=kb.back_keyboard)
@router.message(Doklad.video, F.video_note)
async def video(message: types.Message, state: FSMContext, bot: Bot):
    user_status = await bot.get_chat_member(chat_id='-1001371757648', user_id=message.from_user.id)
    if user_status.status != 'left':
        uid = str(uuid.uuid4())
        await state.update_data(uid=uid)
        kursant_lastname = await lastname(collection, message.chat.id)
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
    else:
        await message.answer("Чтобы продолжить сначала войдите в канал бота по ссылке https://t.me/+A3OPN5aJdoExOTJi\nЗатем нажмите на /start")

@router.message(Doklad.geo_location, F.location)
async def geo_location(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await save_user_location(collection, user_data, message.location)
    await message.answer('Координаты получены. Уникальный код доклада: {}. Пригодится в случае технических неполадок. Запишите его!'.format(user_data['uid']),  reply_markup=types.ReplyKeyboardRemove())
    await message.answer('Спасибо, доклад принят!', reply_markup=kb.back_keyboard)
#Доклад о состоянии дел. Конец

#Ввод адресов проживания. Начало
@router.callback_query(F.data == 'put_address')
async def put_address(callback: CallbackQuery, state: FSMContext):
    try:
        kursant = await poisk_kursanta(collection, callback.from_user.id)
        await callback.message.answer('Введите адрес проживания следующего курсанта.\n{}'.format(kursant['Present']['user_lastname'] + " "
                                                                                                 + kursant['Present']['user_name'] + " "
                                                                                                 + kursant['Present']['user_middlename']),
                                       reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(user_id=kursant['user_id'])
        await state.set_state(Address.get_address)
    except Exception as e:
        await callback.message.answer('Отсуствуют курсанты, у которых не указано место проживания', reply_markup=kb.back_keyboard)
@router.message(Address.get_address)
async def get_address(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await put_address_from_coords(collection, user_data['user_id'], message.text)
    await message.answer('Адрес отправлен в базу данных!', reply_markup=kb.back_address_keyboard)
    await state.set_state(Address.get_dop_address)
@router.callback_query(F.data == 'put_address_dop')
async def put_address_dop(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите следующий адрес проживания.', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Address.get_address)
@router.callback_query(F.data == 'put_address_end')
async def put_address_end(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await save_kursant_address(collection, user_data['user_id'])
    await callback.message.answer('Вернуться в меню или продолжить вводить адреса других курсантов?', reply_markup=kb.back_address_next_keyboard)
    await state.set_state(Address.begin)
@router.callback_query(F.data == 'reset_address_key')
async def reset_address_key(callback: CallbackQuery, state: FSMContext):
    await reset_address(collection, callback.from_user.id)
    await callback.message.answer('База данных готова к обновлению места проживания.', reply_markup=kb.back_keyboard)
#Ввод адресов проживания. Конец

@router.callback_query(F.data == 'prinyt_doklad')
async def prinyt_doklad(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await find_report(collection, callback.from_user.id, callback, kb)
    await get_video_note(collection, callback.from_user.id, callback, kb)

@router.callback_query(F.data == 'create_map_knopka')
async def create_map_knopka(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await create_map(collection, callback.from_user.id, callback, kb)


@router.callback_query(F.data == 'put_address_me')
async def put_address_me(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите адрес проживания (место проведения отпуска) по образцу: г. Санкт-Петербург, п. Шушары, ул. Школьная , д. 26, кв.51',reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Address_me.get_address_me)

@router.message(Address_me.get_address_me)
async def get_address_me(message: types.Message, state: FSMContext):
    await put_address_from_coords(collection, message.from_user.id, message.text)
    await message.answer('Адрес отправлен в базу данных!', reply_markup=kb.back_keyboard)