import datetime

from aiogram.types import FSInputFile

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
        print(number)
    except Exception as ex:
        number = 0
    return number

async def lastname(collection, effective_user):
    check = await collection.find_one({"user_id": effective_user})
    print (check['Present']['user_lastname'])
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
        print(e)

async def save_kursant_address(collection, user_id):
    try:
        await collection.update_one ({"user_id":user_id},
                                    {"$set": {
                                        "Present.count": 1
                                            }
                                    })
    except Exception as e:
        print(e)

async def reset_address(collection, user_id):
    try:
        await collection.update_one ({"user_id":user_id},
                                    {"$set": {
                                        "Present.count": 0
                                    }})
    except Exception as e:
        print(e)




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
    score_all_ok = 0
    score_not_ok = 0
    cur = cur.sort("Present.user_lastname", 1)
    async for doc in cur:
        number = "number " + time_of_day
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
                if min(distance) < 500:
                    all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>"\
                             + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + "<br>" \
                             + "\n<b>Расстояние до места проживания: </b>" + str(round(min(distance))) + " метров<br>"
                else:
                    all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>"\
                             + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + "<br>" \
                             + "\n</span><span style='background-color:#FF0000'><b>Расстояние до места проживания: </b>" + str(round(min(distance))) + " метров</span><span style='background-color:#00FF00'><br>"
            except Exception as ex:
                all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>" \
                         + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] + "<br>" \
                         + "\n</span><span style='background-color:#FF0000'><b>У курсанта командованием курса не введены адреса проживания!</b></span><span style='background-color:#00FF00'><br>"
        except Exception as ex:
            print(ex)
            score_not_ok = score_not_ok + 1
            not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                 doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "<br>" + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] + "<br></span><span style='background-color:#FF0000'>"
    f = open("Report/" + day + " " + time_of_day + " " + nachalnik['Present']['user_lastname'] + ".html", 'w')
    f.write(all_ok + "\n" + not_ok)
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
            "<b>Номер телефона:</b> " + kursant["Present"]["user_lastname"] + "\n"
            "<b>Статус:</b> " + kursant["Present"]["user_status"] + "\n"
            "<b>Адреса проживания (включая при нахождении в отпуске):</b> \n"
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