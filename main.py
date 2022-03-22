from email import header
from sqlite3 import dbapi2
from typing import List
import time
import os
from datetime import datetime
from multiprocessing import Pool
import requests
import bs4

import sqlite3

from pprint import pprint

from entities import Entry, ComparisonPair
from db import PriceTrackerDB


DB_PATH = './pricetracker.db'


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
    price_tag = soup.find('span', {'class': 'js-item-price'})
    price = float(price_tag['content']) or None
    new = Entry(entry.url, price, datetime.now())
    return ComparisonPair(entry, new)    

db = PriceTrackerDB(DB_PATH)


def notify_price_change(pair: ComparisonPair):
    print(f'Notify about price change for {pair}')

def refresh_active_entries():
    entries = db.get_entries()
    
    with Pool() as pool:
        pairs = pool.map(pull_entry_data, entries)
    
    for pair in pairs:
        if pair.old.price != pair.new.price:
            print(f'Entry {pair.new.url} price changed: \
                {pair.old.price} -> {pair.new.price}')
            db.update_entry(pair.new)
            notify_price_change(pair)


def main():
    sleep_time = 60
    try:
        while True:
            refresh_active_entries()
            print(80*'=')
            print(f'Sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)
    except KeyboardInterrupt as e:
        print(f'Caught keyboard interrupt')

    db.close()



if __name__ == '__main__':
    main()
