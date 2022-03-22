import sqlite3
from typing import List
from entities import Entry


_CREATE_TABLES_STMT = '''
    CREATE TABLE IF NOT EXISTS observables (
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
    SELECT url, price, last_check_dt 
    FROM observables;
'''

_INSERT_ENTRY_STMT = '''
    INSERT INTO observables(url, price, last_check_dt)
    VALUES (?, NULL, NULL);
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
    INSERT INTO subscriptions(user_id, subscription_url)
    VALUES (?, ?);
'''

_DELETE_SUBSCRIPTION_STMT = '''
    DELETE FROM subscriptions
    WHERE user_id = ? AND observable_url = ?;


'''

class  PriceTrackerDB:
    def _create_tables(self):
        self.conn.executescript(_CREATE_TABLES_STMT)
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def add_user_id(self, id: int):
        self.conn.execute(_INSERT_USER_STMT, (id,))

    def delete_user_id(self, id: int):
        self.conn.execute(_DELETE_USER_STMT, (id,))

    def add_subscription(self, user_id: int, url: str):
        c = self.conn.execute("SELECT COUNT() FROM OBSERVABLES WHERE url = ?", (url, )).fetchone()[0]
        if c == 0:
            self.add_entry(url)
        self.conn.execute(_INSERT_SUBSCRIPTION_STMT, (user_id, url))

    def delete_subscription(self, user_id: int, url: str):
        self.conn.execute(_DELETE_SUBSCRIPTION_STMT, (user_id, url))
        c = self.conn.execute("SELECT COUNT() FROM subscriptions WHERE observable_url = ?", (url,)).fetchone()[0]
        if c == 0:
            self.delete_entry(url)

    def get_entries(self) -> List[Entry]:
        data = self.conn.execute(_GET_ENTRIES_STMT).fetchall()
        entries = [Entry.from_tuple(item) for item in data]
        return entries

    def add_entry(self, url: str) -> Entry:
        self.conn.execute(_INSERT_ENTRY_STMT, (url,))
        return Entry(url, None, None, True)

    def update_entry(self, entry: Entry):
        self.conn.execute(_UPDATE_ENTRY_STMT, entry.to_tuple())

    def delete_entry(self, url: str):
        self.conn.execute(_DELETE_ENTRY_STMT, (url,))
