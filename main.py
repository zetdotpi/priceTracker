import time
from datetime import datetime
from multiprocessing import Pool
import requests
import bs4

from telegram import bot, ParseMode
from config import BOT_API_KEY, DB_PATH

from entities import Entry, ComparisonPair
from db import PriceTrackerDB


def pull_entry_data(entry: Entry) -> ComparisonPair:
    res = requests.get(
        entry.url,
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
    )
    print(res.status_code, res.reason)
    if not res.ok:
        print(f'Something is not OK with request to this url-> {entry.url}')
        return ComparisonPair(entry, entry)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    title_tag = soup.find('span', {'class': 'title-info-title-text'})
    title = title_tag.get_text()
    
    price_tag = soup.find('span', {'class': 'js-item-price'})
    price = float(price_tag['content']) or None
    
    new = Entry(title, entry.url, price, datetime.now())
    return ComparisonPair(entry, new)    

db = PriceTrackerDB(DB_PATH)

tbot = bot.Bot(BOT_API_KEY)

def notify_price_change(pair: ComparisonPair):
    print(f'Notify about price change for {pair}')
    subs = db.get_subscribers_by_url(pair.new.url)
    for sub in subs:
        tbot.send_message(
            chat_id = sub,
            text = pair.price_changed_message()
        )

def refresh_active_entries():
    entries = db.get_entries()
    print(f'{len(entries)} entries scheduled for update')
    
    pairs = map(pull_entry_data, entries)
    
    for pair in pairs:
        if pair.old.price != pair.new.price:
            print(f'Entry {pair.new.url} price changed: \
                {pair.old.price} -> {pair.new.price}')
            db.update_entry(pair.new)
            notify_price_change(pair)


def main():
    refresh_active_entries()
    db.close()



if __name__ == '__main__':
    main()
