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
    return check['Present']['check_present']

async def save_kursant_anketa(collection, user_data):
    check_present = 1
    #if update.user_data['user_group'] == "Комиссия": check_present = 6
    await collection.update_one(
        {'user_id': user_data['id']},
        {'$set': {'Present': {
                             'year_nabor': user_data['year_nabor'],
                             'fakultet': user_data['fakultet'],
                             'user_group': user_data['kafedra'],
                             'user_unit': user_data['position'],
                             'user_lastname': user_data['last_name'],
                             'user_name': user_data['name'],
                             'user_middlename': user_data['middle_name'],
                             'user_phone': user_data['phone_number'],
                             'check_present': check_present,
                             "count": 0
                             }
                  }
         }
    )
    return 0