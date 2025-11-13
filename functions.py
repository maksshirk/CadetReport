import datetime, folium, zipfile, shutil, codecs
from aiogram.types import FSInputFile
from time import gmtime, strftime
from settings import YANDEX_TOKEN
from yandex_geocoder import Client
from geopy.distance import geodesic

async def search_or_save_user(collection, effective_user, message):
    user = await collection.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": message.id,
            "Present": {"check_present": 0}
        }
        collection.insert_one(user)
    return user

async def search_or_save_user_menu(collection, effective_user):
    user = await collection.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": effective_user.id,
            "Present": {"check_present": 0}
        }
        collection.insert_one(user)
    return user

async def check_point(collection, effective_user):
    check = await collection.find_one({"user_id": effective_user.id})
    try:
        return check['Present']['check_present']
    except Exception as e:
        return 0

async def check_point_menu(collection, effective_user):
    check = await collection.find_one({"user_id": effective_user})
    try:
        return check['Present']['check_present']
    except Exception as e:
        return 0

async def save_kursant_anketa(collection, user_data):
    check_present = 1
    if user_data['kafedra'] != "Управление факультета":
        user_data['kafedra'] = int(user_data['fakultet']) * 100 + (int(user_data['year_nabor']) % 10) * 10 + int(user_data['kafedra'])
    user_data["podgruppa"] = user_data["podgruppa"].replace("/", "-", count=-1)
    if user_data['position'] != "Курсант": check_present = 1
    if user_data['position'] == "Начальник курса" or user_data['position'] == "Курсовой офицер" or user_data['position'] == "Старшина курса": check_present = 3
    if user_data['position'] == "Командир учебной группы" or user_data['position'] == "Командир 1 отд-я" or user_data['position'] == "Командир 2 отд-я" or user_data['position'] == "Командир 3 отд-я": check_present = 2
    await collection.update_one({'user_id': user_data['id']}, {'$set': {'Present': {
        'year_nabor': user_data['year_nabor'],
        'fakultet': user_data['fakultet'],
        'user_group': str(user_data['kafedra']) + user_data["podgruppa"],
        'user_unit': user_data['position'],
        'user_lastname': user_data['last_name'],
        'user_name': user_data['name'],
        'user_middlename': user_data['middle_name'],
        'user_phone': user_data['phone_number'],
        'user_status': 'Вне общежития',
        'check_present': check_present,
        "count": 0
    }}})
    return 0

async def save_user_location(collection, user, location):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        r = "morning"
    else:
        r = "evening"
    s = time.strftime("%H-%M-%S")
    b = datetime.datetime.now()
    b = b.strftime("%d-%m-%Y")
    number = await number_Facts(collection, user, b, r)
    number = int(number) + 1
    time_of_day = "number " + str(r)
    Facts_number = "Facts." + b + "." + time_of_day
    await collection.update_many(
        {'user_id': user['id']},
        {'$set': {Facts_number:
            {
                'number': number}
        }
        })
    r = str(number) + " " + r
    Facts = "Facts." + b + "." + r
    await collection.update_many(
        {'user_id': user['id']},
        {'$set': {Facts:
                      {
                      'time': s,
                      'latitude': location.latitude,
                      'longitude': location.longitude,
                      'number': number,
                      'uid': user['uid']}
                  }
         })
    return user

async def number_Facts(collection, user, b, r):
    check = await collection.find_one({"user_id": user['id']})
    r = str(r) + " number"
    try:
        number = check['Facts'][b][r]["number"]
    except Exception as ex:
        number = 0
    return number

async def lastname(collection, effective_user):
    check = await collection.find_one({"user_id": effective_user})
    return check['Present']['user_lastname']

async def get_group(collection, effective_user):
    check = await collection.find_one({"user_id": effective_user})
    return check['Present']['user_group']

async def poisk_kursanta(collection, effective_user):
    nachalnik = await collection.find_one({"user_id": effective_user})
    year_nabor = nachalnik['Present']['year_nabor']
    fakultet = nachalnik['Present']['fakultet']
    user = await collection.find_one({
        "Present.year_nabor": year_nabor,
        "Present.fakultet": fakultet,
        "Present.count": 0
    })
    return user

async def put_address_from_coords(collection, user_id, address):
    try:
        client = Client(YANDEX_TOKEN)
        coordinates = client.coordinates(address)
        user = await collection.find_one({"user_id": user_id})
        try:
            count = user['Present']['address']['count']
            count = count + 1
        except Exception as e:
            count = 0
        await collection.update_one ({"user_id":user_id},
                                    {"$set": {
                                        "Present.address."+str(count):{
                                            "latitude": str(coordinates[1]),
                                            "longitude": str(coordinates[0]),
                                            "address":address
                                            },
                                        "Present.address.count": count

                                    }})
    except Exception as e:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Ошибка в блоке отправки адреса базу данных: " + str(e))

async def save_kursant_address(collection, user_id):
    try:
        await collection.update_one ({"user_id":user_id},
                                    {"$set": {
                                        "Present.count": 1
                                            }
                                    })
    except Exception as e:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Ошибка в блоке изменения статуса адреса курсанта: " + str(e))

async def reset_address(collection, user_id):
    try:
        await collection.update_one ({"user_id":user_id},
                                    {"$set": {
                                        "Present.count": 0
                                    }})
    except Exception as e:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Ошибка в блоке обнуления адреса курсанта: " + str(e))




async def find_report(collection, user_id, callback,kb):
    nachalnik = await collection.find_one({"user_id": user_id})
    year_nabor = nachalnik['Present']['year_nabor']
    fakultet = nachalnik['Present']['fakultet']
    user_group = nachalnik['Present']['user_group']
    user_unit = nachalnik['Present']['user_unit']
    if user_unit == "Начальник курса" or user_unit == "Курсовой офицер" or user_unit == "Старшина курса":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet
        })
    if user_unit == "НФ" or user_unit == "ЗНФ":
        cur = collection.find({
            "Present.fakultet": fakultet
        })
    if user_unit == "Командир учебной группы":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group
        })
    if user_unit == "Командир 1 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 1 отд-я"
        })
    if user_unit == "Командир 2 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 2 отд-я"
        })
    if user_unit == "Командир 3 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 3 отд-я"
        })
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    all_ok = "<span style='background-color:#00FF00'><b>Курсанты не имеющие проблем на данный момент:</b><br>"
    not_ok = "</span><br><span style='background-color:#FF0000'><b>Курсанты, не совершившие доклад:</b><br>"
    on_service = "<br><b>Курсанты, находящиеся в наряде:</b><br>"
    lazaret = "<br><b>Курсанты, находящиеся в лазарете:</b><br>"
    kazarma = "<br><b>Курсанты, находящиеся в казарме:</b><br>"
    score_all_ok = 0
    score_not_ok = 0
    score_on_service = 0
    score_lazaret = 0
    score_kazarma = 0
    score_otpusk = 0
    score_hospital = 0
    score_yvolnenie = 0
    score_komandirovka = 0
    score_vnekazarm = 0
    cur = cur.sort("Present.user_group", 1)
    async for doc in cur:
        if doc["Present"]['user_unit'] == "Начальник курса" or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
            continue
        if doc["Present"]['user_status'] == "В наряде":
            score_on_service = score_on_service + 1
            on_service = on_service + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_on_service) + ".</b>" + \
                     doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                         "user_middlename"] + "<br>"
            continue
        if doc["Present"]['user_status'] == "В лазарете":
            score_lazaret = score_lazaret + 1
            lazaret = lazaret + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_lazaret) + ".</b>" + \
                     doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                         "user_middlename"] + "<br>"
            continue
        if doc["Present"]['user_status'] == "В казарме":
            score_kazarma = score_kazarma + 1
            kazarma = kazarma + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_kazarma) + ".</b>" + \
                     doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                         "user_middlename"] + "<br>"
            continue
        if doc["Present"]['user_status'] == "В отпуске":
            score_otpusk = score_otpusk + 1
        if doc["Present"]['user_status'] == "В госпитале":
            score_hospital = score_hospital + 1
        if doc["Present"]['user_status'] == "В увольнении":
            score_yvolnenie = score_yvolnenie + 1
        if doc["Present"]['user_status'] == "В командировке":
            score_komandirovka = score_komandirovka + 1
        if doc["Present"]['user_status'] == "Вне общежития":
            score_vnekazarm = score_vnekazarm + 1
        number = "number " + time_of_day
        i_min = 0
        try:
            number = doc["Facts"][day][number]["number"]
            number = str(number) + " " + time_of_day
            score_all_ok = score_all_ok + 1
            try:
                count_address = doc["Present"]["address"]["count"]
                i = 0
                distance = []
                while i <= count_address:
                    home = (float(doc["Present"]["address"][str(i)]["latitude"]), float(doc["Present"]["address"][str(i)]["longitude"]))
                    point = (float(doc["Facts"][day][number]["latitude"]), float(doc["Facts"][day][number]["longitude"]))
                    distance.append(geodesic(point, home).m)
                    i = i + 1
                i = 0
                distance_min = 10000000000
                while i <= count_address:
                    home = (float(doc["Present"]["address"][str(i)]["latitude"]),
                            float(doc["Present"]["address"][str(i)]["longitude"]))
                    point = (float(doc["Facts"][day][number]["latitude"]),
                             float(doc["Facts"][day][number]["longitude"]))
                    if geodesic(point, home).m <= distance_min:
                        distance_min = geodesic(point, home).m
                        i_min = i
                    i = i + 1
                if min(distance) < 500:
                    all_ok = all_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_all_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>"\
                             + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + " <b>Место отметки: </b>" + str(doc["Facts"][day][number]["latitude"]) + ", " + str(doc["Facts"][day][number]["longitude"]) + "<br>" \
                             + "\n<b>Расстояние до места проживания: </b>" + str(round(min(distance))) + " метров<br><span style='background-color:#00FF00'>"
                else:
                    all_ok = all_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_all_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>"\
                             + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + " <b>Место отметки: </b>" + str(doc["Facts"][day][number]["latitude"]) + ", " + str(doc["Facts"][day][number]["longitude"]) + "<br>" \
                             + "\n<span style='background-color:#FF0000'><b>Расстояние до места проживания: </b>" + str(round(min(distance))) + " метров</span> <b>Место проживания: </b>" + doc["Present"]["address"][str(i_min)]["address"] + ". <b>Координаты: </b>" + str(doc["Present"]["address"][str(i_min)]["latitude"]) + ", " + str(doc["Present"]["address"][str(i_min)]["longitude"]) + "<span style='background-color:#00FF00'><br>"
            except Exception as ex:
                all_ok = all_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_all_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>" \
                         + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + " <b>Место отметки: </b>" + str(doc["Facts"][day][number]["latitude"]) + ", " + str(doc["Facts"][day][number]["longitude"]) + "<br>" \
                         + "\n<span style='background-color:#FF0000'><b>У курсанта командованием курса не введены адреса проживания!</b></span><span style='background-color:#00FF00'>" + "<br>"
        except Exception as ex:
            score_not_ok = score_not_ok + 1
            try:
                not_ok = not_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_not_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + \
                     doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>" + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] + "<br>\n<b>Место проживания: </b>" + doc["Present"]["address"][str(i_min)]["address"] + ". <b>Координаты: </b>" + str(doc["Present"]["address"][str(i_min)]["latitude"]) + ", " + str(doc["Present"]["address"][str(i_min)]["longitude"]) + "\n<br><span style='background-color:#FF0000'>"
            except Exception as ex:
                not_ok = not_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_not_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + \
                     doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>" + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] + "<br> <b>Больше данных нет на военнослужащего.</b><br>\n<span style='background-color:#FF0000'>"

    f = open("Report/" + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html", 'w')
    itog = "<b>В системе зарегистрировано: </b>" + str(score_otpusk+score_komandirovka+score_kazarma+score_lazaret+score_hospital+score_yvolnenie+score_on_service+score_vnekazarm) + "<br>" + \
           "<b>Доклад поступил (включая отпуск, командировку, увольнение, госпиталь): </b>" +  str(score_all_ok) + "<br>" + \
           "<b>Доклад не поступил: </b>" + str(score_not_ok) + "<br>" + \
            "<b>В казарме: </b>" + str(score_kazarma) + "<br>" + \
            "<b>В лазарете: </b>" + str(score_lazaret) + "<br>" + \
            "<b>В наряде: </b>" + str(score_on_service) + "<br>"
    f.write(itog + all_ok + "\n" + not_ok + "\n</span>" + kazarma + "\n" + on_service + "\n" + lazaret)
    f.close()
    f = FSInputFile("Report/" + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html")
    await callback.message.answer_document(f)
    await callback.message.answer("Полный доклад в файле выше.\n", reply_markup=kb.back_keyboard)

async def info_account(collection, user_id):
    kursant = await collection.find_one({"user_id": user_id})
    info = ("Информация о Вашем аккаунте из базы данных:\n"
            "<b>Факультет:</b> " + kursant["Present"]["fakultet"] + "\n"
            "<b>Год набора:</b> " + kursant["Present"]["year_nabor"] + "\n"
            "<b>Учебная группа:</b> " + kursant["Present"]["user_group"] + "\n"
            "<b>Должность:</b> " + kursant["Present"]["user_unit"] + "\n"
            "<b>ФИО:</b> " + kursant["Present"]["user_lastname"] + " " + kursant["Present"]["user_name"] + " " + kursant["Present"]["user_middlename"] + "\n"
            "<b>Номер телефона:</b> " + kursant["Present"]["user_phone"] + "\n"
            "<b>Статус:</b> " + kursant["Present"]["user_status"] + "\n"
            "<b>Адреса проживания (включая при нахождении в отпуске). Для внесения изменений обратитесь к @maksshirk:</b> \n"
            )
    try:
        count = kursant["Present"]["address"]["count"]
        i = 0
        while i <= count:
            info = info + str(i + 1) + ". " + kursant["Present"]["address"][str(i)]["address"] + "\n"
            i = i + 1
    except Exception as ex:
        info = info + "В базе данных адреса отсутствуют\n"
    return info



async def create_map(collection, user_id, callback, kb):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    hour = time.strftime("%H-%M-%S")
    map = folium.Map(location=[59.812019, 30.378742], zoom_start = 8)
    nachalnik = await collection.find_one({"user_id": user_id})
    year_nabor = nachalnik['Present']['year_nabor']
    fakultet = nachalnik['Present']['fakultet']
    user_group = nachalnik['Present']['user_group']
    user_unit = nachalnik['Present']['user_unit']
    text_for_yandex = ""
    yandex_count = 1
    if user_unit == "Начальник курса" or user_unit == "Курсовой офицер" or user_unit == "Старшина курса":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet
        })
    if user_unit == "НФ" or user_unit == "ЗНФ":
        cur = collection.find({
            "Present.fakultet": fakultet
        })
    if user_unit == "Командир учебной группы":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group
        })
    if user_unit == "Командир 1 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 1 отд-я"
        })
    if user_unit == "Командир 2 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 2 отд-я"
        })
    if user_unit == "Командир 3 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 3 отд-я"
        })
    async for doc in cur:
        if doc["Present"]['user_unit'] == "Начальник курса" or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
            continue
        if doc["Present"]['user_status'] == "D " or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
            continue
        number = "number " + time_of_day
        try:
            number = doc["Facts"][day][number]["number"]
            number = str(number) + " " + time_of_day
            try:
                try:
                    Family = "<p><b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"][
                        "user_name_mother"] + " " + \
                             doc["SOS"]["user_middlename_mother"] \
                             + "<p><b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                             + "<p><b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                             + "<p><b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"][
                                 "user_name_father"] + " " + \
                             doc["SOS"]["user_middlename_father"] \
                             + "<p><b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                             + "<p><b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                             + "<p><b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + \
                             doc["SOS"][
                                 "user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                             + "<p><b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                             + "<p><b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                except Exception as ex:
                    Family = "<p>Данных о семье нет"
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + Family
                P_latitude = float(doc["Facts"][day][number]["latitude"])
                P_longitude = float(doc["Facts"][day][number]["longitude"])
                popuptext = user_name.replace('\n', ' ')
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                text_for_yandex = text_for_yandex + "\nvar myPlacemark" + str(yandex_count) + " = new ymaps.Placemark([" + str(P_latitude) + "," +  str(P_longitude) + '],{\n' + "hintContent: '"  + popuptext + "' ,\n" + "balloonContentHeader: '"  + popuptext + "',\n" + "},{\n" + "preset: 'islands#grayDotIcon'\n" + "});\n" + "myMap.geoObjects.add(myPlacemark" + str(yandex_count) + ");\n"
                folium.Marker(location=[P_latitude, P_longitude], popup= popup, icon=folium.Icon(color = 'gray')).add_to(map)
                H_latitude_min = 59.825976
                H_longitude_min = 30.380312
                distance = 10000000000000
                try:
                    count = doc["Present"]["address"]["count"]
                    i = 0
                    while i <= count:
                        H_latitude = float(doc["Present"]["address"][str(i)]["latitude"])
                        H_longitude = float(doc["Present"]["address"][str(i)]["longitude"])
                        home = (H_latitude, H_longitude)
                        point = (P_latitude, P_longitude)
                        if geodesic(point, home).m <= distance:
                            distance = geodesic(point, home).m
                            H_latitude_min = H_latitude
                            H_longitude_min = H_longitude
                            i_min = i
                        i = i + 1
                    user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + \
                                doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + " <p>" + \
                                doc["Present"]["address"][str(i_min)]["address"]
                    popuptext = user_name.replace('\n', ' ')
                    iframe = folium.Html(popuptext, script=True)
                    popup = folium.Popup(iframe, max_width=300, min_width=300)
                    folium.Marker(location=[H_latitude_min, H_longitude_min], popup=popup, icon=folium.Icon(color='blue', icon='home')).add_to(map)
                    text_for_yandex = text_for_yandex + "\nvar myPlacemark" + str(yandex_count) + " = new ymaps.Placemark([" + str(H_latitude_min) + "," + str(H_longitude_min) + '],{\n' + "hintContent: '" + popuptext + "' ,\n" + "balloonContentHeader: '" + popuptext + "',\n" + "},{\n" + "preset: 'islands#blueDotIcon'\n" + "});\n" + "myMap.geoObjects.add(myPlacemark" + str(yandex_count) + ");\n"
                except Exception as ex:
                    pass
                text_for_yandex = text_for_yandex + "\nlet myPolyline" + str(yandex_count) + " = new ymaps.Polyline([\n[" + str(P_latitude) + "," + str(P_longitude) + '],\n[' + str(H_latitude_min) + "," + str(H_longitude_min) + ']\n]);\n' + "myMap.geoObjects.add(myPolyline" + str(yandex_count) + ");\n"
                folium.PolyLine(locations=[(P_latitude, P_longitude), (H_latitude_min, H_longitude_min)], line_opacity=0.5).add_to(map)

            except Exception as ex:
                try:
                    Family = "<p><b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"][
                        "user_name_mother"] + " " + \
                             doc["SOS"]["user_middlename_mother"] \
                             + "<p><b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                             + "<p><b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                             + "<p><b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"][
                                 "user_name_father"] + " " + \
                             doc["SOS"]["user_middlename_father"] \
                             + "<p><b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                             + "<p><b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                             + "<p><b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + \
                             doc["SOS"][
                                 "user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                             + "<p><b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                             + "<p><b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                except Exception as ex:
                    Family = "<p>Данных о семье нет"
                try:
                    count = doc["Present"]["address"]["count"]
                    i = 0
                    while i <= count:
                        H_latitude = float(doc["Present"]["address"][str(i)]["latitude"])
                        H_longitude = float(doc["Present"]["address"][str(i)]["longitude"])
                        user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + " <p>" + doc["Present"]["address"][str(i)]["address"]
                        popuptext = user_name.replace('\n', ' ')
                        iframe = folium.Html(popuptext, script=True)
                        popup = folium.Popup(iframe, max_width=300, min_width=300)
                        folium.Marker(location=[H_latitude, H_longitude], popup=popup, icon=folium.Icon(color='red', icon='home')).add_to(map)
                        text_for_yandex = text_for_yandex + "\nvar myPlacemark" + str(yandex_count) + " = new ymaps.Placemark([" + str(H_latitude) + "," + str(H_longitude) + '],{\n' + "hintContent: '" + popuptext + "' ,\n" + "balloonContentHeader: '" + popuptext + "',\n" + "},{\n" + "preset: 'islands#redDotIcon'\n" + "});\n" + "myMap.geoObjects.add(myPlacemark" + str(yandex_count) + ");\n"
                        i = i + 1
                except Exception as ex:
                    pass
        except Exception as ex:
            try:
                try:
                    Family = "<p><b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"][
                        "user_name_mother"] + " " + \
                             doc["SOS"]["user_middlename_mother"] \
                             + "<p><b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                             + "<p><b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                             + "<p><b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"][
                                 "user_name_father"] + " " + \
                             doc["SOS"]["user_middlename_father"] \
                             + "<p><b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                             + "<p><b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                             + "<p><b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + \
                             doc["SOS"][
                                 "user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                             + "<p><b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                             + "<p><b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                except Exception as ex:
                    Family = "<p>Данных о семье нет"
                try:
                    count = doc["Present"]["address"]["count"]
                    i = 0
                    while i <= count:
                        H_latitude = float(doc["Present"]["address"][str(i)]["latitude"])
                        H_longitude = float(doc["Present"]["address"][str(i)]["longitude"])
                        user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + " <p>" + doc["Present"]["address"][str(i)]["address"]
                        popuptext = user_name.replace('\n', ' ')
                        iframe = folium.Html(popuptext, script=True)
                        popup = folium.Popup(iframe, max_width=300, min_width=300)
                        folium.Marker(location=[H_latitude, H_longitude], popup=popup, icon=folium.Icon(color='red', icon='home')).add_to(map)
                        text_for_yandex = text_for_yandex + "\nvar myPlacemark" + str(yandex_count) + " = new ymaps.Placemark([" + str(H_latitude) + "," + str(H_longitude) + '],{\n' + "hintContent: '" + popuptext + "' ,\n" + "balloonContentHeader: '" + popuptext + "',\n" + "},{\n" + "preset: 'islands#redDotIcon'\n" + "});\n" + "myMap.geoObjects.add(myPlacemark" + str(yandex_count) + ");\n"
                        i = i + 1
                except Exception as ex:
                    pass
            except Exception as ex:
                pass
        yandex_count = yandex_count + 1
    if 0 <= time.hour <= 12:
        time_of_day = "утро"
    else:
        time_of_day = "вечер"
    day = time.strftime("%d.%m.%Y")
    title = "Карты/Обстановка на " + time_of_day + " " + day + " " + hour + ".html"
    map.save(title)
    #f = FSInputFile("Карты/Обстановка на " + time_of_day + " " + day + " " + hour + ".html")
    #await callback.message.answer_document(f)
    source = 'yandex_map.html'
    destination = 'Карты/Яндекс обстановка на ' + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html"
    try:
        shutil.copy2(source, destination)
    except Exception as ex:
        pass
    # yandex_map = open('Report/Яндекс обстановка на ' + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html", 'w')
    # yandex_map.close()
    file_yandex_name = 'Карты/Яндекс обстановка на ' + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html"
    yandex_map = FSInputFile(file_yandex_name)
    with open(file_yandex_name, "r") as f:
        contents = f.readlines()
    contents.insert(14, text_for_yandex)
    with codecs.open(file_yandex_name, "w", "utf-8") as f:
        contents = "".join(contents)
        f.write(contents)
    await callback.message.answer_document(yandex_map)
    await callback.message.answer("Полный доклад в файле выше.\n", reply_markup=kb.back_keyboard)


async def get_video_note(collection, user_id, callback,kb):
    nachalnik = await collection.find_one({"user_id": user_id})
    year_nabor = nachalnik['Present']['year_nabor']
    fakultet = nachalnik['Present']['fakultet']
    user_group = nachalnik['Present']['user_group']
    user_unit = nachalnik['Present']['user_unit']
    if user_unit == "Начальник курса" or user_unit == "Курсовой офицер" or user_unit == "Старшина курса":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet
        })
    if user_unit == "НФ" or user_unit == "ЗНФ":
        cur = collection.find({
            "Present.fakultet": fakultet
        })
    if user_unit == "Командир учебной группы":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group
        })
    if user_unit == "Командир 1 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 1 отд-я"
        })
    if user_unit == "Командир 2 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 2 отд-я"
        })
    if user_unit == "Командир 3 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 3 отд-я"
        })
    time_old = datetime.datetime.now()
    if 0 <= time_old.hour <= 12:
        time_of_day = "morning"
        time_of_day_facts = "1 morning"
    else:
        time_of_day = "evening"
        time_of_day_facts = "1 evening"
    time = time_old.strftime("%d.%m.%Y")
    time_facts = time_old.strftime("%d-%m-%Y")
    cur = cur.sort("Present.user_group", 1)
    zip_file_name = 'Report/Видеозаметки на ' + time + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + '.zip'
    video_file_name = 'Report/Видеозаметки на ' + time + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + '.mp4'
    file_names = []
    async for doc in cur:
        if doc["Present"]['user_unit'] == "Начальник курса" or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
            continue
        try:
            name = "Report/" + doc["Present"]['user_group'] + "/" + time + " " + time_of_day + "/" + doc["Present"]['user_lastname'] + " " + doc["Facts"][time_facts][time_of_day_facts]["uid"] + ".mp4"
            video = FSInputFile(name)
            await callback.message.answer_video(video)
            file_names.append(name)
        except Exception as ex:
            pass
    zip_object = zipfile.ZipFile(zip_file_name, 'w')
    #try:
    #    video_clips = [VideoFileClip(video_path) for video_path in file_names]
    #    final_clip = concatenate_videoclips(video_clips)
   #     final_clip.write_videofile(video_file_name)
    #except Exception as ex:
    #    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ex)
    for file_name in file_names:
        zip_object.write(file_name, compress_type=zipfile.ZIP_DEFLATED)
    zip_object.close()
    #f = FSInputFile(zip_file_name)
    #await callback.message.answer_document(f)
    #await callback.message.answer("Видеоролики в файле выше.\n", reply_markup=kb.back_keyboard)

async def find_report_fast(collection, user_id, callback,kb):
    nachalnik = await collection.find_one({"user_id": user_id})
    year_nabor = nachalnik['Present']['year_nabor']
    fakultet = nachalnik['Present']['fakultet']
    user_group = nachalnik['Present']['user_group']
    user_unit = nachalnik['Present']['user_unit']
    if user_unit == "Начальник курса" or user_unit == "Курсовой офицер" or user_unit == "Старшина курса":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet
        })
    if user_unit == "НФ" or user_unit == "ЗНФ":
        cur = collection.find({
            "Present.fakultet": fakultet
        })
    if user_unit == "Командир учебной группы":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group
        })
    if user_unit == "Командир 1 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 1 отд-я"
        })
    if user_unit == "Командир 2 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 2 отд-я"
        })
    if user_unit == "Командир 3 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 3 отд-я"
        })
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    all_ok = "<span style='background-color:#00FF00'><b>Курсанты не имеющие проблем на данный момент:</b><br>"
    all_ok_daleko = "\n<b>Курсанты, которые находятся далеко от места проживания:</b>\n"
    not_ok = "\n<b>Курсанты, не совершившие доклад:</b>\n"
    on_service = "<br><b>Курсанты, находящиеся в наряде:</b><br>"
    lazaret = "<br><b>Курсанты, находящиеся в лазарете:</b><br>"
    kazarma = "<br><b>Курсанты, находящиеся в казарме:</b><br>"
    score_all_ok = 0
    score_not_ok = 0
    score_on_service = 0
    score_lazaret = 0
    score_kazarma = 0
    score_otpusk = 0
    score_hospital = 0
    score_yvolnenie = 0
    score_komandirovka = 0
    score_vnekazarm = 0
    cur = cur.sort("Present.user_group", 1)
    async for doc in cur:
        if doc["Present"]['user_unit'] == "Начальник курса" or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
            continue
        if doc["Present"]['user_status'] == "В наряде":
            score_on_service = score_on_service + 1
            on_service = on_service + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_on_service) + ".</b>" + \
                     doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                         "user_middlename"] + "<br>"
            continue
        if doc["Present"]['user_status'] == "В лазарете":
            score_lazaret = score_lazaret + 1
            lazaret = lazaret + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_lazaret) + ".</b>" + \
                     doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                         "user_middlename"] + "<br>"
            continue
        if doc["Present"]['user_status'] == "В казарме":
            score_kazarma = score_kazarma + 1
            kazarma = kazarma + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_kazarma) + ".</b>" + \
                     doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                         "user_middlename"] + "<br>"
            continue
        if doc["Present"]['user_status'] == "В отпуске":
            score_otpusk = score_otpusk + 1
        if doc["Present"]['user_status'] == "В госпитале":
            score_hospital = score_hospital + 1
        if doc["Present"]['user_status'] == "В увольнении":
            score_yvolnenie = score_yvolnenie + 1
        if doc["Present"]['user_status'] == "В командировке":
            score_komandirovka = score_komandirovka + 1
        if doc["Present"]['user_status'] == "Вне общежития":
            score_vnekazarm = score_vnekazarm + 1
        number = "number " + time_of_day
        i_min = 0
        try:
            number = doc["Facts"][day][number]["number"]
            number = str(number) + " " + time_of_day
            score_all_ok = score_all_ok + 1
            try:
                count_address = doc["Present"]["address"]["count"]
                i = 0
                distance = []
                while i <= count_address:
                    home = (float(doc["Present"]["address"][str(i)]["latitude"]), float(doc["Present"]["address"][str(i)]["longitude"]))
                    point = (float(doc["Facts"][day][number]["latitude"]), float(doc["Facts"][day][number]["longitude"]))
                    distance.append(geodesic(point, home).m)
                    i = i + 1
                i = 0
                distance_min = 10000000000
                while i <= count_address:
                    home = (float(doc["Present"]["address"][str(i)]["latitude"]),
                            float(doc["Present"]["address"][str(i)]["longitude"]))
                    point = (float(doc["Facts"][day][number]["latitude"]),
                             float(doc["Facts"][day][number]["longitude"]))
                    if geodesic(point, home).m <= distance_min:
                        distance_min = geodesic(point, home).m
                        i_min = i
                    i = i + 1
                if min(distance) < 500:
                    all_ok = all_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_all_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>"\
                             + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + " <b>Место отметки: </b>" + str(doc["Facts"][day][number]["latitude"]) + ", " + str(doc["Facts"][day][number]["longitude"]) + "<br>" \
                             + "\n<b>Расстояние до места проживания: </b>" + str(round(min(distance))) + " метров<br><span style='background-color:#00FF00'>"
                else:
                    all_ok_daleko = all_ok_daleko + "<b>" + doc["Present"]["user_group"] + ".</b>" + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + ","
            except Exception as ex:
                all_ok = all_ok + "\n<b>" + doc["Present"]["user_group"] + " " + str(score_all_ok) + ".</b></span> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>" \
                         + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + " <b>Место отметки: </b>" + str(doc["Facts"][day][number]["latitude"]) + ", " + str(doc["Facts"][day][number]["longitude"]) + "<br>" \
                         + "\n<span style='background-color:#FF0000'><b>У курсанта командованием курса не введены адреса проживания!</b></span><span style='background-color:#00FF00'>" + "<br>"
        except Exception as ex:
            score_not_ok = score_not_ok + 1
            try:
                not_ok = not_ok + "<b>" + doc["Present"]["user_group"] + ".</b>" + doc["Present"]["user_lastname"] + " " + \
                     doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + ","
            except Exception as ex:
                not_ok = not_ok + "<b>" + doc["Present"]["user_group"] + ".</b>" + doc["Present"]["user_lastname"] + " " + \
                     doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + ","

    f = open("Report/" + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html", 'w')
    day = time.strftime("%d.%m.%Y")
    itog = "На <b>" + day + " </b> обстановка следующая:\n" + "<b>В системе зарегистрировано: </b>" + str(score_otpusk+score_komandirovka+score_kazarma+score_lazaret+score_hospital+score_yvolnenie+score_on_service+score_vnekazarm) + "\n" + \
           "<b>Доклад поступил (включая отпуск, командировку, увольнение, госпиталь): </b>" +  str(score_all_ok) + "\n" + \
           "<b>Доклад не поступил: </b>" + str(score_not_ok) + "\n" + \
            "<b>В казарме: </b>" + str(score_kazarma) + "\n" + \
            "<b>В лазарете: </b>" + str(score_lazaret) + "\n" + \
            "<b>В наряде: </b>" + str(score_on_service) + "\n"
    f = itog + not_ok + all_ok_daleko
    try:
        await callback.message.answer(f, parse_mode='HTML', reply_markup=kb.back_keyboard)
    except Exception as ex:
        itog = "На <b>" + day + " </b> обстановка следующая:<br>" + "<b>В системе зарегистрировано: </b>" + str(
            score_otpusk + score_komandirovka + score_kazarma + score_lazaret + score_hospital + score_yvolnenie + score_on_service + score_vnekazarm) + "<br>" + \
               "<b>Доклад поступил (включая отпуск, командировку, увольнение, госпиталь): </b>" + str(
            score_all_ok) + "<br>" + \
               "<b>Доклад не поступил: </b>" + str(score_not_ok) + "<br>" + \
               "<b>В казарме: </b>" + str(score_kazarma) + "<br>" + \
               "<b>В лазарете: </b>" + str(score_lazaret) + "<br>" + \
               "<b>В наряде: </b>" + str(score_on_service) + "<br>"
        tekst = open("Report/" + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + " fast.html", 'w')
        tekst.write(itog + "<br>" + not_ok + "<br><br>" + all_ok_daleko)
        tekst.close()
        tekst = FSInputFile("Report/" + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + " fast.html")
        await callback.message.answer_document(tekst)
        await callback.message.answer("Короткий доклад в файле выше.\n", reply_markup=kb.back_keyboard)

async def status_kursants(collection, user_id, callback,kb):
    nachalnik = await collection.find_one({"user_id": user_id})
    year_nabor = nachalnik['Present']['year_nabor']
    fakultet = nachalnik['Present']['fakultet']
    user_group = nachalnik['Present']['user_group']
    user_unit = nachalnik['Present']['user_unit']
    if user_unit == "Начальник курса" or user_unit == "Курсовой офицер" or user_unit == "Старшина курса":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet
        })
    if user_unit == "НФ" or user_unit == "ЗНФ":
        cur = collection.find({
            "Present.fakultet": fakultet
        })
    if user_unit == "Командир учебной группы":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group
        })
    if user_unit == "Командир 1 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 1 отд-я"
        })
    if user_unit == "Командир 2 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 2 отд-я"
        })
    if user_unit == "Командир 3 отд-я":
        cur = collection.find({
            "Present.year_nabor": year_nabor,
            "Present.fakultet": fakultet,
            "Present.user_group": user_group,
            "Present.user_unit": "Курсант 3 отд-я"
        })
    all_ok = "<b>Ваше подразделение:</b><br>\n"
    score_all_ok = 1
    cur = cur.sort("Present.user_group", 1)
    async for doc in cur:
        if doc["Present"]['user_unit'] == "Начальник курса" or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
            continue
        try:
            all_ok = all_ok + str(score_all_ok) + ". " + "<b>" + doc["Present"]["user_group"] + ". ID: <code>" + str(doc["user_id"]) + "</code></b> "+ doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + ": <b>" + doc["Present"]["user_status"] + "</b><br>\n"
            score_all_ok = score_all_ok + 1
        except Exception as ex:
            print(ex)
    try:
        await callback.message.answer(all_ok, parse_mode='HTML')
    except Exception as ex:
        tekst = open("Списки/" + nachalnik['Present']['user_lastname'] + ".html", 'w')
        tekst.write(all_ok)
        tekst.close()
        tekst = FSInputFile(
            "Списки/" + nachalnik['Present']['user_lastname'] + ".html")
        await callback.message.answer_document(tekst)
        await callback.message.answer("Много фамилий. Открывай файл выше.\n")
    await callback.message.answer("Введите ID курсанта, которому необходимо изменить статус, либо вернитесь в меню!\n", reply_markup=kb.back_keyboard)
