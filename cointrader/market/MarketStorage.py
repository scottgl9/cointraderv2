import sqlite3
from cointrader.common.Kline import Kline

class MarketStorage:
    def __init__(self, db_path='market_data.db'):
        self.connection = sqlite3.connect(db_path)

    def table_name(self, symbol):
        return symbol.replace('-', '_') + '_klines'

    def table_exists(self, symbol):
        cursor = self.connection.cursor()
        cursor.execute(f'''
            SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name(symbol)}'
        ''')
        return cursor.fetchone() is not None

    def create_table(self, symbol):
        with self.connection:
            self.connection.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name(symbol)} (
                    id INTEGER PRIMARY KEY,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    ts INTEGER NOT NULL
                )
            ''')

    def kline_exists(self, symbol, ts):
        """
        Check if a kline exists in the database
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT 1 FROM {self.table_name(symbol)} WHERE ts = ?', (ts,))
        return cursor.fetchone() is not None

    def store_kline(self, symbol, kline: Kline):
        """
        Store a kline in the database
        """
        self.create_table(symbol)
        with self.connection:
            self.connection.execute(f'''
                INSERT INTO {self.table_name(symbol)} (open, high, low, close, volume, ts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (kline.open, kline.high, kline.low, kline.close, kline.volume, kline.ts))

    def store_kline(self, symbol, open, high, low, close, volume, ts):
        """
        Store a kline in the database
        """
        self.create_table(symbol)
        with self.connection:
            self.connection.execute(f'''
                INSERT INTO {self.table_name(symbol)} (open, high, low, close, volume, ts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (open, high, low, close, volume, ts))

    def get_kline(self, symbol, ts):
        """
        Get a kline from the database
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name(symbol)} WHERE ts = ?', (ts,))
        return cursor.fetchone()

    def get_klines(self, symbol):
        """
        Get all klines for a symbol from the database with the given symbol
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name(symbol)}')
        return cursor.fetchall()
    
    def get_klines_range(self, symbol, start_ts, end_ts):
        """
        Get all klines for a symbol from the database in the specified range with the given symbol
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name(symbol)} WHERE ts >= ? AND ts <= ?', (start_ts, end_ts))
        return cursor.fetchall()

    def close(self):
        self.connection.close()
