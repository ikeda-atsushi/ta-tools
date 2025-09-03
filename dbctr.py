import sqlite3
import pandas as pd
import time
from icecream import ic

class DBCtr:

    _instance = None

    def __init__(self, db_path='stock.db'):
        if DBCtr._instance is not None:
            raise Exception("This class is a singleton!")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # オプション：dict風に使える
        DBCtr._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DBCtr()
        return cls._instance

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
        DBCtr._instance = None


class SqlCom:


    def __init__(self):
        self.db = DBCtr.get_instance()

    def getSymbolId(self, symbol):
        cur = self.db.get_cursor()
        cur.execute("SELECT id FROM symbols WHERE symbol=?;", (symbol,))
        result = cur.fetchone()
        return result['id'] if result else None


    # Create tables
    def createTables(self):
        
        cur = self.db.get_cursor()
        try:
            cur.executescript("""
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    security_name TEXT,
    company TEXT
);

CREATE TABLE IF NOT EXISTS watch_list (
    id INTEGER PRIMARY KEY,
    group TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER NOT NULL,
    Date TEXT NOT NULL,
    Open REAL,
    High REAL,
    Low REAL,
    Close REAL,
    Volume INTEGER,
    PRIMARY KEY (id, Date),
    FOREIGN KEY (id) REFERENCES symbols(id)
);

CREATE TABLE IF NOT EXISTS moving_average (
   id INTEGER NOT NULL,
   ms5 REAL,
   ma25 REAL,
   PRIMARY KEY (id),
   FOREIGN KEY (id) REFERENCES history(id)
);
""")
            
            self.db.commit()
            
        except sqlite3.Error as e:
            print(e)
            print("Execute SQL error {e}")
            
        return

    # INSERT
    def insertHistory(self, symbol,  df):
        
        cur = self.db.get_cursor()

        try:
            # get id from symbosls table
            cur.execute("SELECT id FROM symbols WHERE symbol=?", (symbol,))
            result = cur.fetchone()

            if result is None:
                raise ValueError(f"symbol '{symbol}' not exist in symbols")

            symbol_id = result[0]

            # insert in history table
            for index, row in df.iterrows(): 

               #ic(symbol_id, row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5])
                
               cur.execute("""
INSERT OR REPLACE INTO history (
id, Date, Open, High, Low, Close, Volume
) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (symbol_id, row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5]))

               self.db.commit()

        except ValueError as ve:
            print('Value error: {ve}')
            return False
        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")
            self.conn.rollback()  
            return False
        except sqlite3.OperationalError as e:
            print(f"OperationalError: {e}")
            return False
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            if self.conn:
                self.conn.rollback()
            return False
        except sqlite3.Error as e:
            print(f"DB error ***: {e}")
            cur.execute('ROLLBACK')
            return False
            
        return True


    def readCach(self, symbol):

        history = None
        cur = self.db.get_cursor()

        try:
            # get idmain in symbol
            cur.execute("SELECT id FROM symbols WHERE symbol=?", (symbol,))
            result = cur.fetchone()

            if result is None:
                raise ValueError(f"symbol '{symbol}' not found")
            
            cur.execute("SELECT * FROM history WHERE id=?", (result[0],))
            rows = cur.fetchall()

            if len(rows) == 0:
                return rows

            #for row in rows:
            #    ic(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

            rows_list = []
            for row in rows:
                tmp_row = {'Date': row[1], 'Open': row[2], 'High': row[3], 'Low': row[4], 'Close': row[5], 'Volume': row[6]}
                rows_list.append(tmp_row)

            df = pd.DataFrame(rows_list)
            #df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
            #df = df.set_index('Date')
            #df.index = df.index.astype(str)

        except ValueError as ve:
            print(ve)
        except sqlite3.Error as e:
            print(f"DB error1: {e}")
            cur.execute("ROLLBACK")

        return df

    def close(self):
        self.db.close()
        return
