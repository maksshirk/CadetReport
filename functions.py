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
    },
        'Present.count': {
            "count": 0
        }
    }
    })
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
        "Present.count.count": 0
    })
    return user

async def put_address_from_coords(collection, user_id, address):
    try:
        client = Client(YANDEX_TOKEN)
        coordinates = client.coordinates(address)
        user = await collection.find_one({"user_id": user_id})
        try:
            count = user['Present']['address']['count']['count']
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
                                        "Present.address.count": {
                                            "count": count
                                            }
                                    }})
    except Exception as e:
        print(e)

async def save_kursant_address(collection, user_id):
    try:
        await collection.update_one ({"user_id":user_id},
                                    {"$set": {
                                        "Present.count": {
                                            "count": 1
                                            }
                                    }})
    except Exception as e:
        print(e)