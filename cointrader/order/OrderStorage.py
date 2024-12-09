import sqlite3
from datetime import datetime
from cointrader.order.Order import Order

class OrderStorage:
    def __init__(self, db_path='orders.db'):
        self.db_path = db_path
        self._create_table()
        self._fields = [
            'id', 'symbol', 'type', 'limit_type', 'side', 'price', 'limit_price', 'stop_price', 'stop_direction', 'size',
            'filled_size', 'fee', 'placed_ts', 'filled_ts', 'msg', 'post_only', 'status', 'error_reason', 'error_msg'
        ]

    def reset(self):
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    type TEXT NOT NULL,
                    limit_type TEXT,
                    side TEXT NOT NULL,
                    price REAL,
                    limit_price REAL,
                    stop_price REAL,
                    stop_direction TEXT,
                    size REAL NOT NULL,
                    filled_size REAL,
                    fee REAL,
                    placed_ts INTEGER,
                    filled_ts INTEGER,
                    msg TEXT NOT NULL,
                    post_only INTEGER,
                    status TEXT NOT NULL,
                    error_reason TEXT NOT NULL,
                    error_msg TEXT NOT NULL
                    )
            ''')
            conn.commit()

    def table_exists(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            return cursor.fetchone() is not None

    def add_order(self, order: Order):
        with sqlite3.connect(self.db_path) as conn:
            field_str = ', '.join(self._fields)
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO orders ({field_str}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (order.id, order.symbol, order.type.name, order.limit_type.name, order.side.name, order.price, order.limit_price,
                  order.stop_price, order.stop_direction.name, order.size, order.filled_size, order.fee, order.placed_ts,
                  order.filled_ts, order.msg, int(order.post_only), order.status.name, order.error_reason.name, str(order.error_msg)))
            conn.commit()

    def get_order(self, order_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
            return cursor.fetchone()
    
    def get_all_orders(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders')
            return cursor.fetchall()

    def update_order_status(self, order_id, status):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
            conn.commit()

    def delete_order(self, order_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id))
            conn.commit()
