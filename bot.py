import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

from .config import BOT_API_KEY, DB_PATH, ACCESS_PASSWORD
        

AUTH_ENTER, AUTH_ACCEPTED, \
MENU, \
ADD_ENTRY, CHOOSE_ADD_ENTRY, \
REMOVE_ENTRY, CHOOSE_REMOVE_ENTRY, \
SHOW_ENTRY, CHOOSE_SHOW_ENTRY = range(9)

bot_db = BotDB(DB_PATH)

def start(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END

def auth_enter(update: Update) -> int:
    if update.message.text == ACCESS_PASSWORD:
        bot_db.add_user_id(update.chat_member.from_user.id)

def main():
    updater = Updater(BOT_API_KEY)

    dispatcher = updater.dispatcher

    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states = {
            AUTH_ENTER: [
                MessageHandler()
            ]
        }
    )

    dispatcher.add_handler(auth_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
