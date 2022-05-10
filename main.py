import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters 
import googletrans
from googletrans import Translator
import csv


translator = Translator()

user_preference = {}

reply_keyboard = [['/help'], ['/start']]
markup_1 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard = [['/lang RUSSIAN', '/lang FRENCH'],
                  ['/lang JAPANESE', '/lang ENGLISH']]
markup_2 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder='Примеры:')

all_lang = googletrans.LANGUAGES
langcodes = dict(map(reversed,all_lang.items()))

def start(update, context):
    message = "Привет, " + update.message.from_user.first_name + '. Я — бот-переводчик. Напиши /help, чтобы узнать, как я работаю.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup_1)
    file = open('userdata.csv')
    reader = csv.reader(file)
    rows = []
    for row in reader:
        rows.append(row)
    print(rows)
    user = update.message.from_user.username
    msgs = list()
    for row in rows:
        row = row[0].split(';')
        if row[0] == update.message.from_user.first_name:
            print(row)
            msg = row[1]
            msgs.append(msg)
    msg = msgs[-1]
    text_message = 'Ваш текущий язык перевода — ' + str((translator.translate(msg,dest = 'Russian')).text) + '. Для смены введите команду /lang.'
    context.bot.send_message(chat_id=update.effective_chat.id, text = text_message)
            
            

def check_lang(update,context):
    user = update.message.from_user.username
    try:
        send_message = "Текущий язык перевода: " + user_preference[user].upper()
        context.bot.send_message(chat_id = update.effective_chat.id, text = send_message)
    except:
        send_message = "Языка перевода не выбрано."
        context.bot.send_message(chat_id = update.effective_chat.id, text = send_message)

def set_preferences(update,context):
    user = update.message.from_user.username
    msg = update.message.text
    msg = msg[5:].strip()
    msg = msg.lower()
    if len(msg) == 0:
        context.bot.send_message(chat_id = update.effective_chat.id, text = "Нет параметра. Пожалуйста, запустите команду с его указанием.", reply_markup=markup_2)
    elif msg not in langcodes.keys():
        context.bot.send_message(chat_id=update.effective_chat.id, text = "Данный язык не поддерживается переводчиком.", reply_markup=markup_2)
    else:
        try:
            user_preference[user] = msg
        except:
            user_preference[user] = msg
        with open('userdata.csv', 'a', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            listn = [update.message.from_user.first_name, msg]
            print(listn)
            writer.writerow([update.message.from_user.first_name, msg])        
        text_message = str((translator.translate(msg,dest = 'Russian')).text) + " выбран языком перевода для " + update.message.from_user.first_name
        context.bot.send_message(chat_id=update.effective_chat.id, text = text_message)

def translate(update,context):
    user = update.message.from_user.username
    try:
        translation_language = user_preference[user]
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text = "Вы не выбрали язык перевода.", reply_markup=markup_2)
        return
    msg = update.message.text
    msg = msg[10:]
    if len(msg) == 0:
        context.bot.send_message(chat_id = update.effective_chat.id, text = "Нет параметра. Пожалуйста, запустите команду с его указанием.")
    else:
        msg = msg.strip().lower()
        translated = translator.translate(msg,dest = translation_language)
        send_message = "Результат перевода: " + str(translated.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text = send_message)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, такой команды не существует.")
    
def help(update, context):
    update.message.reply_text(
        """Привет, сейчас расскажу, что я умею делать.
        Введи /lang <ЯЗЫК> (напр. /lang russian), чтобы выбрать язык, на который ты хочешь переводить.
        Введи /translate <ТЕКСТ>, чтобы перевести введенный текст на твой язык.
        Введи /check <ТЕКСТ>, чтобы узнать язык, на котором написан введенный текст.""")

def check_language(update,context):

    msg = update.message.text
    msg = msg[6:]
    if len(msg) == 0:
        context.bot.send_message(chat_id = update.effective_chat.id, text = "Нет параметра. Пожалуйста, запустите команду с его указанием.")
    else:
        msg = msg.strip()
        language = translator.detect(msg)
        lang_text = all_lang[language.lang.lower()]
        send_message = "Язык: " + str((translator.translate(lang_text, dest = 'Russian')).text)
        context.bot.send_message(chat_id = update.effective_chat.id, text = send_message)

def main():
    bot = telegram.Bot(token='5226011940:AAEhdKWz47emj30M02sTlNueUHWo2cOr2wo')
    updater = Updater(token='5226011940:AAEhdKWz47emj30M02sTlNueUHWo2cOr2wo', use_context = True)
    dispatcher = updater.dispatcher
    print('bot started')
    dispatcher.add_handler(CommandHandler("start", start, pass_args = True))
    dispatcher.add_handler(CommandHandler("help", help, pass_args = True))
    dispatcher.add_handler(CommandHandler("translate", translate, pass_args = True))
    dispatcher.add_handler(CommandHandler("check", check_language, pass_args = True))
    dispatcher.add_handler(CommandHandler("lang", set_preferences, pass_args = True))
    dispatcher.add_handler(CommandHandler("checklang", check_lang, pass_args = True))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
