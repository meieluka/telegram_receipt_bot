import logging
import datetime
import receipt_helper
from receipt_class import receipt
import google_sheets
import os
import config

import telebot
from telebot import types
from telebot_calendar import Calendar, CallbackData, GERMAN_LANGUAGE

from telebot.types import ReplyKeyboardRemove, CallbackQuery

API_TOKEN = config.API_TOKEN  #API token received from BotFather
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(API_TOKEN)

user_receipt = receipt( datetime.datetime.now, 0, "", "", 0, "", "", "", "", 0, 0)

# Creates a unique calendar
calendar = Calendar(language=GERMAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
receipt_1_callback = CallbackData("receipt_1", "action")


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(receipt_1_callback.prefix)
)
@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)
def callback_inline(call: CallbackQuery):
    print("Message: " + str(call.message))
    if call.message.chat.type != "private":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Gruppenchats werden noch nicht vollständig unterstützt, sorry.",
        )
        return 0
    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    if(call.data.startswith(calendar_1_callback.prefix)):
        name, action, year, month, day = call.data.split(calendar_1_callback.sep)
        date = calendar.calendar_query_handler(
           bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
        )
    elif call.data.startswith(receipt_1_callback.prefix):
        name,action = call.data.split(receipt_1_callback.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    #date = calendar.calendar_query_handler(
    #    bot=bot, call=call, name=name, action=action
    #)
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    now = datetime.datetime.now()  # Get the current date
    if action == "NEW_RECEIPT":
        user_receipt.first_name = call.message.from_user.first_name
        user_receipt.last_name = call.message.from_user.last_name
        user_receipt.username = call.message.from_user.username
        bot.edit_message_text(
            text="*Quittung abgeben:* Wähle das Datum: ",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode= 'Markdown',
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,  # Specify the NAME of your calendar
            ),
        )
    elif action == "SHOW_RECEIPTS":
        bot.edit_message_text(
            text="Das sind alle deine Quittungen (Fotos werden nicht gezeigt): ",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode= 'Markdown',
            )
        send_user_receipts(call.message)

    if action == "DAY":
    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    # Processing the calendar. Get either the date or None if the buttons are of a different type
        user_receipt.date = datetime.datetime(int(year), int(month), int(day))
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Datum: {date.strftime('%d.%m.%Y')} \nWähle nun den Anlass:",
            reply_markup= receipt_helper.get_cause(
                    name=name,
                ),
        )
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Cancellation")

    elif action == "SOLA21":
        user_receipt.cause = "Sola 2021"
        bot.edit_message_text(
            text="*Sola21* ausgewählt",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode= 'Markdown',
            )
        msg = bot.send_message(
            chat_id=call.message.chat.id,
            text="Bitte gib einen Zweck an (z.B. Essen, Höckverpflegung etc.): ",
        )
        bot.register_next_step_handler(msg, purpose)

    elif action == "OTHER":
        msg = bot.edit_message_text(
            text="Bitte gib einen Anlass inkl. Jahr an (z.B. Sola21, Schlüraclette19 etc.): ",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode= 'Markdown',
            )
        bot.register_next_step_handler(msg, cause)

def send_user_receipts(message):
    print("USER_ID::" + str(message.chat.id) + "username: " + message.from_user.username)

    values = google_sheets.read_js_name(user_receipt.js_name)
    if len(values) == 0:
        msg = bot.send_message(
            chat_id=message.chat.id,
            text="Du hast noch keine Quittung hinzugefügt.",
        )
    else:
        total_value = 0
        for value in values:
            _timestamp = value[0]
            _date = value[1]
            _cause = value[2]
            _purpose = value[3]
            _user_id = value[4]
            _username = value[5]
            _js_name = value[6]
            _first_name = value[7]
            _last_name = value[8]
            _total = value[9]
            total_value += float(_total)
            msg = bot.send_message(
                parse_mode= 'Markdown',
                chat_id=message.chat.id,
                text="Quittung vom *" + _date + "* \n"\
                    "hinzugefügt am " + _timestamp + "\n"\
                    "von \'" + _js_name + "\', hinzugefügt von " + _first_name + " " + _last_name +\
                    "\nAnlass: " + _cause + "\n"\
                    "Zweck: " + _purpose + "\n"\
                    "Totalbetrag: " + _total + " CHF\n",
            )
        msg = bot.send_message(
                parse_mode= 'Markdown',
                chat_id=message.chat.id,
                text="Du hast *" + str(len(values)) + " Quittungen* abgegeben\n"\
                    "und wirst " + str(total_value) + " CHF erhalten\n"
            )

def get_js_name(message):
    if check_cancel(message):
        bot.reply_to(message, 'Abbruch, Daten gelöscht!')
    else:
        try:
            user_receipt.js_name = str(message.text)
            send_user_receipts(message)
        except Exception as e:
            print(e)
            bot.reply_to(message, 'Ein Fehler ist aufgetaucht, benachrichtige Hornet falls das Problem weiterhin besteht!')

def get_name(message):
    if check_cancel(message):
        bot.reply_to(message, 'Abbruch, Daten gelöscht!')
    else:
        try:
            user_receipt.js_name = message.text
            msg = bot.reply_to(message, 'Hallo ' + user_receipt.js_name + '\nWas möchtest du tun?',
            reply_markup=receipt_helper.start(
                name=receipt_1_callback.prefix
            ))
        except Exception as e:
            bot.reply_to(message, 'Ein Fehler ist aufgetaucht, benachrichtige Hornet falls das Problem weiterhin besteht!')

def cause(message):
    if check_cancel(message):
        user_receipt.date = 0
        bot.reply_to(message, 'Abbruch, Daten gelöscht!')
    else:
        try:
            user_receipt.cause = message.text
            msg = bot.reply_to(message, 'Bitte gib einen Zweck an (z.B. Essen, Höckverpflegung etc.): ')
            bot.register_next_step_handler(msg, purpose)
        except Exception as e:
            bot.reply_to(message, 'Ein Fehler ist aufgetaucht, benachrichtige Hornet falls das Problem weiterhin besteht!')

def purpose(message):
    if check_cancel(message):
        user_receipt.date = 0
        bot.reply_to(message, 'Abbruch, Daten gelöscht!')
    else:
        try:
            user_receipt.purpose = message.text
            msg = bot.reply_to(message, 'Bitte gib nun den Totalbetrag ein (bsp: "12.35"):')
            bot.register_next_step_handler(msg, total)
        except Exception as e:
            bot.reply_to(message, 'Ein Fehler ist aufgetaucht, benachrichtige Hornet falls das Problem weiterhin besteht!')

def total(message):
    if check_cancel(message):
        user_receipt.date = 0
        bot.reply_to(message, 'Abbruch, Daten gelöscht!')
    elif(check_if_number(message.text) == 0):
        msg = bot.reply_to(message, 'Bitte gib einen korrekten Totalbetrag ein (bsp: "12.35"):')
        bot.register_next_step_handler(msg, total)
    else:
        try:
            user_receipt.first_name = message.from_user.first_name
            user_receipt.last_name = message.from_user.last_name
            user_receipt.username = message.from_user.username
            user_receipt.user_id = message.from_user.id
            user_receipt.total = message.text
            msg = bot.reply_to(message, 'Mache nun ein Foto von der Quittung und schicke sie mir: ')
            bot.register_next_step_handler(msg, picture)
        except Exception as e:
            bot.reply_to(message, 'Ein Fehler ist aufgetaucht, benachrichtige Hornet falls das Problem weiterhin besteht!')

def picture(message):
    if check_cancel(message):
        user_receipt.date = 0
        bot.reply_to(message, 'Abbruch, Daten gelöscht!')
    elif(message.content_type  != "photo"):
        msg = bot.reply_to(message, 'Bitte schicke ein Foto von der Quittung:')
        bot.register_next_step_handler(msg, picture)
    else:
        user_receipt.timestamp = datetime.datetime.now()
        download_photo(message)
        try:
            bot.send_message(
                chat_id=message.from_user.id,
                text="Deine Quittung wurde erfolgreich gespeichert!",
            )
        except Exception as e:
            bot.reply_to(message, 'Ein Fehler ist aufgetaucht, benachrichtige Hornet falls das Problem weiterhin besteht!')

def download_photo(message):
    print ('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print ('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print ('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)
    
    date = user_receipt.date
    date = date.strftime('%Y-%m-%d')

    timestamp = user_receipt.timestamp

    user_receipt.picture = user_receipt.js_name + "-" + str(user_receipt.total) + "CHF" + "-" + date +"-"+ str(timestamp) + ".jpg"
    with open("photos/"+ user_receipt.picture, 'wb') as new_file:
        new_file.write(downloaded_file)

    google_sheets.upload(user_receipt)

    os.remove("photos/"+user_receipt.picture)

def check(message):
    bot.send_message(
            chat_id=message.from_user.id,
            text="Deine Quittung wurde erfolgreich gespeichert!",
        )

def check_cancel(message):
    if message.text == "/cancel":
        return 1
    else:
        return 0

def check_if_number(number:str) -> float:
    try:
        if number.isdigit():
            how_much = int(number)
        elif "." in number:
            choice_dot = number
            choice_dot_remove = choice_dot.replace(".","")
            if choice_dot_remove.isdigit():
                how_much = float(number)
        else:
            return 0
        return how_much
    except Exception as e:
        return 0

@bot.message_handler(commands=["start", "help"])
def check_other_messages(message):
    """
    Catches a message with the command "start" and sends the calendar

    :param message:
    :return:
    """

    global state
    state = "start"


    if(state == "start"):
        msg = bot.send_message(
            message.chat.id,
            "Willkommen beim Quittungsbot von Hornet v1\nBitte gib deinen Jungscharnamen ein:",
        )
        bot.register_next_step_handler(msg, get_name)
    elif(state == "purpose"):
        if(user_receipt.date != 0):
            user_receipt.purpose = message.text
            bot.send_message(
                message.chat.id,
                "Zweck: " + message.text + " wurde gespeichert",
            )
        else:
            state = "start"
            bot.send_message(
                message.chat.id,
                "Ein Fehler ist aufgetaucht, Bot wird neugestartet!",
            )
def send_all_receipts(message):
    bot.send_message(
            text="Das sind alle Quittungen (Fotos werden nicht gezeigt): ",
            chat_id=message.chat.id,
            parse_mode= 'Markdown',
            )
    values = google_sheets.read_all()
    if len(values) == 0:
        msg = bot.send_message(
            chat_id=message.chat.id,
            text="Es wurden noch keine Quittungen hinzugefügt.",
        )
    else:
        total_value = 0
        for value in values:
            _timestamp = value[0]
            _date = value[1]
            _cause = value[2]
            _purpose = value[3]
            _user_id = value[4]
            _username = value[5]
            _js_name = value[6]
            _first_name = value[7]
            _last_name = value[8]
            _total = value[9]
            total_value += float(_total)
            msg = bot.send_message(
                parse_mode= 'Markdown',
                chat_id=message.chat.id,
                text="Quittung vom *" + _date + "* \n"\
                    "hinzugefügt am " + _timestamp + "\n"\
                    "von \'" + _js_name + "\', hinzugefügt von " + _first_name + " " + _last_name +\
                    "\nAnlass: " + _cause + "\n"\
                    "Zweck: " + _purpose + "\n"\
                    "Totalbetrag: " + _total + " CHF\n",
            )
        msg = bot.send_message(
                parse_mode= 'Markdown',
                chat_id= message.chat.id,
                text="Es wurden *" + str(len(values)) + " Quittungen* abgegeben.\n"\
                    "Gesamtbetrag: " + str(total_value) + " CHF\n"
            )

@bot.message_handler(commands=["allreceipts"])
def check_other_messages(message):
    """
    Catches a message with the command "start" and sends the calendar

    :param message:
    :return:
    """
    user_receipt = receipt( datetime.datetime.now, 0, "", "", 0, "", "", "", "", 0, 0)
    if(message.from_user.username == "meieluka"):
        send_all_receipts(message)
    else:
        msg = bot.send_message(
            chat_id= message.chat.id,
            text="Bitte gib einen Jungscharnamen ein: ",
        )
        bot.register_next_step_handler(msg, get_js_name)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(15)


