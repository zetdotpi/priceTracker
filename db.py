import sqlite3
from typing import List
from entities import Entry


_CREATE_TABLES_STMT = '''
    CREATE TABLE IF NOT EXISTS observables (
        title TEXT,
        url TEXT PRIMARY KEY,
        price DECIMAL(10,2),
        last_check_dt DATETIME
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER,
        observable_url TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (observable_url) REFERENCES observables(url)
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY
    );
'''

_GET_ENTRIES_STMT = '''
    SELECT title, url, price, last_check_dt 
    FROM observables;
'''

_INSERT_ENTRY_STMT = '''
    INSERT INTO observables(title, url, price, last_check_dt)
    VALUES (NULL, ?, NULL, NULL);
'''

_UPDATE_ENTRY_STMT = '''
    UPDATE observables
    SET
        price = ?,
        last_check_dt = ?
    WHERE
        url = ?
'''

_DELETE_ENTRY_STMT = '''
    DELETE FROM observables
    WHERE url = ?;
'''

_INSERT_USER_STMT = '''
    INSERT INTO users(id)
    VALUES (?);
'''

_DELETE_USER_STMT = '''
    DELETE FROM users
    WHERE id = ?;
'''

_INSERT_SUBSCRIPTION_STMT = '''
    INSERT INTO subscriptions(user_id, observable_url)
    VALUES (?, ?);
'''

_DELETE_SUBSCRIPTION_STMT = '''
    DELETE FROM subscriptions
    WHERE user_id = ? AND observable_url = ?;
'''

_GET_USER_SUBSCRIPTIONS_STMT = '''
    SELECT title, url, price, last_check_dt
    FROM observables
    WHERE url IN (
        SELECT url 
        FROM subscriptions
        WHERE user_id = ?
    );
'''


class  PriceTrackerDB:
    def _create_tables(self):
        self.cur.executescript(_CREATE_TABLES_STMT)
        self.conn.commit()
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.conn.cursor()
        self._create_tables()
    
    def add_user_id(self, id: int):
        self.cur.execute(_INSERT_USER_STMT, (id,))
        self.conn.commit()

    def user_id_exists(self, id: int) -> bool:
        c = self.cur.execute("SELECT COUNT() FROM users WHERE id = ?", (id, )).fetchone()[0]
        self.conn.commit()
        return c > 0    #if one or more matching IDs found -> true, else -> false

    def delete_user_id(self, id: int):
        self.cur.execute(_DELETE_USER_STMT, (id,))
        self.conn.commit()

    def add_subscription(self, user_id: int, url: str):
        self.add_entry(url)
        c = self.cur.execute("SELECT COUNT() FROM OBSERVABLES WHERE url = ?", (url, )).fetchone()[0]
        if c == 0:
            self.add_entry(url)
        self.cur.execute(_INSERT_SUBSCRIPTION_STMT, (user_id, url))
        self.conn.commit()

    def delete_subscription(self, user_id: int, url: str):
        self.cur.execute(_DELETE_SUBSCRIPTION_STMT, (user_id, url))
        self.conn.commit()
        c = self.cur.execute("SELECT COUNT() FROM subscriptions WHERE observable_url = ?", (url,)).fetchone()[0]
        if c == 0:
            self.delete_entry(url)

    def get_entries(self) -> List[Entry]:
        data = self.cur.execute(_GET_ENTRIES_STMT).fetchall()
        entries = [Entry.from_tuple(item) for item in data]
        return entries

    def add_entry(self, url: str) -> Entry:
        self.cur.execute(_INSERT_ENTRY_STMT, (url,))
        self.conn.commit()
        return Entry(url, None, None, True)

    def update_entry(self, entry: Entry):
        self.cur.execute(_UPDATE_ENTRY_STMT, entry.to_tuple())
        self.conn.commit()

    def delete_entry(self, url: str):
        self.cur.execute(_DELETE_ENTRY_STMT, (url,))
        self.conn.commit()

    def get_user_subscriptions(self, user_id: int) -> List[Entry]:
        data = self.cur.execute(_GET_USER_SUBSCRIPTIONS_STMT, (user_id,)).fetchall()
        entries = [Entry.from_tuple(item) for item in data]
        return entries

    def close(self):
        self.conn.close()
