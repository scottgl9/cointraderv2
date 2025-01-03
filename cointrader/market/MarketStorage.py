import sqlite3
from cointrader.common.Kline import Kline

class MarketStorage:
    def __init__(self, db_path='market_data.db'):
        if db_path:
            self.connection = sqlite3.connect(db_path)
        else:
            self.connection = None
        self._header = "(open, high, low, close, volume, ts)"

    def table_name(self, symbol, granularity):
        if granularity == 60:
            granularity_name = "1m"
        elif granularity == 300: # 5 minutes
            granularity_name = "5m"
        elif granularity == 900: # 15 minutes
            granularity_name = "15m"
        elif granularity == 3600: # 1 hour
            granularity_name = "1h"
        else:
            granularity_name = ''
        return symbol.replace('-', '_') + '_' + granularity_name

    def table_exists(self, symbol, granularity):
        cursor = self.connection.cursor()
        cursor.execute(f'''
            SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name(symbol, granularity)}'
        ''')
        return cursor.fetchone() is not None

    def create_table(self, symbol, granularity):
        with self.connection:
            self.connection.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name(symbol, granularity)} (
                    id INTEGER PRIMARY KEY,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    ts INTEGER NOT NULL
                )
            ''')

    def kline_exists(self, symbol, ts, granularity):
        """
        Check if a kline exists in the database
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT 1 FROM {self.table_name(symbol, granularity)} WHERE ts = ?', (ts,))
        result = cursor.fetchone()
        return result is not None

    def store_kline(self, symbol, kline: Kline, granularity):
        """
        Store a kline in the database
        """
        self.create_table(symbol)
        with self.connection:
            self.connection.execute(f'''
                INSERT INTO {self.table_name(symbol, granularity)} (open, high, low, close, volume, ts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (kline.open, kline.high, kline.low, kline.close, kline.volume, kline.ts))

    def store_kline(self, symbol, open, high, low, close, volume, ts, granularity):
        """
        Store a kline in the database
        """
        self.create_table(symbol, granularity)
        with self.connection:
            self.connection.execute(f'''
                INSERT INTO {self.table_name(symbol, granularity)} (open, high, low, close, volume, ts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (open, high, low, close, volume, ts))

    def get_kline(self, symbol, ts, granularity):
        """
        Get a kline from the database
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name(symbol, granularity)} WHERE ts = ?', (ts,))
        columns = [column[0] for column in cursor.description]
        result = cursor.fetchone()
        return dict(zip(columns, result))

    def get_klines(self, symbol, granularity):
        """
        Get all klines for a symbol from the database with the given symbol
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name(symbol, granularity)}')
        # convert from list of tuples to list of dictionaries
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()
        return [dict(zip(columns, row)) for row in results]
    
    def get_klines_range(self, symbol, start_ts, end_ts, granularity):
        """
        Get all klines for a symbol from the database in the specified range with the given symbol
        """
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name(symbol, granularity)} WHERE ts >= ? AND ts <= ?', (start_ts, end_ts))
        # convert from list of tuples to list of dictionaries
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()
        return [dict(zip(columns, row)) for row in results]

    def close(self):
        self.connection.close()
