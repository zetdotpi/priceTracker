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

from .config import BOT_API_KEY, DB_PATH


db = sqlite3.connect(DB_PATH)


def start():
    return ConversationHandler.

def main():
    updater = Updater(BOT_API_KEY)

    dispatcher = updater.dispatcher

    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

    )

    dispatcher.add_handler(auth_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
