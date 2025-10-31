import pymongo
from pymongo import MongoClient
from settings import MONGO_DB
from settings import MONGODB_LINK
from yandex_geocoder import Client
import datetime, telegram, requests
from bs4 import BeautifulSoup
from telegram import  KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from glob import glob
from random import choice
from geopy import GoogleV3
from settings import YANDEX_TOKEN
mdb = MongoClient(MONGODB_LINK)[MONGO_DB]
import folium
from utility import get_keyboard
from geopy.distance import geodesic
import numpy as np
from telegram.ext import ConversationHandler
import haversine
import uuid
import os,shutil


def search_or_save_user(mdb, effective_user, message):
    user = mdb.users.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": message.chat.id,
            "Present": {"check_present": 0}
        }
        mdb.users.insert_one(user)
    return user


def save_user_location(mdb, user, b, location, time, problems):
    if 0 <= time.hour <= 12:
        r = "morning"
    else:
        r = "evening"
    s = time.strftime("%H-%M-%S")
    number = number_Facts(mdb, user, b, r)
    number = int(number) + 1
    print (number)
    print (r)
    time_of_day = "number " + str(r)
    Facts_number = "Facts." + b + "." + time_of_day
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Facts_number:
            {
                'number': number}
        }
        })
    r = str(number) + " " + r
    Facts = "Facts." + b + "." + r
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Facts:
                      {
                      'time': s,
                      'latitude': location.latitude,
                      'longitude': location.longitude,
                      'problems': problems,
                      'number': number}
                  }
         })
    return user

def check_point(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['check_present']

def check_group(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_group']

def check_unit(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_unit']

def number_Facts(mdb, user, b, r):
    print(user['user_id'])
    check = mdb.users.find_one({"user_id": user['user_id']})
    r = str(r) + " number"
    print("тут")
    try:
        print(check['Facts'][b][r]["number"])
        print("Все круто")
        number = check['Facts'][b][r]["number"]
    except Exception as ex:
        print("Сейчас буду здесь")
        print(ex)
        print("Все плохо")
        number = 0
    return number

def number_Report(mdb, user, b, r):
    print(user['user_id'])
    check = mdb.users.find_one({"user_id": user['user_id']})
    a = "number " + str(r)
    try:
        print(check['Report'][b][r][a]["number"])
        print("Все круто")
        number = check['Report'][b][r][a]["number"]
    except Exception as ex:
        print("Сейчас буду здесь")
        print(ex)
        print("Все плохо")
        number = 0
    return number

def lastname(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_lastname']

def get_group(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_group']

def save_user_report(mdb, user, report_category, unit_report, time, uid):
    report_category = report_category.replace('.', ' ')
    report_category = report_category.replace('+', ' ')
    unit_report = unit_report.replace('.', ' ')
    unit_report = unit_report.replace('+', ' ')
    time = time.replace('.', ' ')
    time = time.replace('+', ' ')
    TIME = datetime.datetime.now()
    TIME = TIME.strftime("%d-%m-%Y")
    b = report_category
    r = unit_report
    number = number_Report(mdb, user, b, r)
    number = int(number) + 1
    r = "number " + str(r)
    Report_number = "Report." + report_category + "." + unit_report + "." + r
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Report_number:
                        {'number': number}
                            }
                  }
        ,
        True
    )
    unit_report_number = str(number) + " " + unit_report
    Report = "Report." + report_category + "." + unit_report + "." + unit_report_number
    TIME_HMS = datetime.datetime.now()
    TIME_HMS = TIME_HMS.strftime("%H-%M-%S")
    print(Report)
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Report:
                        {'date': TIME,
                         'time': TIME_HMS,
                         'check': 0,
                         'number': number,
                         'uid': uid}
                            }
                  }
        ,
        True
    )
    Report = "Report." + report_category + "." + unit_report + ".check_report"
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Report: 0
                            }
                  }
        ,
        True
    )
    return user
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {"check_report": 0
                            }
                  }
        ,
        True
    )
    return user

def save_kursant_anketa(mdb, user, user_data, update):
    check_present = 1
    if update.user_data['user_group'] == "Комиссия": check_present = 6
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'Present': {'user_group': user_data['user_group'],
                             'user_unit': user_data['user_unit'],
                             'user_lastname': user_data['user_lastname'],
                             'user_name': user_data['user_name'],
                             'user_middlename': user_data['user_middlename'],
                             'user_phone': user_data['user_phone'],
                             'check_present': check_present,
                             "count": 0
                             }
                  }
         }
    )
    return user

def save_user_anketa(mdb, user, user_data):

    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'SOS':     {'user_lastname_mother': user_data['user_lastname_mother'],
                              'user_name_mother': user_data['user_name_mother'],
                              'user_middlename_mother': user_data['user_middlename_mother'],
                              'user_phone_mother': user_data['user_phone_mother'],
                              'user_address_mother': user_data['user_address_mother'],
                              'user_lastname_father': user_data['user_lastname_father'],
                              'user_name_father': user_data['user_name_father'],
                              'user_middlename_father': user_data['user_middlename_father'],
                              'user_phone_father': user_data['user_phone_father'],
                              'user_address_father': user_data['user_address_father'],
                              'user_lastname_other': user_data['user_lastname_other'],
                              'user_name_other': user_data['user_name_other'],
                              'user_middlename_other': user_data['user_middlename_other'],
                              'user_phone_other': user_data['user_phone_other'],
                              'user_address_other': user_data['user_address_other'],
                              'check_SOS': 0
                             }
                  }
         }
    )
    mdb.users.update_one({'_id': user['_id']},
                         {'$set': {'Present.check_present': 2}})
    return user

def check_address(doc):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    number = "number " + time_of_day
    number = doc["Facts"][day][number]["number"]
    number = str(number) + " " + time_of_day
    try:
        doc["Facts"][day][number]["address"]
        status = "OK"
        return status
    except Exception as ex:
        print(ex)
        status = "not OK"
        return status

def put_address(doc, address):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    number = "number " + time_of_day
    number = doc["Facts"][day][number]["number"]
    number = str(number) + " " + time_of_day
    user_id = doc["user_id"]
    Facts = "Facts." + day + "." + number + ".address"
    mdb.users.update({"user_id": user_id},
                     {'$set': {Facts: address}})
    return user_id

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
        all_ok = "<b>903 учебная группа:</b>"
        problems = "<b>903 учебная группа:</b>"
        not_ok = "<b>903 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 903 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "903"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
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
        all_ok = "<b>904 учебная группа:</b>"
        problems = "<b>904 учебная группа:</b>"
        not_ok = "<b>904 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        #904 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "904"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
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
        all_ok = "<b>905-1 учебная группа:</b>"
        problems = "<b>905-1 учебная группа:</b>"
        not_ok = "<b>905-1 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 905-1
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "905-1"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
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
        all_ok = "<b>905-2 учебная группа:</b>"
        problems = "<b>905-2 учебная группа:</b>"
        not_ok = "<b>905-2 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 905-2
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "905-2"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
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
        all_ok = "<b>906 учебная группа:</b>"
        problems = "<b>906 учебная группа:</b>"
        not_ok = "<b>906 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        #906 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "906"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
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
    print(all_ok)
    print(problems)
    print(not_ok)

    print("На этом пока всё!")

def get_address_from_coords(latitude, longitude, doc):
    #заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    number = "number " + time_of_day
    number = doc["Facts"][day][number]["number"]
    number = str(number) + " " + time_of_day
    if check_address(doc) == "not OK":
        client = Client(YANDEX_TOKEN)
        try:
            address = client.address(longitude,latitude)
            put_address(doc, address)
            return address
        except Exception as e:
            #если не смогли, то возвращаем ошибку
            return "error"
    else:
        return doc["Facts"][day][number]["address"]

def create_map(bot, update):
    print("Я тут")
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    hour = time.strftime("%H-%M-%S")
    map = folium.Map(location=[59.812019, 30.378742], zoom_start = 8)
    cur = mdb.users.find()
    for doc in cur:
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
                    print(ex)
                    Family = "<p>Данных о семье нет"
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + Family
                print(user_name)
                P_latitude = float(doc["Facts"][day][number]["latitude"])
                P_longitude = float(doc["Facts"][day][number]["longitude"])
                popuptext = user_name
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                folium.Marker(location=[P_latitude, P_longitude], popup= popup, icon=folium.Icon(color = 'gray')).add_to(map)
                H_latitude = float(doc["Present"]["address"]["latitude"])
                H_longitude = float(doc["Present"]["address"]["longitude"])
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + " <p>" + doc["Present"]["address"]["address"]
                popuptext = user_name
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                folium.Marker(location=[H_latitude, H_longitude], popup=popup, icon=folium.Icon(color= 'blue', icon='home')).add_to(map)
                folium.PolyLine(locations=[(P_latitude, P_longitude), (H_latitude, H_longitude)], line_opacity=0.5).add_to(map)
            except Exception as ex:
                print(ex)
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
                    print(ex)
                    Family = "<p>Данных о семье нет"
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + Family
                print(user_name)
                H_latitude = float(doc["Present"]["address"]["latitude"])
                H_longitude = float(doc["Present"]["address"]["longitude"])
                popuptext = user_name
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                folium.Marker(location=[H_latitude, H_longitude], popup=popup,
                              icon=folium.Icon(color='red', icon='home')).add_to(map)
        except Exception as ex:
            print(ex)
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
                    print(ex)
                    Family = "<p>Данных о семье нет"
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + Family
                print(user_name)
                H_latitude = float(doc["Present"]["address"]["latitude"])
                H_longitude = float(doc["Present"]["address"]["longitude"])
                popuptext = user_name
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                folium.Marker(location=[H_latitude, H_longitude], popup=popup,
                          icon=folium.Icon(color='red', icon='home')).add_to(map)
            except Exception as ex:
                print(ex)

    if 0 <= time.hour <= 12:
        time_of_day = "утро"
    else:
        time_of_day = "вечер"
    day = time.strftime("%d.%m.%Y")
    title = "Карты/Обстановка на " + time_of_day + " " + day + " " + hour + ".html"
    map.save(title)
    with open(title, "rb") as file:
        update.bot.send_document(chat_id=bot.message.chat.id, document=file,
                                  filename=title)
    print(bot)


def lets_go(bot, update):
    user = mdb.users.find_one({"Present.check_present": 2})
    user_id = user["user_id"]
    update.user_data['find_user_id'] = user_id
    name = 'Введите адрес:' + user["Present"]["user_lastname"] + " " + user["Present"]["user_name"] + " " + user["Present"]["user_middlename"]
    bot.message.reply_text(name)
    return "put_address_from_coords"

def put_address_from_coords(bot, update):
    print("тут")
    user_id = update.user_data['find_user_id']
    print(user_id)
    address = bot.message.text
    print(address)
    try:
        client = Client(YANDEX_TOKEN)
        print("вот тут")
        coordinates = client.coordinates(address)
        print(coordinates[1])
        print(coordinates[0])
        mdb.users.update_one ({"user_id":user_id},
                              {"$set": {"Present.address":
                                            {"latitude": str(coordinates[1]),
                                             "longitude": str(coordinates[0]),
                                             "address":address
                                            }}})
        mdb.users.update_one({"user_id": user_id},
                             {"$set": {"Present.check_present": 3
                                           }})
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Введенные данные отправлены на проверку!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    except Exception as e:
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text(e, reply_markup=get_keyboard(check_user))
        return ConversationHandler.END

def test_start (bot, update):
    mdb.users.find_one({"check_report": 0})



def test (bot, update):
    src_dir = "Report/2. Бланк инструктажа (подпись родителей на обратной стороне)/Курсовое звено"
    target_dir = "Проверены/"
    searchstring = "1743ce2d-c9a3-4951-b91d-54a611286575"

    for f in os.listdir(src_dir):
        if searchstring in f and os.path.isfile(os.path.join(src_dir, f)):
            shutil.copy2(os.path.join(src_dir, f), target_dir)
            print
            "COPY", f


def get_status_film(film, bot, update):
    SOS(bot)
    doklad = "Такие дела"
    number = "number " + film
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Кинофильмы"][film][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + film
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 2 or user["Report"]["Кинофильмы"][film][dock]["check"] == "2":
                try:
                    doklad = "<ins>⛔Доклад не принят. Причина: " + user["Report"]["Кинофильмы"][film][dock]["reason"] + "Исправьте и загрузите заново</ins>"
                except Exception as ex:
                    doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 0 or user["Report"]["Кинофильмы"][film][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 1 or user["Report"]["Кинофильмы"][film][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_status_books(books, bot, update):
    SOS(bot)
    doklad = "Такие дела"
    number = "number " + books
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Литературные произведения"][books][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + books
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 2 or user["Report"]["Литературные произведения"][books][dock]["check"] == "2":
                try:
                    doklad = "<ins>⛔Доклад не принят. Причина: " + user["Report"]["Литературные произведения"][books][dock]["reason"] + "Исправьте и загрузите заново</ins>"
                except Exception as ex:
                    doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 0 or user["Report"]["Литературные произведения"][books][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 1 or user["Report"]["Литературные произведения"][books][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_status_mathematic(math, bot, update):
    SOS(bot)
    doklad = "Такие дела"
    number = "number " + math
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Математический анализ"][math][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + math
            if user["Report"]["Математический анализ"][math][dock]["check"] == 2 or user["Report"]["Математический анализ"][math][dock]["check"] == "2":
                try:
                    doklad = "<ins>⛔Доклад не принят. Причина: " + user["Report"]["Математический анализ"][math][dock]["reason"] + "Исправьте и загрузите заново</ins>"
                except Exception as ex:
                    doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Математический анализ"][math][dock]["check"] == 0 or user["Report"]["Математический анализ"][math][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Математический анализ"][math][dock]["check"] == 1 or user["Report"]["Математический анализ"][math][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_status_analitic(analitic, bot, update):
    SOS(bot)
    doklad = "Такие дела"
    number = "number " + analitic
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + analitic
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 2 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "2":
                try:
                    doklad = "<ins>⛔Доклад не принят. Причина: " + user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["reason"] + "Исправьте и загрузите заново</ins>"
                except Exception as ex:
                    doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 0 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 1 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_status_reps(reps, bot, update):
    SOS(bot)
    doklad = "Такие дела"
    number = "number " + reps
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Отчеты"][reps][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + reps
            if user["Report"]["Отчеты"][reps][dock]["check"] == 2 or user["Report"]["Отчеты"][reps][dock]["check"] == "2":
                try:
                    doklad = "<ins>⛔Доклад не принят. Причина: " + user["Report"]["Отчеты"][reps][dock]["reason"] + "Исправьте и загрузите заново</ins>"
                except Exception as ex:
                    doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Отчеты"][reps][dock]["check"] == 0 or user["Report"]["Отчеты"][reps][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Отчеты"][reps][dock]["check"] == 1 or user["Report"]["Отчеты"][reps][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad




def get_rating_film(film, user_id, update):
    doklad = "Такие дела"
    number = "number " + film
    user = mdb.users.find_one({"user_id": user_id})
    try:
        number_of_film = user["Report"]["Кинофильмы"][film][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + film
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 2 or user["Report"]["Кинофильмы"][film][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 0 or user["Report"]["Кинофильмы"][film][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 1 or user["Report"]["Кинофильмы"][film][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_rating_books(books, user_id, update):
    doklad = "Такие дела"
    number = "number " + books
    user = mdb.users.find_one({"user_id": user_id})
    try:
        number_of_film = user["Report"]["Литературные произведения"][books][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + books
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 2 or user["Report"]["Литературные произведения"][books][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 0 or user["Report"]["Литературные произведения"][books][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 1 or user["Report"]["Литературные произведения"][books][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_rating_mathematic(math, user_id, update):
    doklad = "Такие дела"
    number = "number " + math
    user = mdb.users.find_one({"user_id": user_id})
    try:
        number_of_film = user["Report"]["Математический анализ"][math][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + math
            if user["Report"]["Математический анализ"][math][dock]["check"] == 2 or user["Report"]["Математический анализ"][math][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Математический анализ"][math][dock]["check"] == 0 or user["Report"]["Математический анализ"][math][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Математический анализ"][math][dock]["check"] == 1 or user["Report"]["Математический анализ"][math][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_rating_analitic(analitic, user_id, update):
    doklad = "Такие дела"
    number = "number " + analitic
    user = mdb.users.find_one({"user_id": user_id})
    try:
        number_of_film = user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + analitic
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 2 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 0 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 1 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_rating_reps(reps, user_id, update):
    doklad = "Такие дела"
    number = "number " + reps
    user = mdb.users.find_one({"user_id": user_id})
    try:
        number_of_film = user["Report"]["Отчеты"][reps][number]["number"]
        i = number_of_film
        while i >= 1:
            dock = str(i) + " " + reps
            if user["Report"]["Отчеты"][reps][dock]["check"] == 2 or user["Report"]["Отчеты"][reps][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Отчеты"][reps][dock]["check"] == 0 or user["Report"]["Отчеты"][reps][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Отчеты"][reps][dock]["check"] == 1 or user["Report"]["Отчеты"][reps][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i - 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad


def get_rating(bot, update):
    # заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    print(get_group(mdb, bot.effective_user) + " " + lastname(mdb, bot.effective_user) + " запросил рейтинг")
    films = {1: "Чапаев (1934)",
             2: "Повесть о настоящем человеке (1948)",
             3: "Добровольцы (1958)",
             4: "Обыкновенный фашизм (1965)",
             5: "Офицеры (1972)",
             6: "В бой идут одни старики (1973)",
             7: "Они сражались за Родину (1975)",
             8: "Брестская крепость (2010)",
             9: "Легенда 17 (2013)",
             10: "28 панфиловцев (2016)",
             11: "Движение вверх (2017)",
             12: "Время первых (2017)",
             13: "Сто шагов (2019)",
             14: "Ржев (2019)",
             15: "Балканский рублеж (2019)",
             16: "Лев Яшин  Вратарь моей мечты (2019)",
             17: "Жила-была девочка (1944)",
             18: "Мы смерти смотрели в лицо (1980)",
             19: "Порох (1985)",
             20: "Зимнее утро (1966)",
             21: "Блокада (1973-1977)",
             22: "Коридор бессмертия (2019)"}
    books = {1: "Русский характер  Толстой А Н ",
             2: "Волоколамское шоссе  Бек А А ",
             3: "Взять живым! Карпов В В ",
             4: "Горячий снег  Бондарев Ю В ",
             5: "Генералиссимус Суворов  Раковский Л И ",
             6: "Василий Теркин  Твардовский А Т ",
             7: "Навеки девятнадцатилетник  Бакланов Г Я ",
             8: "Героев славных имена  Сборник очерков",
             9: "Доклад начальника академии об образовании академии"}
    math = {1: "Задание 1 Область определения функции и логарифма",
            2: "Задание 2, 3, 4 Построение графика функции",
            3: "Задание 5 Четность и нечетность функции",
            4: "Задание 6 Экстремумы функции без использования производной",
            5: "Задание 7 Периодические функции",
            6: "Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя",
            7: "Задания 14 15 Непрерывность функции и точки разрыва",
            8: "Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций",
            9: "Задание 18 Значение производной в данной точке",
            10: "Задание 23 Приближенные вычисления с помощью производной",
            11: "Задание 24 Производная функции, заданной параметрическим способом",
            12: "Задания 25, 28 Производная неявной функции",
            13: "Задание 26 Уравнение касательной и нормали к графику функции",
            14: "Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба",
            15: "Задание 29 Правило Лопиталя",
            16: "Задание 30 Нахождение асимптот графиков функций",
            17: "Задание 31 Нахождение интервалов монотонности",
            18: "Задание 32 Экстремумы фнукций",
            19: "Задание 34,34 Исследование функции, применение производной к построению графиков функций"}
    analit = {1: "Задание 1-4 Задача 1-1 Комплексные числа",
              2: "Задание 1-4 Задача 1-2 Разложение на множители",
              3: "Задание 3-5 Задача 3-1 Векторы, их произведения",
              4: "Задание 3-5 Задача 3-2 Длина и угол между векторами",
              5: "Задание 4-2 Задача 4-1 Уравнение прямой",
              6: "Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки",
              7: "Задание 6-2 Задача 6-2 Уравнение параллельной прямой",
              8: "Задание 6-2 Задача 6-3 Уравнение плоскости",
              9: "Задание 6-2 Задача 6-7 Проекция точки на плоскость",
              10: "Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка",
              11: "Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы",
              12: "Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"}
    reports = {1: "1  Отпускной билет (постановка на учет)",
               2: "2  Бланк инструктажа (подпись родителей на обратной стороне)",
               3: "3  Письмо родителям (подпись родителей на обратной стороне)",
               4: "4  Служебное задания (проагитированные курсанты)",
               5: "5  Отпускной билет (снятие с учета)"}
    print ("тут")
    cur = mdb.users.find()
    for doc in cur:
        print(str(doc["user_id"]) + " пошел")
        bot = doc["user_id"]
        count = 1
        film_rate_ok = 0
        film_rate_process = 0
        film_rate_problem = 0
        film_rate_bad = 0
        while count <= 22:
            film = films[count]
            print(film)
            doklad = get_rating_film(film, bot, update)
            print(doklad)
            if doklad == "<ins>✅Доклад принят</ins>": film_rate_ok = film_rate_ok + 1
            if doklad == "<em>⏳На обработке</em>": film_rate_process = film_rate_process + 1
            if doklad == "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>": film_rate_problem = film_rate_problem + 1
            if doklad == "⚠Доклад не представлен": film_rate_bad = film_rate_bad + 1
            count = count + 1
        mdb.users.update_one({"user_id": doc["user_id"]},
                         {'$set': {"Present.rating.film_rate_ok": film_rate_ok,
                              "Present.rating.film_rate_process": film_rate_process,
                              "Present.rating.film_rate_problem": film_rate_problem,
                                  "Present.rating.film_rate_bad": film_rate_bad}})
    cur = mdb.users.find()
    for doc in cur:
        print(str(doc["user_id"]) + " пошел")
        bot = doc["user_id"]
        reps_rate_ok = 0
        reps_rate_process = 0
        reps_rate_problem = 0
        reps_rate_bad = 0
        count = 1
        while count <= 5:
            reps = reports[count]
            doklad = get_rating_reps(reps, bot, update)
            if doklad == "<ins>✅Доклад принят</ins>": reps_rate_ok = reps_rate_ok + 1
            if doklad == "<em>⏳На обработке</em>": reps_rate_process = reps_rate_process + 1
            if doklad == "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>": reps_rate_problem = reps_rate_problem + 1
            if doklad == "⚠Доклад не представлен": reps_rate_bad = reps_rate_bad + 1
            count = count + 1
        mdb.users.update_one({"user_id": doc["user_id"]},
                             {'$set': {"Present.rating.reps_rate_ok": reps_rate_ok,
                                       "Present.rating.reps_rate_process": reps_rate_process,
                                       "Present.rating.reps_rate_problem": reps_rate_problem,
                                       "Present.rating.reps_rate_bad": reps_rate_bad}})
    cur = mdb.users.find()
    for doc in cur:
        print(str(doc["user_id"]) + " пошел")
        bot = doc["user_id"]
        book_rate_ok = 0
        book_rate_process = 0
        book_rate_problem = 0
        book_rate_bad = 0
        count = 1
        while count <= 9:
            book = books[count]
            doklad = get_rating_books(book, bot, update)
            if doklad == "<ins>✅Доклад принят</ins>": book_rate_ok = book_rate_ok + 1
            if doklad == "<em>⏳На обработке</em>": book_rate_process = book_rate_process + 1
            if doklad == "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>": book_rate_problem = book_rate_problem + 1
            if doklad == "⚠Доклад не представлен": book_rate_bad = book_rate_bad + 1
            count = count + 1
        mdb.users.update_one({"user_id": doc["user_id"]},
                             {'$set': {"Present.rating.book_rate_ok": book_rate_ok,
                                       "Present.rating.book_rate_process": book_rate_process,
                                       "Present.rating.book_rate_problem": book_rate_problem,
                                       "Present.rating.book_rate_bad": book_rate_bad}})
    cur = mdb.users.find()
    for doc in cur:
        print(str(doc["user_id"]) + " пошел")
        bot = doc["user_id"]
        mathematic_rate_ok = 0
        mathematic_rate_process = 0
        mathematic_rate_problem = 0
        mathematic_rate_bad = 0
        count = 1
        while count <= 19:
            mathematic = math[count]
            doklad = get_rating_mathematic(mathematic, bot, update)
            if doklad == "<ins>✅Доклад принят</ins>": mathematic_rate_ok = mathematic_rate_ok + 1
            if doklad == "<em>⏳На обработке</em>": mathematic_rate_process = mathematic_rate_process + 1
            if doklad == "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>": mathematic_rate_problem = mathematic_rate_problem + 1
            if doklad == "⚠Доклад не представлен": mathematic_rate_bad = mathematic_rate_bad + 1
            count = count + 1
        mdb.users.update_one({"user_id": doc["user_id"]},
                             {'$set': {"Present.rating.mathematic_rate_ok": mathematic_rate_ok,
                                       "Present.rating.mathematic_rate_process": mathematic_rate_process,
                                       "Present.rating.mathematic_rate_problem": mathematic_rate_problem,
                                       "Present.rating.mathematic_rate_bad": mathematic_rate_bad}})

    cur = mdb.users.find()
    for doc in cur:
        print(str(doc["user_id"]) + " пошел")
        bot = doc["user_id"]
        analitic_rate_ok = 0
        analitic_rate_process = 0
        analitic_rate_problem = 0
        analitic_rate_bad = 0
        count = 1
        while count <= 12:
            analitic = analit[count]
            doklad = get_rating_analitic(analitic, bot, update)
            if doklad == "<ins>✅Доклад принят</ins>": analitic_rate_ok = analitic_rate_ok + 1
            if doklad == "<em>⏳На обработке</em>": analitic_rate_process = analitic_rate_process + 1
            if doklad == "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>": analitic_rate_problem = analitic_rate_problem + 1
            if doklad == "⚠Доклад не представлен": analitic_rate_bad = analitic_rate_bad + 1
            count = count + 1
        mdb.users.update({"user_id": doc["user_id"]},
                         {'$set': {"Present.rating.analitic_rate_ok": analitic_rate_ok,
                                   "Present.rating.analitic_rate_process": analitic_rate_process,
                                   "Present.rating.analitic_rate_problem": analitic_rate_problem,
                                   "Present.rating.analitic_rate_bad": analitic_rate_bad}})
    cur = mdb.users.find()
    for doc in cur:
        print(str(doc["user_id"]) + " пошел")
        rate_ok = doc["Present"]["rating"]["film_rate_ok"] + doc["Present"]["rating"]["reps_rate_ok"] + doc["Present"]["rating"]["book_rate_ok"] + doc["Present"]["rating"]["mathematic_rate_ok"] + doc["Present"]["rating"]["analitic_rate_ok"]
        rate_process = doc["Present"]["rating"]["film_rate_process"] + doc["Present"]["rating"]["reps_rate_process"] + doc["Present"]["rating"]["book_rate_process"] + doc["Present"]["rating"]["mathematic_rate_process"] + doc["Present"]["rating"]["analitic_rate_process"]
        rate_problem = doc["Present"]["rating"]["film_rate_problem"] + doc["Present"]["rating"]["reps_rate_problem"] + doc["Present"]["rating"]["book_rate_problem"] + doc["Present"]["rating"]["mathematic_rate_problem"] + doc["Present"]["rating"]["analitic_rate_problem"]
        rate_bad = doc["Present"]["rating"]["film_rate_bad"] + doc["Present"]["rating"]["reps_rate_bad"] + doc["Present"]["rating"]["book_rate_bad"] + doc["Present"]["rating"]["mathematic_rate_bad"] + doc["Present"]["rating"]["analitic_rate_bad"]
        mdb.users.update({"user_id": doc["user_id"]},
                         {'$set': {"Present.rate_ok": rate_ok,
                                   "Present.rate_process": rate_process,
                                   "Present.rate_problem": rate_problem,
                                   "Present.rate_bad": rate_bad}})
    print("Рейтинг готов!")
    bot.message.reply_text("Рейтинг готов!", parse_mode=ParseMode.HTML)


def get_user_rating(bot, update):
    bot.message.reply_text("Необходимо подождать! Небыстрое дело.", parse_mode=ParseMode.HTML)
    print(str(bot.effective_user.id) + " запросил рейтинг")
    rating = "<b>Рейтинг курса по представлению отчетов по индивидуальным заданиям</b> показан в виде:\n" \
             "Место - Группа - Ф.И. - Принятые доклады✅/На обработке⏳/Не представленные⚠/Непринятые⛔\n Поехали: \n"
    count = 1
    cur = mdb.users.find()
    cur = cur.sort([("Present.user_group", 1),("Present.rate_bad", 1),("Present.rate_problem", 1)])
    for doc in cur:
        try:
            try:
                if doc["user_id"] == bot.effective_user.id:
                    mesto = str(count)
                if doc["Present"]["check_present"] == 2 or doc["Present"]["check_present"] == 3 or doc["Present"]["check_present"] == 4:
                    rating = rating + "<b>" + str(count) + ".</b> "\
                        + doc["Present"]["user_group"] + " " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " \
                        + str(doc["Present"]["rate_ok"]) + "✅/ " + str(doc["Present"]["rate_process"]) + "⏳/ " + str(doc["Present"]["rate_bad"]) + "⚠/ "  + str(doc["Present"]["rate_problem"]) + "⛔\n"
                    count = count + 1
                    if count == 65:
                        bot.message.reply_text(rating, parse_mode=ParseMode.HTML)
                        rating = ""
            except Exception as ex:
                b = "ok"
        except Exception as ex:
            b = "ok"
    bot.message.reply_text(rating + "\nВаше место:<b> " + mesto + "</b>", parse_mode=ParseMode.HTML)
    rating_901_ok = 0
    rating_903_ok = 0
    rating_904_ok = 0
    rating_905_1_ok = 0
    rating_905_2_ok = 0
    rating_906_ok = 0
    rating_901_process = 0
    rating_903_process = 0
    rating_904_process = 0
    rating_905_1_process = 0
    rating_905_2_process = 0
    rating_906_process = 0
    rating_901_bad = 0
    rating_903_bad = 0
    rating_904_bad = 0
    rating_905_1_bad = 0
    rating_905_2_bad = 0
    rating_906_bad = 0
    rating_901_problem = 0
    rating_903_problem = 0
    rating_904_problem = 0
    rating_905_1_problem = 0
    rating_905_2_problem = 0
    rating_906_problem = 0
    cur = mdb.users.find()
    for doc in cur:
        try:

            try:
                    if doc["Present"]["user_group"] == "901":
                        rating_901_ok = rating_901_ok + doc["Present"]["rate_ok"]
                        rating_901_process = rating_901_process + doc["Present"]["rate_process"]
                        rating_901_bad = rating_901_bad + doc["Present"]["rate_bad"]
                        rating_901_problem = rating_901_problem + doc["Present"]["rate_problem"]
                    if doc["Present"]["user_group"] == "903":
                        rating_903_ok = rating_903_ok + doc["Present"]["rate_ok"]
                        rating_903_process = rating_903_process + doc["Present"]["rate_process"]
                        rating_903_bad = rating_903_bad + doc["Present"]["rate_bad"]
                        rating_903_problem = rating_903_problem + doc["Present"]["rate_problem"]
                    if doc["Present"]["user_group"] == "904":
                        rating_904_ok = rating_904_ok + doc["Present"]["rate_ok"]
                        rating_904_process = rating_904_process + doc["Present"]["rate_process"]
                        rating_904_bad = rating_904_bad + doc["Present"]["rate_bad"]
                        rating_904_problem = rating_904_problem + doc["Present"]["rate_problem"]
                    if doc["Present"]["user_group"] == "905-1":
                        rating_905_1_ok = rating_905_1_ok + doc["Present"]["rate_ok"]
                        rating_905_1_process = rating_905_1_process + doc["Present"]["rate_process"]
                        rating_905_1_bad = rating_905_1_bad + doc["Present"]["rate_bad"]
                        rating_905_1_problem = rating_905_1_problem + doc["Present"]["rate_problem"]
                    if doc["Present"]["user_group"] == "905-2":
                        rating_905_2_ok = rating_905_2_ok + doc["Present"]["rate_ok"]
                        rating_905_2_process = rating_905_2_process + doc["Present"]["rate_process"]
                        rating_905_2_bad = rating_905_2_bad + doc["Present"]["rate_bad"]
                        rating_905_2_problem = rating_905_2_problem + doc["Present"]["rate_problem"]
                    if doc["Present"]["user_group"] == "906":
                        rating_906_ok = rating_906_ok + doc["Present"]["rate_ok"]
                        rating_906_process = rating_906_process + doc["Present"]["rate_process"]
                        rating_906_bad = rating_906_bad + doc["Present"]["rate_bad"]
                        rating_906_problem = rating_906_problem + doc["Present"]["rate_problem"]
            except Exception as ex:
                b = "ok"
        except Exception as ex:
            b = "ok"
    rating_group= "<b>Учет докладов групп </b> представлен в виде:\n" \
             "Группа - Количество принятых докладов✅/Не обработанных⏳/Не представленных⚠/Непринятых⛔\n"
    rating_group = rating_group + "901 учебная группа - " + str(rating_901_ok) + "✅/ " + str(rating_901_process) + "⏳/ " + str(rating_901_bad) + "⚠/ "  + str(rating_901_problem) + "⛔\n" + \
                   "903 учебная группа - " + str(rating_903_ok) + "✅/ " + str(rating_903_process) + "⏳/ " + str(rating_903_bad) + "⚠/ "  + str(rating_903_problem) + "⛔\n" + \
                   "904 учебная группа - " + str(rating_904_ok) + "✅/ " + str(rating_904_process) + "⏳/ " + str(rating_904_bad) + "⚠/ "  + str(rating_904_problem) + "⛔\n" + \
                   "905-1 учебная группа - " + str(rating_905_1_ok) + "✅/ " + str(rating_905_1_process) + "⏳/ " + str(rating_905_1_bad) + "⚠/ "  + str(rating_905_1_problem) + "⛔\n" + \
                   "905-2 учебная группа - " + str(rating_905_2_ok) + "✅/ " + str(rating_905_2_process) + "⏳/ " + str(rating_905_2_bad) + "⚠/ "  + str(rating_905_2_problem) + "⛔\n" + \
                   "906 учебная группа - " + str(rating_906_ok) + "✅/ " + str(rating_906_process) + "⏳/ " + str(rating_906_bad) + "⚠/ "  + str(rating_906_problem) + "⛔\n"
    bot.message.reply_text(rating_group, parse_mode=ParseMode.HTML)
    rating_group= "<b>Учет докладов групп </b>представлен в виде:\n" \
             "Группа - Процент(%) принятых докладов✅/Не обработанных⏳/Не представленных⚠/Непринятых⛔\n"
    rating_group = rating_group + "901 учебная группа - " + str(round(rating_901_ok * 100 / (68 * 23),2)) + "%✅/ " + str(round(rating_901_process * 100 / (68 * 23),2)) + "%⏳/ " + str(round(rating_901_bad * 100 / (68 * 23),2)) + "%⚠/ "  + str(round(rating_901_problem * 100 / (68 * 23),2)) + "%⛔\n" + \
                   "903 учебная группа - " + str(round(rating_903_ok * 100 / (68 * 15),2)) + "%✅/ " + str(round(rating_903_process * 100 / (68 * 15),2)) + "%⏳/ " + str(round(rating_903_bad * 100 / (68 * 15),2)) + "%⚠/ "  + str(round(rating_903_problem * 100 / (68 * 15),2)) + "%⛔\n" + \
                   "904 учебная группа - " + str(round(rating_904_ok * 100 / (68 * 15),2)) + "%✅/ " + str(round(rating_904_process * 100 / (68 * 15),2)) + "%⏳/ " + str(round(rating_904_bad * 100 / (68 * 15),2)) + "%⚠/ "  + str(round(rating_904_problem * 100 / (68 * 15),2)) + "%⛔\n" + \
                   "905-1 учебная группа - " + str(round(rating_905_1_ok * 100 / (68 * 29),2)) + "%✅/ " + str(round(rating_905_1_process * 100 / (68 * 29),2)) + "%⏳/ " + str(round(rating_905_1_bad * 100 / (68 * 29),2)) + "%⚠/ "  + str(round(rating_905_1_problem * 100 / (68 * 29),2)) + "%⛔\n" + \
                   "905-2 учебная группа - " + str(round(rating_905_2_ok * 100 / (68 * 29),2)) + "%✅/ " + str(round(rating_905_2_process * 100 / (68 * 29),2)) + "%⏳/ " + str(round(rating_905_2_bad * 100 / (68 * 29),2)) + "%⚠/ "  + str(round(rating_905_2_problem * 100 / (68 * 29),2)) + "%⛔\n" + \
                   "906 учебная группа - " + str(round(rating_906_ok * 100 / (68 * 15),2)) + "%✅/ " + str(round(rating_906_process * 100 / (68 * 15),2)) + "%⏳/ " + str(round(rating_906_bad * 100 / (68 * 15),2)) + "%⚠/ "  + str(round(rating_906_problem * 100 / (68 * 15),2)) + "%⛔\n"
    bot.message.reply_text(rating_group, parse_mode=ParseMode.HTML)
    bot.message.reply_text("Рейтинг представлен🏆!", parse_mode=ParseMode.HTML)
    print(str(bot.effective_user.id) + " посмотрел рейтинг")

def find_report_group(bot, mdb, user_group):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"

    day = time.strftime("%d-%m-%Y")
    vremya = time.strftime("%H:%M:%S")
    bot.message.reply_text("Сегодня:\n<b>" + day + "</b>\n" + "Сейчас:\n <b>" + vremya + "</b>" + " \nДоклады от курсантов принимаются \nс <b>8:00 до 8:45</b> \nи с <b>19:00 до 20:00</b> \nпо Москве", parse_mode=telegram.ParseMode.HTML)
    all_ok = "<b>" + user_group + " учебная группа:</b>"
    problems = "<b>" + user_group + " учебная группа:</b>"
    not_ok = "<b>" + user_group + " учебная группа:</b>"
    score_all_ok = 0
    score_problems = 0
    score_not_ok = 0
    rezerv_1 = ""
    rezerv_2 = ""
    rezerv_3 = ""
    rezerv_4 = ""
    all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
    problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
    not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
    cur = mdb.users.find({'Present.user_group': user_group})
    cur = cur.sort("Present.user_lastname", 1)
    for doc in cur:
        print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"])
        number = "number " + time_of_day
        try:
            number = doc["Facts"][day][number]["number"]
            number = str(number) + " " + time_of_day
            try:
                if doc["Facts"][day][number]["problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                    score_all_ok = score_all_ok + 1
                    all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] \
                                        + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"]
                else:
                    score_problems = score_problems + 1
                    problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] \
                                       + "\n<b>Время отметки: </b>" + doc["Facts"][day][number]["time"] \
                                       + "\n<b>Проблемы: </b>" + doc["Facts"][day][number]["problems"]
            except Exception as ex:
                print(ex)
        except Exception as ex:
            print(ex)
            score_not_ok = score_not_ok + 1
            print(score_not_ok)
            print(not_ok)
            if score_not_ok == 7:
                rezerv_1 = not_ok
                not_ok = ""
            if score_not_ok == 14:
                rezerv_2 = not_ok
                not_ok = ""
            if score_not_ok == 21:
                rezerv_3 = not_ok
                not_ok = ""
            if score_not_ok == 28:
                rezerv_4 = not_ok
                not_ok = ""
            if 2 <= doc["Present"]["check_present"] <= 4:
                not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                                doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                                 + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                                 + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                                 + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                                 + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                                 + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                                 + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                                 + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + \
                                 doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                                 + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                                 + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
            else:
                not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " \
                                 + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
    bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
    bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
    if rezerv_1 != "": bot.message.reply_text("\n" + rezerv_1, parse_mode=telegram.ParseMode.HTML)
    if rezerv_2 != "": bot.message.reply_text("\n" + rezerv_2, parse_mode=telegram.ParseMode.HTML)
    if rezerv_3 != "": bot.message.reply_text("\n" + rezerv_3, parse_mode=telegram.ParseMode.HTML)
    if rezerv_4 != "": bot.message.reply_text("\n" + rezerv_4, parse_mode=telegram.ParseMode.HTML)
    bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
    print("На этом пока всё!")



def check_doklad(bot, update):
    SOS(bot)
    reply_keyboard = [["Отчеты"],
                      ["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "type_doklad"

def type_doklad(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_category'] = bot.message.text

    if bot.message.text == "Отчеты":
        reply_keyboard = [["1. Отпускной билет (постановка на учет)"],
                          ["2. Бланк инструктажа (подпись родителей на обратной стороне)"],
                          ["3. Письмо родителям (подпись родителей на обратной стороне)"],
                          ["4. Служебное задания (проагитированные курсанты)"],
                          ["5. Отпускной билет (снятие с учета)"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите документ!',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Кинофильмы":
        reply_keyboard = [["Чапаев (1934)"],
                          ["Повесть о настоящем человеке (1948)"],
                          ["Добровольцы (1958)"],
                          ["Обыкновенный фашизм (1965)"],
                          ["Офицеры (1972)"],
                          ["В бой идут одни старики (1973)"],
                          ["Они сражались за Родину (1975)"],
                          ["Брестская крепость (2010)"],
                          ["Легенда 17 (2013)"],
                          ["28 панфиловцев (2016)"],
                          ["Движение вверх (2017)"],
                          ["Время первых (2017)"],
                          ["Сто шагов (2019)"],
                          ["Ржев (2019)"],
                          ["Балканский рублеж (2019)"],
                          ["Лев Яшин. Вратарь моей мечты (2019)"],
                          ["Жила-была девочка (1944)"],
                          ["Мы смерти смотрели в лицо (1980)"],
                          ["Порох (1985)"],
                          ["Зимнее утро (1966)"],
                          ["Блокада (1973-1977)"],
                          ["Коридор бессмертия (2019)"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите кинофильм',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Математический анализ":
        reply_keyboard = [["Задание 1 Область определения функции и логарифма"],
                          ["Задание 2, 3, 4 Построение графика функции"],
                          ["Задание 5 Четность и нечетность функции"],
                          ["Задание 6 Экстремумы функции без использования производной"],
                          ["Задание 7 Периодические функции"],
                          ["Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя"],
                          ["Задания 14 15 Непрерывность функции и точки разрыва"],
                          ["Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций"],
                          ["Задание 18 Значение производной в данной точке"],
                          ["Задание 23 Приближенные вычисления с помощью производной"],
                          ["Задание 24 Производная функции, заданной параметрическим способом"],
                          ["Задания 25, 28 Производная неявной функции"],
                          ["Задание 26 Уравнение касательной и нормали к графику функции"],
                          ["Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба"],
                          ["Задание 29 Правило Лопиталя"],
                          ["Задание 30 Нахождение асимптот графиков функций"],
                          ["Задание 31 Нахождение интервалов монотонности"],
                          ["Задание 32 Экстремумы фнукций"],
                          ["Задание 34,34 Исследование функции, применение производной к построению графиков функций"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Аналитическая геометрия и линейная алгебра":
        reply_keyboard = [["Задание 1-4 Задача 1-1 Комплексные числа"],
                          ["Задание 1-4 Задача 1-2 Разложение на множители"],
                          ["Задание 3-5 Задача 3-1 Векторы, их произведения"],
                          ["Задание 3-5 Задача 3-2 Длина и угол между векторами"],
                          ["Задание 4-2 Задача 4-1 Уравнение прямой"],
                          ["Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки"],
                          ["Задание 6-2 Задача 6-2 Уравнение параллельной прямой"],
                          ["Задание 6-2 Задача 6-3 Уравнение плоскости"],
                          ["Задание 6-2 Задача 6-7 Проекция точки на плоскость"],
                          ["Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка"],
                          ["Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы"],
                          ["Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите индивидуальное задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    else:
        reply_keyboard = [["Русский характер. Толстой А.Н."],
                          ["Волоколамское шоссе. Бек А.А."],
                          ["Взять живым! Карпов В.В."],
                          ["Горячий снег. Бондарев Ю.В."],
                          ["Генералиссимус Суворов. Раковский Л.И."],
                          ["Василий Теркин. Твардовский А.Т."],
                          ["Навеки девятнадцатилетник. Бакланов Г.Я."],
                          ["Героев славных имена. Сборник очерков"],
                          ["Доклад начальника академии об образовании академии"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите книгу',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    print("123")
    return "choice_doklad"

def choice_doklad(bot, update):
    SOS(bot)
    print("Я оказался тут")
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_title'] = bot.message.text
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    report_category = type.replace('.', ' ')
    unit_report = title.replace('.', ' ')
    Report = "Report." + report_category + "." + unit_report + ".check_report"
    print(Report)
    try:
        user = mdb.users.find_one({Report: 0})
        update.user_data['user'] = user
        bot.message.reply_text(user["Present"]["user_lastname"])
        unit_report = title.replace('.', ' ')
        number = "number " + unit_report
        print(number)
        try:
            number_of_type = user["Report"][report_category][unit_report][number]["number"]
            unit_report = title.replace('.', ' ')
            print(number_of_type)
            i = 1
            while i <= number_of_type:
                dock = str(i) + " " + unit_report
                print(dock)
                searchstring = user["Report"][report_category][unit_report][dock]["uid"]
                print(searchstring)
                print(type)
                print(title)
                if report_category != "Отчеты":
                    src_dir = "Report/" + type + "/" + title + "/" + user["Present"]["user_group"]
                else:
                    src_dir = "Report/" + title + "/" + user["Present"]["user_group"]
                for f in os.listdir(src_dir):
                    if searchstring in f and os.path.isfile(os.path.join(src_dir, f)):
                        photo = open(os.path.join(src_dir, f), 'rb')
                        update.bot.send_photo(chat_id=bot.message.chat.id, photo=photo)
                Report = "Report." + report_category + "." + unit_report + "." + dock + ".check"
                Reason = "Report." + report_category + "." + unit_report + "." + dock + ".reason"
                Officer = "Report." + report_category + "." + unit_report + "." + dock + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Reason: "Отправьте доклад повторно. Техническая неполадка",
                                               Officer: str(bot.message.chat.id)}})
                Report = "Report." + report_category + "." + unit_report + ".check_report"
                Officer = "Report." + report_category + "." + unit_report + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Officer: str(bot.message.chat.id)}})
                i = i + 1
            reply_keyboard = [["Доклад принят. Приступить к следующему"],
                              ["Доклад не принят."],
                              ["Я устал. Вернуться в меню!"]]
            bot.message.reply_text(user["Present"]["user_group"] + " " + user["Present"]["user_lastname"] + ' ' + user["Present"]["user_name"] + " " + user["Present"]["user_middlename"] +'\n' + user["Present"]["user_phone"] + "\n" + title, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return "zagruzka_v_bd"
        except Exception as ex:
            check_user = check_point(mdb, bot.effective_user)
            bot.message.reply_text('У товарища ' + user["Present"]["user_lastname"] + " какие то проблемы с этим докладом. Надо звонить Широкопетлеву")
            reply_keyboard = [["Отчеты"],
                              ["Кинофильмы"],
                              ["Литературные произведения"],
                              ["Математический анализ"],
                              ["Аналитическая геометрия и линейная алгебра"],
                              ["Вернуться в меню!"]]
            bot.message.reply_text('Выберите категорию',
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True))
            return "type_doklad"
    except Exception as ex:
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('У данного задания все отчеты проверены! Выберите другое задание')
        reply_keyboard = [["Отчеты"],
                          ["Кинофильмы"],
                          ["Литературные произведения"],
                          ["Математический анализ"],
                          ["Аналитическая геометрия и линейная алгебра"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите категорию',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "type_doklad"


def zagruzka_v_bd(bot, update):
    SOS(bot)
    if bot.message.text == "Я устал. Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    if bot.message.text == "Доклад принят. Приступить к следующему":
        type = update.user_data['quest_category']
        title = update.user_data['quest_title']
        type = type.replace('.', ' ')
        title = title.replace('.', ' ')
        Report = "Report." + type + "." + title + ".check_report"
        Officer = "Report." + type + "." + title + ".officer"
        user = update.user_data['user']
        mdb.users.update_one ({"user_id": user["user_id"]},
                              {"$set":{Report: 1,
                                       Officer: str(bot.message.chat.id)}})
        print("3 здесь")
        number = "number " + title
        try:
            print("1 здесь")
            number_of_type = user["Report"][type][title][number]["number"]
            i = 1
            while i <= number_of_type:
                print("2 здесь")
                dock = str(i) + " " + title
                Report = "Report." + type + "." + title + "." + dock + ".check"
                Reason = "Report." + type + "." + title + "." + dock + ".reason"
                Officer = "Report." + type + "." + title + "." + dock + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set":{Report: 1,
                                              Officer: str(bot.message.chat.id)}})
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$unset":{Reason: 1}})
                i = i + 1
        except Exception as ex:
            print("Эх, плохо то как")
        print("Принял!")
        officer = bot.message.chat.id
        print("Тут!")
        officer = mdb.users.find_one({"user_id":officer})
        count = officer["Present"]["count"] + 1
        print(count)
        Present = "Present.count"
        officer = bot.message.chat.id
        mdb.users.update({"user_id": officer},
                         {"$set": {Present: count}})
        reply_keyboard = [["Загружай, еще хочу!"],
                           ["Вернуться в меню!"]]
        bot.message.reply_text("Давай нажимай", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return "poehali"
    if bot.message.text == "Доклад не принят.":
        type = update.user_data['quest_category']
        title = update.user_data['quest_title']
        update.user_data['quest_category'] = type
        update.user_data['quest_title'] = title
        type = type.replace('.', ' ')
        title = title.replace('.', ' ')
        Report = "Report." + type + "." + title + ".check_report"
        user = update.user_data['user']
        Officer = "Report." + type + "." + title + ".officer"
        mdb.users.update_one({"user_id": user["user_id"]},
                             {"$set": {Report: 2,
                                       Officer: str(bot.message.chat.id)}})
        number = "number " + title
        try:
            number_of_type = user["Report"][type][title][number]["number"]
            i = 1
            while i <= number_of_type:
                dock = str(i) + " " + title
                Report = "Report." + type + "." + title + "." + dock + ".check"
                Reason = "Report." + type + "." + title + "." + dock + ".reason"
                Officer = "Report." + type + "." + title + "." + dock + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Officer: str(bot.message.chat.id)}})
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$unset": {Reason: 1}})
                i = i + 1
        except Exception as ex:
            print("Эх, плохо то как")
        reply_keyboard = [["Доклад неполный (менее 30 предложений). Необходимо переписать. "],
                          ["Доклад не оформлен (не подписан, нет заглавия). "],
                          ["Работа выполнено неаккуратно (без линейки, помарки) "],
                          ["Доклад невозможно разобрать. Сделать фото, либо переписать. "],
                          ["Доклад списан у товарища. Переписать. "],
                          ["Я устал. Не спрашивайте таких вопросов. Вернуться в меню!"]]
        bot.message.reply_text("Выберите причину либо ❗ напишите своими словами и отправьте сообщение.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=True))
        return "zagruzka_v_bd_problem"

def zagruzka_v_bd_problem(bot, update):
    SOS(bot)
    if bot.message.text == "Я устал. Не спрашивайте таких вопросов. Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    reason = bot.message.text
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    update.user_data['quest_category'] = type
    update.user_data['quest_title'] = title
    type = type.replace('.', ' ')
    title = title.replace('.', ' ')
    Report = "Report." + type + "." + title + ".check_report"
    user = update.user_data['user']
    mdb.users.update_one({"user_id": user["user_id"]},
                         {"$set": {Report: 2
                                   }})
    number = "number " + title
    try:
        number_of_type = user["Report"][type][title][number]["number"]
        i = 1
        while i <= number_of_type:
            dock = str(i) + " " + title
            Report = "Report." + type + "." + title + "." + dock + ".check"
            Reason = "Report." + type + "." + title + "." + dock + ".reason"
            Officer = "Report." + type + "." + title + "." + dock + ".officer"
            mdb.users.update_one({"user_id": user["user_id"]},
                                 {"$set": {Report: 2,
                                           Reason: reason,
                                           Officer: str(bot.message.chat.id)}})
            i = i + 1
    except Exception as ex:
        print("Эх, плохо то как")
    officer = bot.message.chat.id
    officer = mdb.users.find_one({"user_id": officer})
    count = officer["Present"]["count"] + 1
    Present = "Present.count"
    officer = bot.message.chat.id
    mdb.users.update({"user_id": officer},
                     {"$set": {Present: count}})
    reply_keyboard = [["Загружай, еще хочу!"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text("Давай нажимай", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "poehali"


def poehali (bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    print("Поехали")
    print(update.user_data['quest_category'])
    print(update.user_data['quest_title'])
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    report_category = type.replace('.', ' ')
    unit_report = title.replace('.', ' ')
    Report = "Report." + report_category + "." + unit_report + ".check_report"
    try:
        user = mdb.users.find_one({Report: 0})
        update.user_data['user'] = user
        bot.message.reply_text(user["Present"]["user_lastname"])
        number = "number " + unit_report
        try:
            number_of_type = user["Report"][report_category][unit_report][number]["number"]
            i = 1
            while i <= number_of_type:
                dock = str(i) + " " + unit_report
                searchstring = user["Report"][report_category][unit_report][dock]["uid"]
                if report_category != "Отчеты":
                    src_dir = "Report/" + type + "/" + title + "/" + user["Present"]["user_group"]
                else:
                    src_dir = "Report/" + title + "/" + user["Present"]["user_group"]
                for f in os.listdir(src_dir):
                    if searchstring in f and os.path.isfile(os.path.join(src_dir, f)):
                        photo = open(os.path.join(src_dir, f), 'rb')
                        update.bot.send_photo(chat_id=bot.message.chat.id, photo=photo)
                i = i + 1
                Report = "Report." + report_category + "." + unit_report + "." + dock + ".check"
                Reason = "Report." + report_category + "." + unit_report + "." + dock + ".reason"
                Officer = "Report." + report_category + "." + unit_report + "." + dock + ".officer"
                print("Сейчас обновлю")
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Reason: "Отправьте доклад повторно. Техническая неполадка",
                                               Officer: str(bot.message.chat.id)}})
                Report = "Report." + report_category + "." + unit_report + ".check_report"
                Officer = "Report." + report_category + "." + unit_report + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Officer: str(bot.message.chat.id)}})
            reply_keyboard = [["Доклад принят. Приступить к следующему"],
                              ["Доклад не принят."],
                              ["Я устал. Вернуться в меню!"]]
            bot.message.reply_text(
                user["Present"]["user_group"] + " " + user["Present"]["user_lastname"] + ' ' + user["Present"][
                    "user_name"] + " " + user["Present"]["user_middlename"] + '\n' + user["Present"][
                    "user_phone"] + "\n" + title,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return "zagruzka_v_bd"
        except Exception as ex:
            check_user = check_point(mdb, bot.effective_user)
            bot.message.reply_text('У товарища ' + user["Present"]["user_lastname"] + " какие то проблемы с этим докладом. Надо звонить Широкопетлеву")
            reply_keyboard = [["Отчеты"],
                              ["Кинофильмы"],
                              ["Литературные произведения"],
                              ["Математический анализ"],
                              ["Аналитическая геометрия и линейная алгебра"],
                              ["Вернуться в меню!"]]
            bot.message.reply_text('Выберите категорию',
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True))
            return "type_doklad"
    except Exception as ex:
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('У данного задания все отчеты проверены! Выберите другое задание')
        reply_keyboard = [["Отчеты"],
                          ["Кинофильмы"],
                          ["Литературные произведения"],
                          ["Математический анализ"],
                          ["Аналитическая геометрия и линейная алгебра"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите категорию',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "type_doklad"


def check_officer(bot, update):
    SOS(bot)
    cur_count = mdb.users.find({"Present.check_present": 5})
    text = ""
    for doc in cur_count:
        count = str(doc["Present"]["count"])
        text = text + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " проверил<b> " + count + " </b>работ(ы, у)\n"
    bot.message.reply_text(text, parse_mode=telegram.ParseMode.HTML)
    cur_count = mdb.users.find({"Present.check_present": 6})
    text = ""
    for doc in cur_count:
        count = str(doc["Present"]["count"])
        text = text + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " проверил<b> " + count + " </b>работ(ы, у)\n"
    bot.message.reply_text(text, parse_mode=telegram.ParseMode.HTML)
    cur_count = mdb.users.find({"Present.check_present": 7})
    text = ""
    for doc in cur_count:
        count = str(doc["Present"]["count"])
        text = text + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " проверил<b> " + count + " </b>работ(ы, у)\n"
    bot.message.reply_text(text, parse_mode=telegram.ParseMode.HTML)

def get_count_film(film, bot, update):
    doklad = "Такие дела"
    number = "number " + film
    user = mdb.users.find_one({"user_id": bot})
    try:
        number_of_film = user["Report"]["Кинофильмы"][film][number]["number"]
        i = 1
        while i <= number_of_film:
            dock = str(i) + " " + film
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 2 or user["Report"]["Кинофильмы"][film][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 0 or user["Report"]["Кинофильмы"][film][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Кинофильмы"][film][dock]["check"] == 1 or user["Report"]["Кинофильмы"][film][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i + 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_count_books(books, bot, update):
    doklad = "Такие дела"
    number = "number " + books
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Литературные произведения"][books][number]["number"]
        i = 1
        while i <= number_of_film:
            dock = str(i) + " " + books
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 2 or user["Report"]["Литературные произведения"][books][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 0 or user["Report"]["Литературные произведения"][books][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Литературные произведения"][books][dock]["check"] == 1 or user["Report"]["Литературные произведения"][books][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i + 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_count_mathematic(math, bot, update):
    doklad = "Такие дела"
    number = "number " + math
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Математический анализ"][math][number]["number"]
        i = 1
        while i <= number_of_film:
            dock = str(i) + " " + math
            if user["Report"]["Математический анализ"][math][dock]["check"] == 2 or user["Report"]["Математический анализ"][math][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Математический анализ"][math][dock]["check"] == 0 or user["Report"]["Математический анализ"][math][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Математический анализ"][math][dock]["check"] == 1 or user["Report"]["Математический анализ"][math][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i + 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_count_analitic(analitic, bot, update):
    doklad = "Такие дела"
    number = "number " + analitic
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][number]["number"]
        i = 1
        while i <= number_of_film:
            dock = str(i) + " " + analitic
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 2 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 0 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == 1 or user["Report"]["Аналитическая геометрия и линейная алгебра"][analitic][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i + 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_count_reps(reps, bot, update):
    doklad = "Такие дела"
    number = "number " + reps
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    try:
        number_of_film = user["Report"]["Отчеты"][reps][number]["number"]
        i = 1
        while i <= number_of_film:
            dock = str(i) + " " + reps
            if user["Report"]["Отчеты"][reps][dock]["check"] == 2 or user["Report"]["Отчеты"][reps][dock]["check"] == "2":
                doklad = "<ins>⛔Доклад не принят (Не тот документ, списан у другого курсанта, мало предложений, не подписан, не озаглавлен или невозможно разобрать подчерк). Исправьте и загрузите заново</ins>"
                return doklad
            if user["Report"]["Отчеты"][reps][dock]["check"] == 0 or user["Report"]["Отчеты"][reps][dock]["check"] == "0":
                doklad = "<em>⏳На обработке</em>"
                return doklad
            if user["Report"]["Отчеты"][reps][dock]["check"] == 1 or user["Report"]["Отчеты"][reps][dock]["check"] == "1":
                doklad = "<ins>✅Доклад принят</ins>"
            i = i + 1
    except Exception as ex:
        doklad = "⚠Доклад не представлен"
    return doklad

def get_rating_facts(bot, update):
    # заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    print(get_group(mdb, bot.effective_user) + " " + lastname(mdb, bot.effective_user) + " обновляет рейтинг докладов")
    today = datetime.datetime.now()
    hour_now = int(today.strftime("%H"))
    day = datetime.datetime.now()
    today = today.strftime("%d-%m-%Y")
    print(today)
    day = day.strftime("%d")
    print(day)
    day = int(day)
    print(day)
    cur = mdb.users.find()
    for doc in cur:
            fact_ok = 0
            fact_bad = 0
            i = 21
            while i <= day:
                day_fact = str(i) + "-01-2021"
                print(str(doc["user_id"]) + " пошел")
                user_id = doc["user_id"]
                user = mdb.users.find_one({"user_id": user_id})
                try:
                    time_evening = user["Facts"][day_fact]["1 evening"]["time"]
                    time_evening = time_evening.split("-")
                    hour_evening = int(time_evening[0])
                    if 18 <= hour_evening <= 20:
                        fact_ok = fact_ok + 1
                    else:
                        fact_bad = fact_bad + 1
                except Exception as ex:
                    fact_bad = fact_bad + 1
                try:
                    time_morning = user["Facts"][day_fact]["1 morning"]["time"]
                    time_morning = time_morning.split("-")
                    hour_morning = int(time_morning[0])
                    if 7 <= hour_morning <= 8:
                        fact_ok = fact_ok + 1
                    else:
                        fact_bad = fact_bad + 1
                except Exception as ex:
                    fact_bad = fact_bad + 1
                i = i + 1
            if hour_now <= 9: fact_bad = fact_bad - 2
            if 9 < hour_now <= 21: fact_bad = fact_bad - 1
            mdb.users.update_one({"user_id": user_id},
                                    {'$set': {"Present.fact_ok": fact_ok,
                                             "Present.fact_bad": fact_bad}})
    print("Рейтинг готов!")
    bot.message.reply_text("Рейтинг готов!", parse_mode=ParseMode.HTML)


def get_user_rating_facts(bot, update):
    bot.message.reply_text("Необходимо подождать! Небыстрое дело.", parse_mode=ParseMode.HTML)
    print(str(bot.effective_user.id) + " запросил рейтинг")
    rating = "<b>Рейтинг курса по представлению докладов о состоянии дел \n" \
             "Внимание! Принимаются доклады с 21 января. Принятый доклад - время отметки с 7:00 до 9:00 и с 18:00 до 21:00 по Москве</b>\n" \
             "Рейтинг показан в следующем виде:\n" \
             "Место - Группа - Ф.И. - Своевременных доклады✅/Непредставленные вовремя⚠\n Поехали: \n"
    count = 1
    cur = mdb.users.find()
    cur = cur.sort([("Present.fact_ok", pymongo.DESCENDING)])
    for doc in cur:
        try:
            try:
                if doc["user_id"] == bot.effective_user.id:
                    mesto = str(count)
                if doc["Present"]["check_present"] == 2 or doc["Present"]["check_present"] == 3 or doc["Present"]["check_present"] == 4:
                    rating = rating + "<b>" + str(count) + ".</b> "\
                        + doc["Present"]["user_group"] + " " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " \
                        + str(doc["Present"]["fact_ok"]) + "✅/ "  + str(doc["Present"]["fact_bad"]) + "⚠\n"
                    count = count + 1
                    if count == 65:
                        bot.message.reply_text(rating, parse_mode=ParseMode.HTML)
                        rating = ""
            except Exception as ex:
                b = "ok"
        except Exception as ex:
            b = "ok"
    bot.message.reply_text(rating + "\nВаше место:<b> " + mesto + "</b>", parse_mode=ParseMode.HTML)
    rating_901_ok = 0
    rating_903_ok = 0
    rating_904_ok = 0
    rating_905_1_ok = 0
    rating_905_2_ok = 0
    rating_906_ok = 0
    rating_901_bad = 0
    rating_903_bad = 0
    rating_904_bad = 0
    rating_905_1_bad = 0
    rating_905_2_bad = 0
    rating_906_bad = 0
    cur = mdb.users.find()
    for doc in cur:
        try:
            try:
                    if doc["Present"]["user_group"] == "901":
                        rating_901_ok = rating_901_ok + doc["Present"]["fact_ok"]
                        rating_901_bad = rating_901_bad + doc["Present"]["fact_bad"]
                    if doc["Present"]["user_group"] == "903":
                        rating_903_ok = rating_903_ok + doc["Present"]["fact_ok"]
                        rating_903_bad = rating_903_bad + doc["Present"]["fact_bad"]
                    if doc["Present"]["user_group"] == "904":
                        rating_904_ok = rating_904_ok + doc["Present"]["fact_ok"]
                        rating_904_bad = rating_904_bad + doc["Present"]["fact_bad"]
                    if doc["Present"]["user_group"] == "905-1":
                        rating_905_1_ok = rating_905_1_ok + doc["Present"]["fact_ok"]
                        rating_905_1_bad = rating_905_1_bad + doc["Present"]["fact_bad"]
                    if doc["Present"]["user_group"] == "905-2":
                        rating_905_2_ok = rating_905_2_ok + doc["Present"]["fact_ok"]
                        rating_905_2_bad = rating_905_2_bad + doc["Present"]["fact_bad"]
                    if doc["Present"]["user_group"] == "906":
                        rating_906_ok = rating_906_ok + doc["Present"]["fact_ok"]
                        rating_906_bad = rating_906_bad + doc["Present"]["fact_bad"]
            except Exception as ex:
                b = "ok"
        except Exception as ex:
            b = "ok"
    rating_group= "<b>Учет докладов групп </b> представлен в виде:\n" \
             "Группа - Количество своевременных докладов✅/Не представленных вовремя⚠\n"
    rating_group = rating_group + "901 учебная группа - " + str(rating_901_ok) + "✅/ " + str(rating_901_bad) +  "⚠\n" + \
                   "903 учебная группа - " + str(rating_903_ok) + "✅/ " + str(rating_903_bad) + "⚠\n" + \
                   "904 учебная группа - " + str(rating_904_ok) + "✅/ " + str(rating_904_bad) + "⚠\n" + \
                   "905-1 учебная группа - " + str(rating_905_1_ok) + "✅/ " + str(rating_905_1_bad) + "⚠\n" + \
                   "905-2 учебная группа - " + str(rating_905_2_ok) + "✅/ " + str(rating_905_2_bad) + "⚠\n" + \
                   "906 учебная группа - " + str(rating_906_ok) + "✅/ " + str(rating_906_bad) + "⚠\n"
    bot.message.reply_text(rating_group, parse_mode=ParseMode.HTML)
    itog_1 = rating_901_ok + rating_901_bad
    itog_3 = rating_903_ok + rating_903_bad
    itog_4 = rating_904_ok + rating_904_bad
    itog_5_1 = rating_905_1_ok + rating_905_1_bad
    itog_5_2 = rating_905_2_ok + rating_905_2_bad
    itog_6 = rating_906_ok + rating_906_bad
    rating_group= "<b>Учет докладов групп </b>представлен в виде:\n" \
             "Группа - Процент(%) своевременных докладов✅/Не представленных вовремя⚠\n"
    rating_group = rating_group + "901 учебная группа - " + str(round(rating_901_ok * 100 / itog_1, 2)) + "%✅/ " + str(round(rating_901_bad * 100 / itog_1, 2)) + "%⚠\n" + \
                   "903 учебная группа - " + str(round(rating_903_ok * 100 / itog_3, 2)) + "%✅/ " + str(round(rating_903_bad * 100 / itog_3, 2)) + "%⚠\n" + \
                   "904 учебная группа - " + str(round(rating_904_ok * 100 / itog_4, 2)) + "%✅/ " + str(round(rating_904_bad * 100 / itog_4, 2)) + "%⚠\n" + \
                   "905-1 учебная группа - " + str(round(rating_905_1_ok * 100 / itog_5_1, 2)) + "%✅/ " + str(round(rating_905_1_bad * 100 / itog_5_1, 2)) + "%⚠\n" + \
                   "905-2 учебная группа - " + str(round(rating_905_2_ok * 100 / itog_5_2, 2)) + "%✅/ " + str(round(rating_905_2_bad * 100 / itog_5_2, 2)) + "%⚠\n" + \
                   "906 учебная группа - " + str(round(rating_906_ok * 100 / itog_6, 2)) + "%✅/ " + str(round(rating_906_bad * 100 / itog_6, 2)) + "%⚠\n"
    bot.message.reply_text(rating_group, parse_mode=ParseMode.HTML)
    your_facts = "<b>Ваши доклады</b>: \n"
    user = mdb.users.find_one({"user_id": bot.effective_user.id})
    day = datetime.datetime.now()
    day = day.strftime("%d")
    day = int(day)
    i = 21
    print(i)
    while i <= day:
        day_fact = str(i) + "-01-2021"
        try:
            time_morning = user["Facts"][day_fact]["1 morning"]["time"]
            your_facts = your_facts + "<b>" + day_fact + "</b> " + "утренний доклад осуществлен в <b>" + time_morning + "</b> по Москве\n"
        except Exception as ex:
            your_facts = your_facts + "<b>" + day_fact + "</b> " + "утренний доклад <b> не осуществлён</b>\n"
        day_fact = str(i) + "-01-2021"
        try:
            time_evening = user["Facts"][day_fact]["1 evening"]["time"]
            your_facts = your_facts + "<b>" + day_fact + "</b> " + "вечерний доклад осуществлен в <b>" + time_evening + "</b> по Москве\n"
        except Exception as ex:
            your_facts = your_facts + "<b>" + day_fact + "</b> " + "вечерний доклад <b> не осуществлён</b>\n"
        i = i+1
    bot.message.reply_text(your_facts, parse_mode=ParseMode.HTML)
    bot.message.reply_text("Рейтинг представлен🏆!", parse_mode=ParseMode.HTML)
    print(str(bot.effective_user.id) + " посмотрел рейтинг")

def SOS(bot):
    if bot.message.text == "/sos":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END

def type_doklad_kursant (bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_category'] = bot.message.text

    if bot.message.text == "Математический анализ":
        reply_keyboard = [["Задание 1 Область определения функции и логарифма"],
                          ["Задание 2, 3, 4 Построение графика функции"],
                          ["Задание 5 Четность и нечетность функции"],
                          ["Задание 6 Экстремумы функции без использования производной"],
                          ["Задание 7 Периодические функции"],
                          ["Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя"],
                          ["Задания 14 15 Непрерывность функции и точки разрыва"],
                          ["Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций"],
                          ["Задание 18 Значение производной в данной точке"],
                          ["Задание 23 Приближенные вычисления с помощью производной"],
                          ["Задание 24 Производная функции, заданной параметрическим способом"],
                          ["Задания 25, 28 Производная неявной функции"],
                          ["Задание 26 Уравнение касательной и нормали к графику функции"],
                          ["Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба"],
                          ["Задание 29 Правило Лопиталя"],
                          ["Задание 30 Нахождение асимптот графиков функций"],
                          ["Задание 31 Нахождение интервалов монотонности"],
                          ["Задание 32 Экстремумы фнукций"],
                          ["Задание 34,34 Исследование функции, применение производной к построению графиков функций"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Аналитическая геометрия и линейная алгебра":
        reply_keyboard = [["Задание 1-4 Задача 1-1 Комплексные числа"],
                          ["Задание 1-4 Задача 1-2 Разложение на множители"],
                          ["Задание 3-5 Задача 3-1 Векторы, их произведения"],
                          ["Задание 3-5 Задача 3-2 Длина и угол между векторами"],
                          ["Задание 4-2 Задача 4-1 Уравнение прямой"],
                          ["Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки"],
                          ["Задание 6-2 Задача 6-2 Уравнение параллельной прямой"],
                          ["Задание 6-2 Задача 6-3 Уравнение плоскости"],
                          ["Задание 6-2 Задача 6-7 Проекция точки на плоскость"],
                          ["Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка"],
                          ["Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы"],
                          ["Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите индивидуальное задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    print("123")
    return "choice_doklad_kursant"

def choice_doklad_kursant (bot, update):
    SOS(bot)
    print("Я оказался тут")
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_title'] = bot.message.text
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    report_category = type.replace('.', ' ')
    unit_report = title.replace('.', ' ')
    Report = "Report." + report_category + "." + unit_report + ".check_report"
    print(Report)
    try:
        user = mdb.users.find_one({Report: 0})
        update.user_data['user'] = user
        bot.message.reply_text(user["Present"]["user_lastname"])
        unit_report = title.replace('.', ' ')
        number = "number " + unit_report
        print(number)
        try:
            number_of_type = user["Report"][report_category][unit_report][number]["number"]
            unit_report = title.replace('.', ' ')
            print(number_of_type)
            i = 1
            while i <= number_of_type:
                dock = str(i) + " " + unit_report
                print(dock)
                searchstring = user["Report"][report_category][unit_report][dock]["uid"]
                print(searchstring)
                print(type)
                print(title)
                if report_category != "Отчеты":
                    src_dir = "Report/" + type + "/" + title + "/" + user["Present"]["user_group"]
                else:
                    src_dir = "Report/" + title + "/" + user["Present"]["user_group"]
                for f in os.listdir(src_dir):
                    if searchstring in f and os.path.isfile(os.path.join(src_dir, f)):
                        photo = open(os.path.join(src_dir, f), 'rb')
                        update.bot.send_photo(chat_id=bot.message.chat.id, photo=photo)
                Report = "Report." + report_category + "." + unit_report + "." + dock + ".check"
                Reason = "Report." + report_category + "." + unit_report + "." + dock + ".reason"
                Officer = "Report." + report_category + "." + unit_report + "." + dock + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Reason: "Отправьте доклад повторно. Техническая неполадка",
                                               Officer: str(bot.message.chat.id)}})
                Report = "Report." + report_category + "." + unit_report + ".check_report"
                Officer = "Report." + report_category + "." + unit_report + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Officer: str(bot.message.chat.id)}})
                i = i + 1
            reply_keyboard = [["Доклад принят. Приступить к следующему"],
                              ["Доклад не принят."],
                              ["Я устал. Вернуться в меню!"]]
            bot.message.reply_text(user["Present"]["user_group"] + " " + user["Present"]["user_lastname"] + ' ' + user["Present"]["user_name"] + " " + user["Present"]["user_middlename"] +'\n' + user["Present"]["user_phone"] + "\n" + title, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return "zagruzka_v_bd_kursant"
        except Exception as ex:
            check_user = check_point(mdb, bot.effective_user)
            bot.message.reply_text('У товарища ' + user["Present"]["user_lastname"] + " какие то проблемы с этим докладом. Надо звонить Широкопетлеву")
            reply_keyboard = [["Математический анализ"],
                              ["Аналитическая геометрия и линейная алгебра"],
                              ["Вернуться в меню!"]]
            bot.message.reply_text('Выберите категорию',
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True))
            return "type_doklad_kursant"
    except Exception as ex:
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('У данного задания все отчеты проверены! Выберите другое задание')
        reply_keyboard = [["Математический анализ"],
                          ["Аналитическая геометрия и линейная алгебра"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите категорию',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "type_doklad_kursant"


def zagruzka_v_bd_kursant (bot, update):
    SOS(bot)
    if bot.message.text == "Я устал. Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    if bot.message.text == "Доклад принят. Приступить к следующему":
        type = update.user_data['quest_category']
        title = update.user_data['quest_title']
        type = type.replace('.', ' ')
        title = title.replace('.', ' ')
        Report = "Report." + type + "." + title + ".check_report"
        Officer = "Report." + type + "." + title + ".officer"
        user = update.user_data['user']
        mdb.users.update_one ({"user_id": user["user_id"]},
                              {"$set":{Report: 1,
                                       Officer: str(bot.message.chat.id)}})
        print("3 здесь")
        number = "number " + title
        try:
            print("1 здесь")
            number_of_type = user["Report"][type][title][number]["number"]
            i = 1
            while i <= number_of_type:
                print("2 здесь")
                dock = str(i) + " " + title
                Report = "Report." + type + "." + title + "." + dock + ".check"
                Reason = "Report." + type + "." + title + "." + dock + ".reason"
                Officer = "Report." + type + "." + title + "." + dock + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set":{Report: 1,
                                              Officer: str(bot.message.chat.id)}})
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$unset":{Reason: 1}})
                i = i + 1
        except Exception as ex:
            print("Эх, плохо то как")
        print("Принял!")
        officer = bot.message.chat.id
        print("Тут!")
        officer = mdb.users.find_one({"user_id":officer})
        count = officer["Present"]["count"] + 1
        print(count)
        Present = "Present.count"
        officer = bot.message.chat.id
        mdb.users.update({"user_id": officer},
                         {"$set": {Present: count}})
        reply_keyboard = [["Загружай, еще хочу!"],
                           ["Вернуться в меню!"]]
        bot.message.reply_text("Давай нажимай", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return "poehali_kursant"
    if bot.message.text == "Доклад не принят.":
        type = update.user_data['quest_category']
        title = update.user_data['quest_title']
        update.user_data['quest_category'] = type
        update.user_data['quest_title'] = title
        type = type.replace('.', ' ')
        title = title.replace('.', ' ')
        Report = "Report." + type + "." + title + ".check_report"
        user = update.user_data['user']
        Officer = "Report." + type + "." + title + ".officer"
        mdb.users.update_one({"user_id": user["user_id"]},
                             {"$set": {Report: 2,
                                       Officer: str(bot.message.chat.id)}})
        number = "number " + title
        try:
            number_of_type = user["Report"][type][title][number]["number"]
            i = 1
            while i <= number_of_type:
                dock = str(i) + " " + title
                Report = "Report." + type + "." + title + "." + dock + ".check"
                Reason = "Report." + type + "." + title + "." + dock + ".reason"
                Officer = "Report." + type + "." + title + "." + dock + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Officer: str(bot.message.chat.id)}})
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$unset": {Reason: 1}})
                i = i + 1
        except Exception as ex:
            print("Эх, плохо то как")
        reply_keyboard = [["Доклад неполный (менее 30 предложений). Необходимо переписать. "],
                          ["Доклад не оформлен (не подписан, нет заглавия). "],
                          ["Работа выполнено неаккуратно (без линейки, помарки) "],
                          ["Доклад невозможно разобрать. Сделать фото, либо переписать. "],
                          ["Доклад списан у товарища. Переписать. "],
                          ["Я устал. Не спрашивайте таких вопросов. Вернуться в меню!"]]
        bot.message.reply_text("Выберите причину либо ❗ напишите своими словами и отправьте сообщение.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=True))
        return "zagruzka_v_bd_problem_kursant"

def zagruzka_v_bd_problem_kursant (bot, update):
    SOS(bot)
    if bot.message.text == "Я устал. Не спрашивайте таких вопросов. Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    reason = bot.message.text
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    update.user_data['quest_category'] = type
    update.user_data['quest_title'] = title
    type = type.replace('.', ' ')
    title = title.replace('.', ' ')
    Report = "Report." + type + "." + title + ".check_report"
    user = update.user_data['user']
    mdb.users.update_one({"user_id": user["user_id"]},
                         {"$set": {Report: 2
                                   }})
    number = "number " + title
    try:
        number_of_type = user["Report"][type][title][number]["number"]
        i = 1
        while i <= number_of_type:
            dock = str(i) + " " + title
            Report = "Report." + type + "." + title + "." + dock + ".check"
            Reason = "Report." + type + "." + title + "." + dock + ".reason"
            Officer = "Report." + type + "." + title + "." + dock + ".officer"
            mdb.users.update_one({"user_id": user["user_id"]},
                                 {"$set": {Report: 2,
                                           Reason: reason,
                                           Officer: str(bot.message.chat.id)}})
            i = i + 1
    except Exception as ex:
        print("Эх, плохо то как")
    officer = bot.message.chat.id
    officer = mdb.users.find_one({"user_id": officer})
    count = officer["Present"]["count"] + 1
    Present = "Present.count"
    officer = bot.message.chat.id
    mdb.users.update({"user_id": officer},
                     {"$set": {Present: count}})
    reply_keyboard = [["Загружай, еще хочу!"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text("Давай нажимай", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "poehali_kursant"


def poehali_kursant (bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    print("Поехали")
    print(update.user_data['quest_category'])
    print(update.user_data['quest_title'])
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    report_category = type.replace('.', ' ')
    unit_report = title.replace('.', ' ')
    Report = "Report." + report_category + "." + unit_report + ".check_report"
    try:
        user = mdb.users.find_one({Report: 0})
        update.user_data['user'] = user
        bot.message.reply_text(user["Present"]["user_lastname"])
        number = "number " + unit_report
        try:
            number_of_type = user["Report"][report_category][unit_report][number]["number"]
            i = 1
            while i <= number_of_type:
                dock = str(i) + " " + unit_report
                searchstring = user["Report"][report_category][unit_report][dock]["uid"]
                if report_category != "Отчеты":
                    src_dir = "Report/" + type + "/" + title + "/" + user["Present"]["user_group"]
                else:
                    src_dir = "Report/" + title + "/" + user["Present"]["user_group"]
                for f in os.listdir(src_dir):
                    if searchstring in f and os.path.isfile(os.path.join(src_dir, f)):
                        photo = open(os.path.join(src_dir, f), 'rb')
                        update.bot.send_photo(chat_id=bot.message.chat.id, photo=photo)
                i = i + 1
                Report = "Report." + report_category + "." + unit_report + "." + dock + ".check"
                Reason = "Report." + report_category + "." + unit_report + "." + dock + ".reason"
                Officer = "Report." + report_category + "." + unit_report + "." + dock + ".officer"
                print("Сейчас обновлю")
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Reason: "Отправьте доклад повторно. Техническая неполадка",
                                               Officer: str(bot.message.chat.id)}})
                Report = "Report." + report_category + "." + unit_report + ".check_report"
                Officer = "Report." + report_category + "." + unit_report + ".officer"
                mdb.users.update_one({"user_id": user["user_id"]},
                                     {"$set": {Report: 2,
                                               Officer: str(bot.message.chat.id)}})
            reply_keyboard = [["Доклад принят. Приступить к следующему"],
                              ["Доклад не принят."],
                              ["Я устал. Вернуться в меню!"]]
            bot.message.reply_text(
                user["Present"]["user_group"] + " " + user["Present"]["user_lastname"] + ' ' + user["Present"][
                    "user_name"] + " " + user["Present"]["user_middlename"] + '\n' + user["Present"][
                    "user_phone"] + "\n" + title,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
            return "zagruzka_v_bd_kursant"
        except Exception as ex:
            check_user = check_point(mdb, bot.effective_user)
            bot.message.reply_text('У товарища ' + user["Present"]["user_lastname"] + " какие то проблемы с этим докладом. Надо звонить Широкопетлеву")
            reply_keyboard = [["Математический анализ"],
                              ["Аналитическая геометрия и линейная алгебра"],
                              ["Вернуться в меню!"]]
            bot.message.reply_text('Выберите категорию',
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                    one_time_keyboard=True))
            return "type_doklad_kursant"
    except Exception as ex:
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('У данного задания все отчеты проверены! Выберите другое задание')
        reply_keyboard = [["Математический анализ"],
                          ["Аналитическая геометрия и линейная алгебра"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите категорию',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "type_doklad_kursant"

def check_doklad_kursant(bot, update):
    SOS(bot)
    reply_keyboard = [["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "type_doklad_kursant"

def check_kursants(bot, update):
    SOS(bot)
    cur_count = mdb.users.find({"Present.check_present": 7})
    text = ""
    for doc in cur_count:
        count = str(doc["Present"]["count"])
        text = text + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " проверил<b> " + count + " </b>работ(ы, у)\n"
    bot.message.reply_text(text, parse_mode=telegram.ParseMode.HTML)

def get_choice_rating(bot, update):
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    if bot.message.text == "Кинофильмы":
        ok = "film_rate_ok"
        process = "film_rate_process"
        bad = "film_rate_bad"
        problem = "film_rate_problem"
        sum = 22
    if bot.message.text == "Литературный произведения":
        ok = "book_rate_ok"
        process = "book_rate_process"
        bad = "book_rate_bad"
        problem = "book_rate_problem"
        sum = 9
    if bot.message.text == "Математический анализ":
        ok = "mathematic_rate_ok"
        process = "mathematic_rate_process"
        bad = "mathematic_rate_bad"
        problem = "mathematic_rate_problem"
        sum = 19
    if bot.message.text == "Аналитическая геометрия и линейная алгебра":
        ok = "analitic_rate_ok"
        process = "analitic_rate_process"
        bad = "analitic_rate_bad"
        problem = "analitic_rate_problem"
        sum = 12
    bot.message.reply_text("Необходимо подождать! Небыстрое дело.", parse_mode=ParseMode.HTML)
    print(str(bot.effective_user.id) + " запросил рейтинг")
    rating = "<b>Рейтинг курса по представлению отчетов по индивидуальным заданиям</b> показан в виде:\n" \
             "Место - Группа - Ф.И. - Принятые доклады✅/На обработке⏳/Не представленные⚠/Непринятые⛔\n Поехали: \n"
    count = 1
    cur = mdb.users.find()
    cur = cur.sort([("Present.user_group", 1),("Present.rating" + bad, 1),("Present.rating" + problem, 1)])

    for doc in cur:
        try:
            try:
                if doc["user_id"] == bot.effective_user.id:
                    mesto = str(count)
                if doc["Present"]["check_present"] == 2 or doc["Present"]["check_present"] == 3 or doc["Present"]["check_present"] == 4:
                    rating = rating + "<b>" + str(count) + ".</b> "\
                        + doc["Present"]["user_group"] + " " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " \
                        + str(doc["Present"]["rating"][ok]) + "✅/ " + str(doc["Present"]["rating"][process]) + "⏳/ " + str(doc["Present"]["rating"][bad]) + "⚠/ "  + str(doc["Present"]["rating"][problem]) + "⛔\n"

                    count = count + 1
                    if count == 65:
                        bot.message.reply_text(rating, parse_mode=ParseMode.HTML)
                        rating = ""
            except Exception as ex:
                b = "ok"
        except Exception as ex:
            b = "ok"
    bot.message.reply_text(rating + "\nВаше место:<b> " + mesto + "</b>", parse_mode=ParseMode.HTML)
    rating_901_ok = 0
    rating_903_ok = 0
    rating_904_ok = 0
    rating_905_1_ok = 0
    rating_905_2_ok = 0
    rating_906_ok = 0
    rating_901_process = 0
    rating_903_process = 0
    rating_904_process = 0
    rating_905_1_process = 0
    rating_905_2_process = 0
    rating_906_process = 0
    rating_901_bad = 0
    rating_903_bad = 0
    rating_904_bad = 0
    rating_905_1_bad = 0
    rating_905_2_bad = 0
    rating_906_bad = 0
    rating_901_problem = 0
    rating_903_problem = 0
    rating_904_problem = 0
    rating_905_1_problem = 0
    rating_905_2_problem = 0
    rating_906_problem = 0
    cur = mdb.users.find()
    for doc in cur:
        try:

            try:
                    if doc["Present"]["user_group"] == "901":
                        rating_901_ok = rating_901_ok + doc["Present"]["rating"][ok]
                        rating_901_process = rating_901_process + doc["Present"]["rating"][process]
                        rating_901_bad = rating_901_bad + doc["Present"]["rating"][bad]
                        rating_901_problem = rating_901_problem + doc["Present"]["rating"][problem]
                    if doc["Present"]["user_group"] == "903":
                        rating_903_ok = rating_903_ok + doc["Present"]["rating"][ok]
                        rating_903_process = rating_903_process + doc["Present"]["rating"][process]
                        rating_903_bad = rating_903_bad + doc["Present"]["rating"][bad]
                        rating_903_problem = rating_903_problem + doc["Present"]["rating"][problem]
                    if doc["Present"]["user_group"] == "904":
                        rating_904_ok = rating_904_ok + doc["Present"]["rating"][ok]
                        rating_904_process = rating_904_process + doc["Present"]["rating"][process]
                        rating_904_bad = rating_904_bad + doc["Present"]["rating"][bad]
                        rating_904_problem = rating_904_problem + doc["Present"]["rating"][problem]
                    if doc["Present"]["user_group"] == "905-1":
                        rating_905_1_ok = rating_905_1_ok + doc["Present"]["rating"][ok]
                        rating_905_1_process = rating_905_1_process + doc["Present"]["rating"][process]
                        rating_905_1_bad = rating_905_1_bad + doc["Present"]["rating"][bad]
                        rating_905_1_problem = rating_905_1_problem + doc["Present"]["rating"][problem]
                    if doc["Present"]["user_group"] == "905-2":
                        rating_905_2_ok = rating_905_2_ok + doc["Present"]["rating"][ok]
                        rating_905_2_process = rating_905_2_process + doc["Present"]["rating"][process]
                        rating_905_2_bad = rating_905_2_bad + doc["Present"]["rating"][bad]
                        rating_905_2_problem = rating_905_2_problem + doc["Present"]["rating"][problem]
                    if doc["Present"]["user_group"] == "906":
                        rating_906_ok = rating_906_ok + doc["Present"]["rating"][ok]
                        rating_906_process = rating_906_process + doc["Present"]["rating"][process]
                        rating_906_bad = rating_906_bad + doc["Present"]["rating"][bad]
                        rating_906_problem = rating_906_problem + doc["Present"]["rating"][problem]
            except Exception as ex:
                b = "ok"
        except Exception as ex:
            b = "ok"
    rating_group= "<b>Учет докладов групп </b> представлен в виде:\n" \
             "Группа - Количество принятых докладов✅/Не обработанных⏳/Не представленных⚠/Непринятых⛔\n"
    rating_group = rating_group + "901 учебная группа - " + str(rating_901_ok) + "✅/ " + str(rating_901_process) + "⏳/ " + str(rating_901_bad) + "⚠/ "  + str(rating_901_problem) + "⛔\n" + \
                   "903 учебная группа - " + str(rating_903_ok) + "✅/ " + str(rating_903_process) + "⏳/ " + str(rating_903_bad) + "⚠/ "  + str(rating_903_problem) + "⛔\n" + \
                   "904 учебная группа - " + str(rating_904_ok) + "✅/ " + str(rating_904_process) + "⏳/ " + str(rating_904_bad) + "⚠/ "  + str(rating_904_problem) + "⛔\n" + \
                   "905-1 учебная группа - " + str(rating_905_1_ok) + "✅/ " + str(rating_905_1_process) + "⏳/ " + str(rating_905_1_bad) + "⚠/ "  + str(rating_905_1_problem) + "⛔\n" + \
                   "905-2 учебная группа - " + str(rating_905_2_ok) + "✅/ " + str(rating_905_2_process) + "⏳/ " + str(rating_905_2_bad) + "⚠/ "  + str(rating_905_2_problem) + "⛔\n" + \
                   "906 учебная группа - " + str(rating_906_ok) + "✅/ " + str(rating_906_process) + "⏳/ " + str(rating_906_bad) + "⚠/ "  + str(rating_906_problem) + "⛔\n"
    bot.message.reply_text(rating_group, parse_mode=ParseMode.HTML)
    rating_group= "<b>Учет докладов групп </b>представлен в виде:\n" \
             "Группа - Процент(%) принятых докладов✅/Не обработанных⏳/Не представленных⚠/Непринятых⛔\n"
    rating_group = rating_group + "901 учебная группа - " + str(round(rating_901_ok * 100 / (sum * 23),2)) + "%✅/ " + str(round(rating_901_process * 100 / (sum * 23),2)) + "%⏳/ " + str(round(rating_901_bad * 100 / (sum * 23),2)) + "%⚠/ "  + str(round(rating_901_problem * 100 / (sum * 23),2)) + "%⛔\n" + \
                   "903 учебная группа - " + str(round(rating_903_ok * 100 / (sum * 15),2)) + "%✅/ " + str(round(rating_903_process * 100 / (sum * 15),2)) + "%⏳/ " + str(round(rating_903_bad * 100 / (sum * 15),2)) + "%⚠/ "  + str(round(rating_903_problem * 100 / (sum * 15),2)) + "%⛔\n" + \
                   "904 учебная группа - " + str(round(rating_904_ok * 100 / (sum * 15),2)) + "%✅/ " + str(round(rating_904_process * 100 / (sum * 15),2)) + "%⏳/ " + str(round(rating_904_bad * 100 / (sum * 15),2)) + "%⚠/ "  + str(round(rating_904_problem * 100 / (sum * 15),2)) + "%⛔\n" + \
                   "905-1 учебная группа - " + str(round(rating_905_1_ok * 100 / (sum * 29),2)) + "%✅/ " + str(round(rating_905_1_process * 100 / (sum * 29),2)) + "%⏳/ " + str(round(rating_905_1_bad * 100 / (sum * 29),2)) + "%⚠/ "  + str(round(rating_905_1_problem * 100 / (sum * 29),2)) + "%⛔\n" + \
                   "905-2 учебная группа - " + str(round(rating_905_2_ok * 100 / (sum * 29),2)) + "%✅/ " + str(round(rating_905_2_process * 100 / (sum * 29),2)) + "%⏳/ " + str(round(rating_905_2_bad * 100 / (sum * 29),2)) + "%⚠/ "  + str(round(rating_905_2_problem * 100 / (sum * 29),2)) + "%⛔\n" + \
                   "906 учебная группа - " + str(round(rating_906_ok * 100 / (sum * 15),2)) + "%✅/ " + str(round(rating_906_process * 100 / (sum * 15),2)) + "%⏳/ " + str(round(rating_906_bad * 100 / (sum * 15),2)) + "%⚠/ "  + str(round(rating_906_problem * 100 / (sum * 15),2)) + "%⛔\n"
    bot.message.reply_text(rating_group, parse_mode=ParseMode.HTML)
    bot.message.reply_text("Рейтинг представлен🏆!", parse_mode=ParseMode.HTML)
    print(str(bot.effective_user.id) + " посмотрел рейтинг")
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
    return ConversationHandler.END