import sqlite3
from datetime import datetime
from cointrader.order.Order import Order
from cointrader.trade.TraderConfig import TraderConfig

class OrderStorage:
    def __init__(self, config: TraderConfig, db_path='orders.db', reset=True):
        self._config = config
        self.db_path = db_path
        self._reset = reset
        self._fields = [
            'id', 'pid', 'active', 'symbol', 'type', 'limit_type', 'side', 'price', 'limit_price', 'stop_price', 'stop_direction',
            'size', 'filled_size', 'fee', 'placed_ts', 'filled_ts', 'msg', 'post_only', 'status', 'error_reason', 'error_msg'
        ]
        print(f"db_path: {db_path}")
        self._simulate = self._config.simulate()
        # sqlite connections must be created in the same thread as they are used, so for simulations this is fine
        if self._simulate:
            self._conn = sqlite3.connect(self.db_path)
        else:
            self._conn = None
        self.reset()


    def reset(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        if self._reset:
            cursor.execute('DROP TABLE IF EXISTS orders')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                pid INTEGER,
                active INTEGER,
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
        if not self._simulate:
            conn.close()

    def get_connection(self):
        if self._simulate:
            return self._conn
        else:
            print(f"db_path: {self.db_path}")
            return sqlite3.connect(self.db_path)

    def table_exists(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
        return cursor.fetchone() is not None

    def add_order(self, order: Order):
        conn = self.get_connection()
        field_str = ', '.join(self._fields)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO orders ({field_str}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order.id, order.pid, int(order.active), order.symbol, order.type.name, order.limit_type.name, order.side.name, order.price, order.limit_price,
                order.stop_price, order.stop_direction.name, order.size, order.filled_size, order.fee, order.placed_ts,
                order.filled_ts, order.msg, int(order.post_only), order.status.name, order.error_reason.name, str(order.error_msg)))
        
        if not self._config.simulate():
            conn.commit()
            conn.close()

    def exists_order(self, order_id):
        return self.get_order(order_id) is not None

    def get_order(self, order_id: str, symbol: str) -> Order:
        conn = self.get_connection()
        cursor = conn.cursor()
        if symbol is not None:
            cursor.execute('SELECT * FROM orders WHERE id = ? AND symbol = ?', (order_id, symbol))
        else:
            cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        columns = [column[0] for column in cursor.description]
        result = cursor.fetchone()

        if not self._config.simulate():
            conn.close()

        if result is None:
            return None
        return Order(symbol=symbol, data=dict(zip(columns, result)))

    def get_all_orders(self, symbol: str=None) -> list[Order]:
        if not self.table_exists():
            return []
        conn = self.get_connection()
        cursor = conn.cursor()
        if symbol is None:
            cursor.execute('SELECT * FROM orders')
        else:
            cursor.execute('SELECT * FROM orders WHERE symbol = ?', (symbol,))
        columns = [column[0] for column in cursor.description]
        result = cursor.fetchall()

        if not self._config.simulate():
            conn.close()

        if result is None:
            return None
        return [Order(symbol=symbol, data=dict(zip(columns, row))) for row in result]
    
    def get_active_orders(self, symbol: str=None) -> list[Order]:
        conn = self.get_connection()
        cursor = conn.cursor()
        if symbol is None:
            cursor.execute('SELECT * FROM orders WHERE active = 1')
        else:
            cursor.execute('SELECT * FROM orders WHERE symbol = ? AND active = 1', (symbol,))
        columns = [column[0] for column in cursor.description]
        result = cursor.fetchall()

        if not self._config.simulate():
            conn.close()

        if result is None:
            return None
        
        return [Order(symbol=symbol, data=dict(zip(columns, row))) for row in result]

    def update_order(self, order: Order):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET pid = ?, active = ?, symbol = ?, type = ?, limit_type = ?, side = ?, price = ?, limit_price = ?, stop_price = ?, stop_direction = ?, size = ?, filled_size = ?, fee = ?, placed_ts = ?, filled_ts = ?, msg = ?, post_only = ?, status = ?, error_reason = ?, error_msg = ? WHERE id = ?',
            (order.pid, int(order.active), order.symbol, order.type.name, order.limit_type.name, order.side.name, order.price, order.limit_price, order.stop_price, order.stop_direction.name, order.size, order.filled_size, order.fee, order.placed_ts, order.filled_ts, order.msg, int(order.post_only), order.status.name, order.error_reason.name, str(order.error_msg), order.id))
        if not self._config.simulate():
            self._conn.commit()

    def update_order_status(self, order_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        if not self._config.simulate():
            conn.commit()
            conn.close()

    def update_order_active(self, order_id: str, active: bool):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET active = ? WHERE id = ?', (active, order_id))
        if not self._config.simulate():
            conn.commit()
            conn.close()

    def delete_order(self, order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        if not self._config.simulate():
            conn.commit()
            conn.close()

    def commit(self):
        conn = self.get_connection()
        conn.commit()
        if not self._config.simulate():
            conn.close()
