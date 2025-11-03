import uuid, zipfile, asyncio, aioschedule
from collections import defaultdict
import os, datetime, logging, codecs
from aiogram import F, Router
from aiogram import types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from settings import TG_TOKEN, MONGODB_LINK, PASSWORD_NKY, PASSWORD_KO, PASSWORD_KUG
import keyboards as kb
from functions import *
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

import motor.motor_asyncio, pymongo, settings

router = Router()
cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_LINK)
collection = cluster.tm_bot.users

class Register(StatesGroup):
    year_nabor = State()
    fakultet = State()
    kafedra = State()
    position = State()
    password_nky = State()
    password_kug = State()
    password_ko = State()
    podgruppa = State()
    last_name = State()
    name = State()
    middle_name = State()
    phone_number = State()

class Doklad(StatesGroup):
    video = State()
    geo_location = State()

class Status_change(StatesGroup):
    Status_change_get = State()
    Status_change_put = State()

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
    logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввёл команду /start, возможно это его первая запись и он начал регистрацию")
    try:
        info = await info_account(collection, message.from_user.id)
    except Exception as e:
        print("Ошибка в блоке старта: " + str(e))
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
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " вернулся в меню для работы с ботом")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    try:
        info = await info_account(collection, callback.from_user.id)
    except Exception as e:
        print("Ошибка в блоке перехода в меню: " + str(e))
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
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " начал регистрацию")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await callback.message.answer('Выберите из выпавшего списка год поступления в академию. '
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.year_nabor_keyboard)
    await state.set_state(Register.year_nabor)
@router.message(Register.year_nabor)
async def register_year_nabor(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " вводит год набора при регистрации")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(year_nabor=message.text)
    await state.set_state(Register.fakultet)
    await message.answer('Выберите из выпавшего списка факультет.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.fakultet_keyboard)
@router.message(Register.fakultet)
async def register_fakultet(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " вводит факультет при регистрации")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(fakultet=message.text)
    await state.set_state(Register.kafedra)
    await message.answer('Выберите из выпавшего списка номер кафедры, на которой обучаетесь.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.kafedra_keyboard)
@router.message(Register.kafedra)
async def register_kafedra(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " вводит кафедру при регистрации")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(kafedra=message.text)
    await state.set_state(Register.podgruppa)
    await message.answer('Если у Вашей кафедры есть подгруппа, выберите свою.'
                                  'Если случайно закрыли клавиатуру, нажмите на символ '
                                  '"шоколадки" рядом с кнопкой отправки сообщения',
                                   reply_markup=kb.podgruppa_keyboard)
@router.message(Register.podgruppa)
async def register_kafedra(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " выбирает подгруппу при регистрации")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
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
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " выбирает должность при регистрации")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(position=message.text)
    if message.text == "Начальник курса" or message.text == "Курсовой офицер" or message.text == "Старшина курса":
        await state.set_state(Register.password_nky)
        await message.answer('Для продолжения введите пароль!', reply_markup=types.ReplyKeyboardRemove())
    if message.text == "Командир учебной группы":
        await state.set_state(Register.password_kug)
        await message.answer('Для продолжения введите пароль!', reply_markup=types.ReplyKeyboardRemove())
    if message.text == "Командир 1 отд-я" or message.text == "Командир 2 отд-я" or message.text == "Командир 3 отд-я":
        await state.set_state(Register.password_ko)
        await message.answer('Для продолжения введите пароль!', reply_markup=types.ReplyKeyboardRemove())
    if message.text == "Курсант 1 отд-я" or message.text == "Курсант 2 отд-я" or message.text == "Курсант 3 отд-я":
        await state.set_state(Register.last_name)
        await message.answer('Введите свою фамилию', reply_markup=types.ReplyKeyboardRemove())

@router.message(Register.password_nky)
async def register_password_nky(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    if message.text == PASSWORD_NKY:
        try:
            logging.warning("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
        except Exception as ex:
            logging.warning("Ошибка логирования в поле для ввода пароля: " + str(ex))
        await state.set_state(Register.last_name)
        await message.answer('Введите свою фамилию', reply_markup=types.ReplyKeyboardRemove())
    else:
        try:
            logging.warning("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
            print("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
        except Exception as ex:
            logging.warning("Ошибка логирования в поле для ввода пароля: " + str(ex))
        await message.answer('Пароль введён неверно!', reply_markup=kb.back_keyboard)

@router.message(Register.password_kug)
async def register_password_kug(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    if message.text == PASSWORD_KUG:
        try:
            logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввёл правильный пароль и переходит в вводу фамилии")
        except Exception as ex:
            logging.info("Ошибка логирования: " + str(ex))
        await state.set_state(Register.last_name)
        await message.answer('Введите свою фамилию', reply_markup=types.ReplyKeyboardRemove())
    else:
        try:
            logging.warning("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
            print("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
        except Exception as ex:
            logging.warning("Ошибка логирования в поле для ввода пароля: " + str(ex))
        await message.answer('Пароль введён неверно!', reply_markup=kb.back_keyboard)

@router.message(Register.password_ko)
async def register_password_ko(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    if message.text == PASSWORD_KO:
        try:
            logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввёл правильный пароль и переходит в вводу фамилии")
        except Exception as ex:
            logging.info("Ошибка логирования: " + str(ex))
        await state.set_state(Register.last_name)
        await message.answer('Введите свою фамилию', reply_markup=types.ReplyKeyboardRemove())
    else:
        try:
            logging.warning("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
            print("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " ввел неправильный пароль: " + message.text)
        except Exception as ex:
            logging.warning("Ошибка логирования в поле для ввода пароля: " + str(ex))
        await message.answer('Пароль введён неверно!', reply_markup=kb.back_keyboard)

@router.message(Register.last_name)
async def register_last_name(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " вводит фамилию")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(last_name=message.text)
    await state.set_state(Register.name)
    await message.answer('Введите свое имя')
@router.message(Register.name)
async def register_name(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " вводит имя")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(name=message.text)
    await state.set_state(Register.middle_name)
    await message.answer('Введите свое отчество')
@router.message(Register.middle_name)
async def register_middle_name(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " вводит отчество")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await state.update_data(middle_name=message.text)
    await state.set_state(Register.phone_number)
    await message.answer('Отправьте свой номер через кнопку ниже. Если её нет или она пропала, нажмите на "шоколадку" слева от кнопки "отправить"', reply_markup=kb.get_number_keyboard)
@router.message(Register.phone_number, F.contact)
async def register_phone_number(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " отправляет номер телефона")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
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
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " проверяет данные и заканчивает регистрацию")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await callback.message.answer('Регистрация успешна. Приступим к работе.', reply_markup=kb.back_keyboard)
    user_data = await state.get_data()
    await save_kursant_anketa(collection, user_data)
#Конец регистрации

#Доклад о состоянии дел. Начало
@router.callback_query(F.data == 'doklad')
async def doklad(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " приступил к докладу о состоянии дел")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    time = datetime.datetime.now()
    if 8 <= time.hour <= 9 or 21 <= time.hour <= 22:
        await callback.message.answer('Отправьте видеозаметку ("кружок") с докладом о состоянии дел. Например "Дома, без происшествий".',
                                       reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Doklad.video)
    else:
        await callback.message.answer('Доклад принимается утром с 8:00 до 9:00 по МСК и вечером с 21:00 до 22:00 по МСК!', reply_markup=kb.back_keyboard)
@router.message(Doklad.video, F.video_note)
async def video(message: types.Message, state: FSMContext, bot: Bot):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " отправил видео о состоянии дел")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
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
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " отправил геолокацию, где находится")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    user_data = await state.get_data()
    await save_user_location(collection, user_data, message.location)
    await message.answer('Координаты получены. Уникальный код доклада: {}. Пригодится в случае технических неполадок. Запишите его!'.format(user_data['uid']),  reply_markup=types.ReplyKeyboardRemove())
    await message.answer('Спасибо, доклад принят!', reply_markup=kb.back_keyboard)
#Доклад о состоянии дел. Конец

#Ввод адресов проживания. Начало
@router.callback_query(F.data == 'put_address')
async def put_address(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " вводит адрес курсанта")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
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
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " отправил адрес курсанта")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    user_data = await state.get_data()
    await put_address_from_coords(collection, user_data['user_id'], message.text)
    await message.answer('Адрес отправлен в базу данных!', reply_markup=kb.back_address_keyboard)
    await state.set_state(Address.get_dop_address)
@router.callback_query(F.data == 'put_address_dop')
async def put_address_dop(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователю с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " предложено ввести следующий адрес проживания")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await callback.message.answer('Введите следующий адрес проживания.', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Address.get_address)
@router.callback_query(F.data == 'put_address_end')
async def put_address_end(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователю с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " предложено вернуться в меню или перейти к следующему курсанту")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    user_data = await state.get_data()
    await save_kursant_address(collection, user_data['user_id'])
    await callback.message.answer('Вернуться в меню или продолжить вводить адреса других курсантов?', reply_markup=kb.back_address_next_keyboard)
    await state.set_state(Address.begin)
@router.callback_query(F.data == 'reset_address_key')
async def reset_address_key(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " хочет обновить свои адреса проживания")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await reset_address(collection, callback.from_user.id)
    await callback.message.answer('База данных готова к обновлению места проживания.', reply_markup=kb.back_keyboard)
#Ввод адресов проживания. Конец

@router.callback_query(F.data == 'prinyt_doklad')
async def prinyt_doklad(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " принимает доклад у своих подчиненных")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await get_video_note(collection, callback.from_user.id, callback, kb)
    await find_report(collection, callback.from_user.id, callback, kb)

@router.callback_query(F.data == 'create_map_knopka')
async def create_map_knopka(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " создаёт карту обстановки")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await create_map(collection, callback.from_user.id, callback, kb)


@router.callback_query(F.data == 'put_address_me')
async def put_address_me(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " вводит себе адрес проживания")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await callback.message.answer('Введите адрес проживания (место проведения отпуска) по образцу: г. Санкт-Петербург, п. Шушары, ул. Школьная , д. 26, кв.51',reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Address_me.get_address_me)

@router.message(Address_me.get_address_me)
async def get_address_me(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " отправляет адрес проживания")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await put_address_from_coords(collection, message.from_user.id, message.text)
    await message.answer('Адрес отправлен в базу данных!', reply_markup=kb.back_keyboard)

@router.callback_query(F.data == 'about')
async def about(callback: CallbackQuery):
    await callback.message.answer('Спасибо за то, что принимаете участие в апробации данного бота. Для тех, кому интересно, заходите на мой гитхаб, ставьте звездочки, интересуйтесь разработками дальше! https://github.com/maksshirk/CadetReport', reply_markup=kb.back_keyboard)


#@router.message()
#async def choose_your_dinner():
#    await Bot.send_message(chat_id=479947781, text="Хей🖖")

#async def scheduler():
#    aioschedule.every().day.at("15:47").do(choose_your_dinner)
#    while True:
#        await aioschedule.run_pending()
#        await asyncio.sleep(1)

#async def on_startup(dp):
#    asyncio.create_task(scheduler())


@router.callback_query(F.data == 'status_change')
async def status_change(callback: CallbackQuery, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " меняет статус")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    try:
        kursant = await collection.find_one({"user_id": callback.from_user.id})
        await callback.message.answer('Ваш статус:\n{}'.format(kursant['Present']['user_status'] + "\n Для того чтобы изменить статус нажмите на одну из нижеуказанных кнопок. Если кнопки закрылись, нажмите на 'шоколадку' слева от кнопки отправить"),
                                       reply_markup=kb.status_keyboard)
        await state.update_data(user_id=kursant['user_id'])
        await state.set_state(Status_change.Status_change_get)
    except Exception as e:
        await callback.message.answer('Ошибка(', reply_markup=kb.back_keyboard)
@router.message(Status_change.Status_change_get)
async def Status_change_get(message: types.Message, state: FSMContext):
    try:
        logging.info("Пользователь с ID: " + str(message.from_user.id) + " " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + " поменял статус на: " + message.text)
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    user_data = await state.get_data()
    await collection.update_one ({"user_id":user_data['user_id']},
                                    {"$set": {
                                        "Present.user_status": message.text
                                            }
                                    })
    await message.answer('Статус изменён!', reply_markup=types.ReplyKeyboardRemove())
    await message.answer('Вернитесь в меню!', reply_markup=kb.back_keyboard)

@router.callback_query(F.data == 'prinyt_doklad_fast')
async def prinyt_doklad_fast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " принял краткий доклад")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    await find_report_fast(collection, callback.from_user.id, callback, kb)

@router.callback_query(F.data == 'get_log')
async def get_log(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " запросил лог-файл")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    file_name = "py_log.log"
    file_name = FSInputFile(file_name)
    await callback.message.answer_document(file_name)
    await callback.message.answer('Вот вам лог-файл со всей свежатиной!)', reply_markup=kb.back_keyboard)

@router.callback_query(F.data == 'get_all')
async def get_all(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        logging.info("Пользователь с ID: " + str(callback.from_user.id) + " " + str(callback.from_user.last_name) + " " + str(callback.from_user.first_name) + " запросил список всех, кто есть в БД")
    except Exception as ex:
        logging.info("Ошибка логирования: " + str(ex))
    cur = collection.find()
    score = 0
    all_people = "<br><b>Полный список:</b><br>"
    async for doc in cur:
        all_people = all_people + str(score) + ". " + str(doc["user_id"]) + " " + str(doc["first_name"]) + " " + str(doc["last_name"]) + "<br>"
        score = score + 1
    f = codecs.open("Report/Список БД.html", 'w', "utf-8")
    f.write(all_people)
    f.close()
    file_name = FSInputFile("Report/Список БД.html")
    await callback.message.answer_document(file_name)
    await callback.message.answer('Вот полный список всех юзеров!', reply_markup=kb.back_keyboard)