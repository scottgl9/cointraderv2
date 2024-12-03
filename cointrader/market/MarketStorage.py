import sqlite3
from cointrader.common.Kline import Kline

class MarketStorage:
    def __init__(self, db_path='market_data.db'):
        self.connection = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS klines (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    ts INTEGER NOT NULL
                )
            ''')

    def store_kline(self, symbol, kline: Kline):
        with self.connection:
            self.connection.execute('''
                INSERT INTO klines (symbol, open, high, low, close, volume, ts)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, kline.open, kline.high, kline.low, kline.close, kline.volume, kline.ts))

    def store_kline(self, symbol, open, high, low, close, volume, ts):
        with self.connection:
            self.connection.execute('''
                INSERT INTO klines (symbol, open, high, low, close, volume, ts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, open, high, low, close, volume, ts))

    def get_kline(self, symbol, ts):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM klines WHERE symbol = ? AND ts = ?', (symbol, ts))
        return cursor.fetchone()

    def get_klines(self, symbol):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM klines WHERE symbol = ?', (symbol,))
        return cursor.fetchall()
    
    def get_klines_range(self, symbol, start_ts, end_ts):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM klines WHERE symbol = ? AND ts >= ? AND ts <= ?', (symbol, start_ts, end_ts))
        return cursor.fetchall()

    def close(self):
        self.connection.close()
