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

get_number_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер. Нажми на меня', request_contact = True)]], resize_keyboard= True, input_field_placeholder='Используй кнопку ниже для отправки номера!')

access_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все правильно! Вперёд!', callback_data='registration_ok')],
    [InlineKeyboardButton(text='Данные неправильные! Заново пройти регистрацию!', callback_data='registration')]
], resize_keyboard= True)

kursant_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Добавить адрес проживания (место проведения отпуска)', callback_data='put_address_me')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')],
    [InlineKeyboardButton(text='В помощь курсанту (руководящие документы и т.д.)', callback_data='get_help')],
    [InlineKeyboardButton(text='При наличии уникального номера принять информацию', callback_data='dovedenie_info')],
    #[InlineKeyboardButton(text='У меня обновились сведения по месту проживания', callback_data='reset_address_key')],
    [InlineKeyboardButton(text='Заново пройти регистрацию', callback_data='registration')],
    #[InlineKeyboardButton(text='О разработке бота', callback_data='about')]
], resize_keyboard= True)

komandir_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Довести информацию до подчиненных', callback_data='dovedenie')],
    [InlineKeyboardButton(text='Проверить, до кого доведена информация', callback_data='check_dovedenie')],
    [InlineKeyboardButton(text='Принять доклад от подчиненных', callback_data='prinyt_doklad')],
    [InlineKeyboardButton(text='Добавить адрес проживания (место проведения отпуска)', callback_data='put_address_me')],
    [InlineKeyboardButton(text='Изменить статус подчиненному', callback_data='status_change_kursant')],
    [InlineKeyboardButton(text='В помощь курсанту (руководящие документы и т.д.)', callback_data='get_help')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')],
    [InlineKeyboardButton(text='При наличии уникального номера принять информацию', callback_data='dovedenie_info')],
    #[InlineKeyboardButton(text='У меня обновились сведения по месту проживания', callback_data='reset_address_key')],
    [InlineKeyboardButton(text='Заново пройти регистрацию', callback_data='registration')],
    #[InlineKeyboardButton(text='О разработке бота', callback_data='about')]
], resize_keyboard= True)

nachalnik_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Довести информацию до подчиненных', callback_data='dovedenie')],
    [InlineKeyboardButton(text='Проверить, до кого доведена информация', callback_data='check_dovedenie')],
    [InlineKeyboardButton(text='Кратко принять доклад от подчиненных', callback_data='prinyt_doklad_fast')],
    [InlineKeyboardButton(text='Принять доклад от подчиненных в полной форме', callback_data='prinyt_doklad')],
    [InlineKeyboardButton(text='Создать карту обстановки', callback_data='create_map_knopka')],
    [InlineKeyboardButton(text='В помощь курсанту (руководящие документы и т.д.)', callback_data='get_help')],
    [InlineKeyboardButton(text='Ввести адреса проживания', callback_data='put_address')],
    [InlineKeyboardButton(text='Добавить адрес проживания (место проведения отпуска)', callback_data='put_address_me')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')],
    [InlineKeyboardButton(text='Изменить статус подчиненному', callback_data='status_change_kursant')],
    [InlineKeyboardButton(text='Получить лог-файл (проверить действия с ботом, помогает в сложных ситуациях)', callback_data='get_log')],
    [InlineKeyboardButton(text='Вывести список всех, кто зарегистрирован в БД', callback_data='get_all')],
    [InlineKeyboardButton(text='При наличии уникального номера принять информацию', callback_data='dovedenie_info')],
    #[InlineKeyboardButton(text='У меня обновились сведения по месту проживания', callback_data='reset_address_key')],
    [InlineKeyboardButton(text='Заново пройти регистрацию', callback_data='registration')],
    #[InlineKeyboardButton(text='О разработке бота', callback_data='about')]
], resize_keyboard= True)

geo_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить координаты. Нажми на меня', request_location=True)]], resize_keyboard= True, input_field_placeholder='Используй кнопку ниже для отправки геолокации!')

back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]
], resize_keyboard= True)

dovedenie_ok_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Информация получена!', callback_data='dovedenie_info')]
], resize_keyboard= True)

back_address_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввести еще один адрес данному курсанту', callback_data='put_address_dop')],
    [InlineKeyboardButton(text='Закончить ввод адресов', callback_data='put_address_end')]
], resize_keyboard= True)

back_address_next_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввести адрес следующего курсанта', callback_data='put_address')],
    [InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]
], resize_keyboard= True)

get_help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='РУКОВОДЯЩИЕ ДОКУМЕНТЫ', callback_data='get_help_rukdok')],
    [InlineKeyboardButton(text='Кинофильмы', callback_data='get_help_kino')],
    [InlineKeyboardButton(text='Литературные произведения', callback_data='get_help_knigi')],
    [InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]
], resize_keyboard= True)

get_help_kino_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Чапаев (1934)')],
    [KeyboardButton(text='Повесть о настоящем человеке (1948)')],
    [KeyboardButton(text='Добровольцы (1958)')],
    [KeyboardButton(text='Обыкновенный фашизм (1965)')],
    [KeyboardButton(text='Офицеры (1972)')],
    [KeyboardButton(text='В бой идут одни старики (1973)')],
    [KeyboardButton(text='Они сражались за Родину (1975)')],
    [KeyboardButton(text='Брестская крепость (2010)')],
    [KeyboardButton(text='Легенда 17 (2013)')],
    [KeyboardButton(text='28 панфиловцев (2016)')],
    [KeyboardButton(text='Движение вверх (2017)')],
    [KeyboardButton(text='Время первых (2017)')],
    [KeyboardButton(text='Сто шагов (2019)')],
    [KeyboardButton(text='Ржев (2019)')],
    [KeyboardButton(text='Балканский рублеж (2019)')],
    [KeyboardButton(text='Лев Яшин. Вратарь моей мечты (2019)')],
    [KeyboardButton(text='Жила-была девочка (1944)')],
    [KeyboardButton(text='Мы смерти смотрели в лицо (1980)')],
    [KeyboardButton(text='Порох (1985)')],
    [KeyboardButton(text='Зимнее утро (1966)')],
    [KeyboardButton(text='Блокада (1973-1977)')],
    [KeyboardButton(text='Коридор бессмертия (2019)')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите кинофильм для скачивания!')

get_help_rukdok_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Общевоинские уставы ВС РФ')],
    [KeyboardButton(text='Уголовный кодекс')],
    [KeyboardButton(text='Вопросы прохождения службы')],
    [KeyboardButton(text='О статусе военнослужащих')],
    [KeyboardButton(text='Военная доктрина')],
    [KeyboardButton(text='Инструктаж в отпуск')],
    [KeyboardButton(text='КоАП РФ')],
    [KeyboardButton(text='О вещевом обеспечении')],
    [KeyboardButton(text='О воинской обязанности и военной службе')],
    [KeyboardButton(text='О государственной тайне')],
    [KeyboardButton(text='О продовольственном обеспечении')],
    [KeyboardButton(text='О финансовом обеспечении')],
    [KeyboardButton(text='Об обороне')],
    [KeyboardButton(text='Памятка БДД')],
    [KeyboardButton(text='Перечни рекомендуемых и обязательных книг и фильмов')],
    [KeyboardButton(text='Пособие для ВВУЗОВ по COVID-19')],
    [KeyboardButton(text='Приказ МО РФ 2017 по ВПД')],
    [KeyboardButton(text='Проверка и оценка ФП')],
    [KeyboardButton(text='Трудовой кодекс')],
    [KeyboardButton(text='Пособие для ВВУЗОВ по COVID-19')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите руководящий документ для скачивания!')

get_help_knigi_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Русский характер. Толстой А.Н.')],
    [KeyboardButton(text='Волоколамское шоссе. Бек А.А.')],
    [KeyboardButton(text='Взять живым! Карпов В.В.')],
    [KeyboardButton(text='Горячий снег. Бондарев Ю.В.')],
    [KeyboardButton(text='Генералиссимус Суворов. Раковский Л.И.')],
    [KeyboardButton(text='Василий Теркин. Твардовский А.Т.')],
    [KeyboardButton(text='Навеки девятнадцатилетник. Бакланов Г.Я.')],
    [KeyboardButton(text='Героев славных имена. Сборник очерков')],
    [KeyboardButton(text='Доклад начальника академии об образовании академии')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите литературу для скачивания!')

go_report_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доклад о состоянии дел', callback_data='doklad')],
    [InlineKeyboardButton(text='Изменить статус (В наряде, в казарме, в госпитале и т.д.)', callback_data='status_change')]
], resize_keyboard= True)