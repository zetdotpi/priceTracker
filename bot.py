import validators

from telegram import ParseMode, ReplyKeyboardMarkup, ReplyMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

from db import PriceTrackerDB
from config import BOT_API_KEY, DB_PATH, ACCESS_PASSWORD
        

AUTH = 0; MENU = 1
ENTRY_LIST = 10
ENTRY_ADD = 20; ENTRY_ADD_URL = 21
ENTRY_REMOVE = 30; ENTRY_REMOVE_CHOICE = 31

db = PriceTrackerDB(DB_PATH)

updater = Updater(BOT_API_KEY)
bot = updater.bot
#bot.send_message(chat_id=user_id, text='message itself')
def start(update: Update, context: CallbackContext) -> int:
    if db.user_id_exists(update.message.from_user.id):
        update.message.reply_text('Вы уже называли пароль. Я вас помню.')
        return ConversationHandler.END
    
    update.message.reply_text('Назовите пароль')
    return AUTH

def auth_enter(update: Update, context: CallbackContext) -> int:
    if update.message.text == ACCESS_PASSWORD:
        db.add_user_id(update.message.from_user.id)
        update.message.reply_text('Все, верно.')
        return ConversationHandler.END
    else:
        update.message.reply_text('Нет. Попытайтесь еще раз')
        return AUTH


def list_entries(update: Update, context: CallbackContext):
    items = db.get_user_subscriptions(update.message.from_user.id)
    if len(items) == 0:
        update.message.reply_text('В списке отслеживания ничего нет.')
        return
    msg = '\n'.join([item.to_string() for item in items])
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def add_entry(update: Update, context: CallbackContext):
    update.message.reply_text('Введите ссылку на объявление')
    return ENTRY_ADD_URL

def add_entry_url(update: Update, context: CallbackContext):
    answer = update.message.text
    if validators.url(answer):
        db.add_subscription(update.message.from_user.id, answer)
        update.message.reply_text('Готово.')
    else:
        update.message.reply_text('Неверная ссылка.')
    return ConversationHandler.END

def remove_entry(update: Update, context: CallbackContext):
    entries = db.get_user_subscriptions(update.message.from_user.id)
    if len(entries) == 0:
        update.message.reply_text('У вас нет отслеживаемых объявлений')
        return ConversationHandler.END
    selections = [f'{entry.title}\n{entry.url}' for entry in entries]
    markup = ReplyKeyboardMarkup([selections,], one_time_keyboard=True)
    update.message.reply_text('Выберите элемент для удаления', reply_markup=markup)
    return ENTRY_REMOVE_CHOICE

def fallback(update: Update, context: CallbackContext):
    return ConversationHandler.END

def remove_selected_entry(update: Update, context: CallbackContext):
    user_id =  update.message.from_user.id
    title, url = update.message.text.split('\n')
    db.delete_subscription(user_id, url)
    update.message.reply_text(f'{title} больше не отслеживается')
    return ConversationHandler.END

def main():
    dispatcher = updater.dispatcher

    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states = {
            AUTH: [MessageHandler(Filters.text, auth_enter)],
        },
        fallbacks=[MessageHandler(Filters.text, fallback)]
    )


    add_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_entry)],
        states = {
            ENTRY_ADD_URL: [MessageHandler(Filters.text, add_entry_url)],
        },
        fallbacks=[MessageHandler(Filters.text,fallback)]
    )

    remove_handler = ConversationHandler(
        entry_points=[CommandHandler('remove', remove_entry)],
        states = {
            ENTRY_REMOVE_CHOICE: [MessageHandler(Filters.text, remove_selected_entry)],
        },
        fallbacks=[MessageHandler(Filters.text, fallback)]
    )

    dispatcher.add_handler(auth_handler)
    dispatcher.add_handler(CommandHandler('list', list_entries))
    dispatcher.add_handler(add_handler)
    dispatcher.add_handler(remove_handler)

    try:
        updater.start_polling()
        updater.idle()

    except KeyboardInterrupt:
        print('Shutting down')
    
    finally:
        db.close()
        print('Closed DB')

    

if __name__ == '__main__':
    main()
