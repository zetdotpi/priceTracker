from typing import List
from dataclasses import dataclass
import os
from datetime import datetime
import requests
import bs4
import huey

import sqlite3

@dataclass
class Entry:
    url: str
    price: float
    last_check_dt: datetime
    active: bool

    def to_tuple(self):
        return (self.price, self.last_check_dt.isoformat(), 1 if self.active else 0, self.url)

@dataclass
class ComparisonPair:
    old: Entry
    new: Entry

    def priceDifference(self):
        return self.new.price - self.old.price

DB_PATH = './pricetracker.db'


CREATE_TABLES_STATEMENT = '''
    CREATE TABLE OBSERVABLES (
        URL TEXT PRIMARY KEY,
        PRICE DECIMAL(10,2),
        LAST_CHECK_DT DATETIME,
        ACTIVE BOOLEAN
    );
'''

GET_ALL_ENTRIES_STMT = '''
    SELECT URL, PRICE, LAST_CHECK_DT, ACTIVE 
    FROM OBSERVABLES;
'''

GET_ALL_ACTIVE_ENTRIES_STMT = '''
    SELECT URL, PRICE, LAST_CHECK_DT, ACTIVE
    FROM OBSERVABLES
    WHERE ACTIVE = TRUE;
'''

INSERT_ENTRY_STMT = '''
    INSERT INTO OBSERVABLES(URL, PRICE, LAST_CHECK_DT, ACTIVE)
    VALUES (?, NULL, NULL, TRUE);
'''

UPDATE_ENTRY_STMT = '''
    UPDATE OBSERVABLES
    SET
        PRICE = ?,
        LAST_CHECK_DT = ?,
        ACTIVE = ?
    WHERE
        URL = ?
'''

def list_to_entry(data: list) -> Entry:
    return Entry(data[0], data[1], datetime.fromisoformat(data[2]) if data[2] else None, bool(data[3]))

def create_database(path: str):
    db = sqlite3.connect(DB_PATH)
    db.execute(CREATE_TABLES_STATEMENT)
    return db

def get_active_entries(db: sqlite3.Connection) -> List[Entry]:
    data = db.execute(GET_ALL_ACTIVE_ENTRIES_STMT).fetchall()
    entries = [list_to_entry(item) for item in data]
    return entries

def get_all_entries(db: sqlite3.Connection) -> List[Entry]:
    data = db.execute(GET_ALL_ENTRIES_STMT).fetchall()
    entries = [list_to_entry(item) for item in data]
    return entries

def get_db() -> sqlite3.Connection:
    db = create_database(DB_PATH) if not os.path.exists(DB_PATH) else sqlite3.connect(DB_PATH)
    return db

def add_entry(db: sqlite3.Connection, url: str) -> Entry:
    c = db.cursor()
    c.execute(INSERT_ENTRY_STMT, (url,))
    db.commit()
    return Entry(url, None, None, True)

def update_entry(db: sqlite3.Connection, entry: Entry):
    c = db.cursor()
    c.execute(UPDATE_ENTRY_STMT, entry.to_tuple())
    db.commit()
    c.close()

def pull_entry_data(entry: Entry) -> ComparisonPair:
    res = requests.get(entry.url)
    if not res.ok:
        print(f'Something is not OK with request to this url-> {entry.url}')

    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    price_tag = soup.find('span', {'class': 'js-item-price'})
    price = float(price_tag['content'])
    new = Entry(entry.url, price, datetime.now(), entry.active)
    return ComparisonPair(entry, new)    

def main():    
    sqlite3.enable_callback_tracebacks(True)
    db = get_db()

    print('SELECTING ALL ACTIVE')
    active_entries = get_active_entries(db)
    for entry in active_entries:
        print(entry)
        pair = pull_entry_data(entry)
        print(pair)
        update_entry(db, pair.new)

    db.close()

if __name__ == '__main__':
    main()
