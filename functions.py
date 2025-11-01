import datetime
from settings import YANDEX_TOKEN
from yandex_geocoder import Client

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




def find_report(bot, mdb, user_group, kursant_unit):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    all_ok = "<b>Курсанты не имеющие проблем на данный момент:</b>"
    problems = "<b>Курсанты, имеющие проблемы:</b>"
    not_ok = "<b>Курсанты, не совершившие доклад:</b>"
    score_all_ok = 0
    score_problems = 0
    score_not_ok = 0
    if user_group == "91 курс":
        all_ok = "<b>901 учебная группа:</b>"
        problems = "<b>901 учебная группа:</b>"
        not_ok = "<b>901 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 901 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "901"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print (doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    get_address_from_coords(str(doc["Facts"][day][number]["latitude"]), str(doc["Facts"][day][number]["longitude"]), doc)
                    home = (float(doc["Present"]["address"]["latitude"]), float(doc["Present"]["address"]["longitude"]))
                    point = (float(doc["Facts"][day][number]["latitude"]), float(doc["Facts"][day][number]["longitude"]))
                    distance = geodesic(point, home).m
                    print(str(round(distance)))
                    if doc["Facts"][day][number]["problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] \
                                 + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] \
                                 + "\n<b>Расстояние до места проведения отпуска: </b>" + str(round(distance)) + " метров"
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] \
                                   + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] \
                                   + "\n<b>Расстояние до места проведения отпуска: </b>" + str(round(distance)) + " метров" \
                                   + "\n<b>Проблемы: </b>" + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if 2 <= doc["Present"]["check_present"] <= 4:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)