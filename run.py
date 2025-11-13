import asyncio
import logging
from handlers import router
from aiogram import Dispatcher
from time import gmtime, strftime
from aiogram import Bot
from settings import TG_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers import collection
import datetime
import keyboards as kb
from aiogram.types import FSInputFile
from geopy.distance import geodesic
from time import gmtime, strftime
import logging

scheduler = AsyncIOScheduler()

bot = Bot(token=TG_TOKEN)

async def go_report():
    cur = collection.find()
    async for doc in cur:
        try:
            if doc["Present"]['user_unit'] == "Начальник курса" or doc["Present"]['user_unit'] == "Курсовой офицер" or doc["Present"]['user_unit'] == "НФ" or doc["Present"]['user_unit'] == "ЗНФ":
                continue
            if doc["Present"]['user_status'] == "В наряде":
                continue
            if doc["Present"]['user_status'] == "В лазарете":
                continue
            if doc["Present"]['user_status'] == "В казарме":
                continue
            time = datetime.datetime.now()
            if 0 <= time.hour <= 12:
                time_of_day = "morning"
            else:
                time_of_day = "evening"
            day = time.strftime("%d-%m-%Y")
            number = "number " + time_of_day
            number = doc["Facts"][day][number]["number"]
        except Exception as e:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Обнаружен не доложивший. Пробую его предупредить: " + str(e))
            logging.info("Обнаружен не доложивший. Пробую его предупредить: " + str(doc))
            try:
                await bot.send_message(chat_id=doc["user_id"], text="Приветствую! Не поступил доклад о состоянии дел, для отметки или изменения статуса нажми на кнопку ниже! Доброй ночи!", reply_markup=kb.go_report_keyboard)
            except Exception as e:
                try:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + str(doc) + " не получил информацию, ошибка: " + str(e))
                    await collection.update_one({"user_id": doc['user_id']},
                                                {"$set": {"private": "Включен режим приватности"}})
                    logging.info(str(doc) + " не получил информацию")
                    continue
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Ошибка отправки в базу данных: " + str(doc) + " Ошибка: " + str(e))
                    logging.info("Ошибка отправки в базу данных:" + str(doc) + " Ошибка: " + str(e))
                    continue

async def go_report_komandir():
    global cursor
    cur = collection.find()
    async for doc in cur:
        try:
            year_nabor = doc['Present']['year_nabor']
            fakultet = doc['Present']['fakultet']
            user_group = doc['Present']['user_group']
            user_unit = doc['Present']['user_unit']
            if (user_unit == "Курсант 3 отд-я"
                    or user_unit == "Курсант 2 отд-я"
                    or user_unit == "Курсант 1 отд-я"):
                continue
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

            if user_unit == "Начальник курса" or user_unit == "Курсовой офицер" or user_unit == "Старшина курса" :
                try:
                    cursor = collection.find({
                        "Present.year_nabor": year_nabor,
                        "Present.fakultet": fakultet
                    })
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "  Ошибка при поиске 1 " + str(e))
            if user_unit == "НФ" or user_unit == "ЗНФ":
                try:
                    cursor = collection.find({
                        "Present.fakultet": fakultet
                    })
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "  Ошибка при поиске 2 " + str(e))
            if user_unit == "Командир учебной группы":
                try:
                    cursor = collection.find({
                        "Present.year_nabor": year_nabor,
                        "Present.fakultet": fakultet,
                        "Present.user_group": user_group
                    })
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "  Ошибка при поиске 3 " + str(e))
            if user_unit == "Командир 1 отд-я":
                try:
                    cursor = collection.find({
                        "Present.year_nabor": year_nabor,
                        "Present.fakultet": fakultet,
                        "Present.user_group": user_group,
                        "Present.user_unit": "Курсант 1 отд-я"
                    })
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "  Ошибка при поиске 4 " + str(e))
            if user_unit == "Командир 2 отд-я":
                try:
                    cursor = collection.find({
                        "Present.year_nabor": year_nabor,
                        "Present.fakultet": fakultet,
                        "Present.user_group": user_group,
                        "Present.user_unit": "Курсант 2 отд-я"
                    })
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "  Ошибка при поиске 5 " + str(e))
            if user_unit == "Командир 3 отд-я":
                try:
                    cursor = collection.find({
                        "Present.year_nabor": year_nabor,
                        "Present.fakultet": fakultet,
                        "Present.user_group": user_group,
                        "Present.user_unit": "Курсант 3 отд-я"
                    })
                except Exception as e:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "  Ошибка при поиске 6 " + str(e))
            #cursor = cursor.sort("Present.user_group", 1)
            async for document in cursor:
                if document["Present"]['user_unit'] == "Начальник курса" or document["Present"][
                    'user_unit'] == "Курсовой офицер" or document["Present"]['user_unit'] == "НФ" or document["Present"][
                    'user_unit'] == "ЗНФ":
                    continue
                if document["Present"]['user_status'] == "В наряде":
                    score_on_service = score_on_service + 1
                    on_service = on_service + "\n<b>" + document["Present"]["user_group"] + " " + str(
                        score_on_service) + ".</b>" + \
                                 document["Present"]["user_lastname"] + " " + document["Present"]["user_name"] + " " + \
                                 document["Present"][
                                     "user_middlename"] + "<br>"
                    continue
                if document["Present"]['user_status'] == "В лазарете":
                    score_lazaret = score_lazaret + 1
                    lazaret = lazaret + "\n<b>" + document["Present"]["user_group"] + " " + str(score_lazaret) + ".</b>" + \
                              document["Present"]["user_lastname"] + " " + document["Present"]["user_name"] + " " + \
                              document["Present"][
                                  "user_middlename"] + "<br>"
                    continue
                if document["Present"]['user_status'] == "В казарме":
                    score_kazarma = score_kazarma + 1
                    kazarma = kazarma + "\n<b>" + document["Present"]["user_group"] + " " + str(score_kazarma) + ".</b>" + \
                              document["Present"]["user_lastname"] + " " + document["Present"]["user_name"] + " " + \
                              document["Present"][
                                  "user_middlename"] + "<br>"
                    continue
                if document["Present"]['user_status'] == "В отпуске":
                    score_otpusk = score_otpusk + 1
                if document["Present"]['user_status'] == "В госпитале":
                    score_hospital = score_hospital + 1
                if document["Present"]['user_status'] == "В увольнении":
                    score_yvolnenie = score_yvolnenie + 1
                if document["Present"]['user_status'] == "В командировке":
                    score_komandirovka = score_komandirovka + 1
                if document["Present"]['user_status'] == "Вне общежития":
                    score_vnekazarm = score_vnekazarm + 1
                number = "number " + time_of_day
                try:
                    number = document["Facts"][day][number]["number"]
                    number = str(number) + " " + time_of_day
                    score_all_ok = score_all_ok + 1
                    try:
                        count_address = document["Present"]["address"]["count"]
                        i = 0
                        distance = []
                        while i <= count_address:
                            home = (float(document["Present"]["address"][str(i)]["latitude"]),
                                    float(document["Present"]["address"][str(i)]["longitude"]))
                            point = (float(document["Facts"][day][number]["latitude"]),
                                     float(document["Facts"][day][number]["longitude"]))
                            distance.append(geodesic(point, home).m)
                            i = i + 1
                        i = 0
                        distance_min = 10000000000
                        while i <= count_address:
                            home = (float(document["Present"]["address"][str(i)]["latitude"]),
                                    float(document["Present"]["address"][str(i)]["longitude"]))
                            point = (float(document["Facts"][day][number]["latitude"]),
                                     float(document["Facts"][day][number]["longitude"]))
                            if geodesic(point, home).m <= distance_min:
                                distance_min = geodesic(point, home).m
                            i = i + 1
                        if min(distance) < 500:
                            all_ok = all_ok + "\n<b>" + document["Present"]["user_group"] + " " + str(
                                score_all_ok) + ".</b></span> " + document["Present"]["user_lastname"] + " " + \
                                     document["Present"]["user_name"] + " " + document["Present"]["user_middlename"] + "<br>" \
                                     + "\n<b>Время отметки: </b>" + document["Facts"][day][number][
                                         "time"] + " <b>Место отметки: </b>" + str(
                                document["Facts"][day][number]["latitude"]) + ", " + str(
                                document["Facts"][day][number]["longitude"]) + "<br>" \
                                     + "\n<b>Расстояние до места проживания: </b>" + str(
                                round(min(distance))) + " метров<br><span style='background-color:#00FF00'>"
                        else:
                            all_ok_daleko = all_ok_daleko + "<b>" + document["Present"]["user_group"] + ".</b>" + \
                                            document["Present"]["user_lastname"] + " " + document["Present"]["user_name"] + " " + \
                                            document["Present"]["user_middlename"] + ","
                    except Exception as ex:
                        all_ok = all_ok + "\n<b>" + document["Present"]["user_group"] + " " + str(
                            score_all_ok) + ".</b></span> " + document["Present"]["user_lastname"] + " " + \
                                 document["Present"]["user_name"] + " " + document["Present"]["user_middlename"] + "<br>" \
                                 + "\n<b>Время отметки: </b>" + document["Facts"][day][number][
                                     "time"] + " <b>Место отметки: </b>" + str(
                            document["Facts"][day][number]["latitude"]) + ", " + str(
                            document["Facts"][day][number]["longitude"]) + "<br>" \
                                 + "\n<span style='background-color:#FF0000'><b>У курсанта командованием курса не введены адреса проживания!</b></span><span style='background-color:#00FF00'>" + "<br>"
                except Exception as ex:
                    score_not_ok = score_not_ok + 1
                    try:
                        not_ok = not_ok + "<b>" + document["Present"]["user_group"] + ".</b>" + document["Present"][
                            "user_lastname"] + " " + \
                                 document["Present"]["user_name"] + " " + document["Present"]["user_middlename"] + ","
                    except Exception as ex:
                        not_ok = not_ok + "<b>" + document["Present"]["user_group"] + ".</b>" + document["Present"][
                            "user_lastname"] + " " + \
                                 document["Present"]["user_name"] + " " + document["Present"]["user_middlename"] + ","
            f = open("Report/" + day + " " + time_of_day + " " + doc['Present']['user_lastname'] + " fast.html", 'w')
            day = time.strftime("%d.%m.%Y")
            itog = "Привет командир! \n На <b>" + day + " </b> обстановка следующая:\n" + "<b>В системе зарегистрировано: </b>" + str(
                score_otpusk + score_komandirovka + score_kazarma + score_lazaret + score_hospital + score_yvolnenie + score_on_service + score_vnekazarm) + "\n" + \
                   "<b>Доклад поступил (включая отпуск, командировку, увольнение, госпиталь): </b>" + str(
                score_all_ok) + "\n" + \
                   "<b>Доклад не поступил: </b>" + str(score_not_ok) + "\n" + \
                   "<b>В казарме: </b>" + str(score_kazarma) + "\n" + \
                   "<b>В лазарете: </b>" + str(score_lazaret) + "\n" + \
                   "<b>В наряде: </b>" + str(score_on_service) + "\n"
            f = itog + not_ok + all_ok_daleko
            try:
                await bot.send_message(chat_id=doc["user_id"], text=f, parse_mode='HTML', reply_markup=kb.back_keyboard)
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " До " + doc["user_id"] + " информация доведена")
                logging.info("До " + doc["user_id"] + " информация доведена")
                if doc["Present"]["user_lastname"] == "Широкопетлев":
                    try:
                        await bot.send_message(-1003246610130, text=f, parse_mode='HTML')
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " До группы 93 курса информация доведена")
                        "До группы 93 курса информация доведена"
                    except Exception as ex:
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " До группы 93 курса информация не доведена, потому что ошибка: " + str(ex))
                        logging.info("До группы 93 курса информация не доведена, потому что ошибка: " + str(ex))
            except Exception as ex:
                itog = "Привет командир! \n На <b>" + day + " </b> обстановка следующая:<br>" + "<b>В системе зарегистрировано: </b>" + str(
                    score_otpusk + score_komandirovka + score_kazarma + score_lazaret + score_hospital + score_yvolnenie + score_on_service + score_vnekazarm) + "<br>" + \
                       "<b>Доклад поступил (включая отпуск, командировку, увольнение, госпиталь): </b>" + str(
                    score_all_ok) + "<br>" + \
                       "<b>Доклад не поступил: </b>" + str(score_not_ok) + "<br>" + \
                       "<b>В казарме: </b>" + str(score_kazarma) + "<br>" + \
                       "<b>В лазарете: </b>" + str(score_lazaret) + "<br>" + \
                       "<b>В наряде: </b>" + str(score_on_service) + "<br>"
                day = time.strftime("%d-%m-%Y")
                tekst = open(
                    "Report/" + day + " " + time_of_day + " " + doc['Present']['user_lastname'] + " fast.html",
                    'w')
                tekst.write(itog + "<br>" + not_ok + "<br><br>" + all_ok_daleko)
                tekst.close()
                tekst = FSInputFile(
                    "Report/" + day + " " + time_of_day + " " + doc['Present']['user_lastname'] + " fast.html")
                try:
                    await bot.send_document(doc["user_id"], tekst)
                    await bot.send_message(chat_id=doc["user_id"], text="Короткий доклад в файле выше.\n", reply_markup=kb.back_keyboard)
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " До " + doc["user_id"] + " короткий доклад файлом доведен")
                    logging.info("До " + doc["user_id"] + " короткий доклад файлом доведен")
                    if doc["Present"]["user_lastname"] == "Широкопетлев":
                        try:
                            await bot.send_document(-1003246610130, tekst)
                            await bot.send_message(chat_id=-1003246610130, text="Короткий доклад в файле выше.\n",
                                                   reply_markup=kb.back_keyboard)
                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " До 93 курса доклад файлом доведен")
                            logging.info("До 93 курса доклад файлом доведен")
                        except Exception as ex:
                            print(strftime("%Y-%m-%d %H:%M:%S",
                                           gmtime()) + " До группы 93 курса файл не доведен, потому что ошибка: " + str(ex))
                            logging.info("До группы 93 курса файл не доведен, потому что ошибка: " + str(ex))
                except Exception as ex:
                    try:
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + str(doc) + " не получил информацию и заработал ошибку: " + str(ex))
                        await collection.update_one({"user_id": doc['user_id']},
                                                    {"$set": {"private": "Включен режим приватности"}})
                        logging.info(str(doc) + " не получил информацию и заработал ошибку: " + str(ex))
                    except Exception as ex:
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + str(doc) + " Ошибка отправки в базу данных: " + str(ex))
                        logging.info(str(doc) + " Ошибка отправки в базу данных: " + str(ex))
        except Exception as e:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + str(doc) + " Ошибка при доведении информации командирам: " + str(e))
            logging.info(str(doc) + " Ошибка при доведении информации командирам: " + str(e))
            pass
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

async def main():
    # Объект бота
    # Диспетчер
    dp = Dispatcher()
    dp.include_router(router)
    scheduler.add_job(go_report_komandir, "cron", hour=22)
    scheduler.add_job(go_report, "cron", hour=21, minute=58)
    scheduler.add_job(go_report, "cron", hour=22, minute=15)
    scheduler.add_job(go_report, "cron", hour=22, minute=30)
    scheduler.add_job(go_report, "cron", hour=22, minute=45)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " Бот выключен.")