from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Регистрация', callback_data='registration')]
])

year_nabor_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='2021'), KeyboardButton(text='2022')],
    [KeyboardButton(text='2023'), KeyboardButton(text='2024')],
    [KeyboardButton(text='2025')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите год поступления в академию')

fakultet_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='1'), KeyboardButton(text='2'),
    KeyboardButton(text='3'), KeyboardButton(text='4'),
    KeyboardButton(text='5')], [KeyboardButton(text='6'),
    KeyboardButton(text='7'), KeyboardButton(text='8'),
    KeyboardButton(text='9')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите факультет')

kafedra_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Управление факультета')],
    [KeyboardButton(text='1'), KeyboardButton(text='2'),
    KeyboardButton(text='3'), KeyboardButton(text='4'),
    KeyboardButton(text='5')], [KeyboardButton(text='6'),
    KeyboardButton(text='7')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите кафедру')

podgruppa_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='На моей кафедре/в управлении нет подгрупп')],
    [KeyboardButton(text='/1'),
     KeyboardButton(text='/2'),
     KeyboardButton(text='/3'),
     KeyboardButton(text='/4')]],
    resize_keyboard=True,
    input_field_placeholder='В какой Вы подгруппе?')

position_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начальник курса'),KeyboardButton(text='Курсовой офицер')],
     [KeyboardButton(text='Старшина курса'),KeyboardButton(text='Командир учебной группы')],
    [KeyboardButton(text='Командир 1 отд-я'),KeyboardButton(text='Командир 2 отд-я'),KeyboardButton(text='Командир 3 отд-я')],
    [KeyboardButton(text='Курсант 1 отд-я'),KeyboardButton(text='Курсант 2 отд-я'),KeyboardButton(text='Курсант 3 отд-я')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите должность')

status_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Вне общежития'),KeyboardButton(text='В отпуске')],
     [KeyboardButton(text='В госпитале'),KeyboardButton(text='В наряде')],
    [KeyboardButton(text='В казарме'),KeyboardButton(text='В лазарете')],
    [KeyboardButton(text='В увольнении'),KeyboardButton(text='В командировке')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите статус')

get_number_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер. Нажми на меня', request_contact = True)]], resize_keyboard= True)

access_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все правильно! Вперёд!', callback_data='registration_ok')],
    [InlineKeyboardButton(text='Данные неправильные! Заново пройти регистрацию!', callback_data='registration')]
], resize_keyboard= True)

kursant_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Добавить адрес проживания (место проведения отпуска)', callback_data='put_address_me')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')],
    #[InlineKeyboardButton(text='У меня обновились сведения по месту проживания', callback_data='reset_address_key')],
    [InlineKeyboardButton(text='Заново пройти регистрацию', callback_data='registration')],
    #[InlineKeyboardButton(text='О разработке бота', callback_data='about')]
], resize_keyboard= True)

komandir_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Принять доклад от подчиненных', callback_data='prinyt_doklad')],
    [InlineKeyboardButton(text='Добавить адрес проживания (место проведения отпуска)', callback_data='put_address_me')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')],
    #[InlineKeyboardButton(text='У меня обновились сведения по месту проживания', callback_data='reset_address_key')],
    [InlineKeyboardButton(text='Заново пройти регистрацию', callback_data='registration')],
    #[InlineKeyboardButton(text='О разработке бота', callback_data='about')]
], resize_keyboard= True)

nachalnik_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Кратко принять доклад от подчиненных', callback_data='prinyt_doklad_fast')],
    [InlineKeyboardButton(text='Принять доклад от подчиненных в полной форме', callback_data='prinyt_doklad')],
    [InlineKeyboardButton(text='Создать карту обстановки', callback_data='create_map_knopka')],
    [InlineKeyboardButton(text='Ввести адреса проживания', callback_data='put_address')],
    [InlineKeyboardButton(text='Добавить адрес проживания (место проведения отпуска)', callback_data='put_address_me')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')],
    #[InlineKeyboardButton(text='У меня обновились сведения по месту проживания', callback_data='reset_address_key')],
    [InlineKeyboardButton(text='Заново пройти регистрацию', callback_data='registration')],
    #[InlineKeyboardButton(text='О разработке бота', callback_data='about')]
], resize_keyboard= True)

geo_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить координаты. Нажми на меня', request_location=True)]], resize_keyboard= True)

back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]
], resize_keyboard= True)

back_address_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввести еще один адрес данному курсанту', callback_data='put_address_dop')],
    [InlineKeyboardButton(text='Закончить ввод адресов', callback_data='put_address_end')]
], resize_keyboard= True)

back_address_next_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввести адрес следующего курсанта', callback_data='put_address')],
    [InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]
], resize_keyboard= True)