#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
#from coinbase.rest import RESTExchange
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from threading import Thread

import json
import sys
import time
import argparse

try:
    import cointrader
except ImportError:
    sys.path.append('.')

import pandas as pd

from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.account.AccountSimulate import AccountSimulate
from cointrader.execute.TradeExecuteSimulate import TraderExecuteSimulate
from cointrader.execute.pipeline.ExecutePipeline import ExecutePipeline
from cointrader.market.Market import Market
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.order.Orders import Orders
from cointrader.common.Kline import Kline
from cointrader.common.LogLevel import LogLevel
from cointrader.config import *
from cointrader.indicators.EMA import EMA
from cointrader.common.KlineEmitter import KlineEmitter

class PipelineExecutionThread(Thread):
    def __init__(self, exec_pipe: ExecutePipeline):
        Thread.__init__(self)
        self._exec_pipe = exec_pipe

    def run(self):
        while True:
            self._exec_pipe.process_order_requests()
            time.sleep(1 / 1000) # sleep for 1ms

def run_trader(tconfig: TraderConfig, account: AccountSimulate, exchange: str, symbols: list[str], df: pd.DataFrame, granularity: int, initial_usdt: float):
    account.update_asset_balance("USDT", available=initial_usdt, hold=0.0)
    tconfig.set_global_current_balance_quote(balance=initial_usdt)

    if tconfig.log_level() >= LogLevel.INFO.value:
        print(account.get_account_balances())
        print("Start Total USDT Balance:")
        print(account.get_total_balance("USDT"))

    ex = TraderExecuteSimulate(exchange=exchange, account=account, config=tconfig)

    exec_pipe_threaded = False
    ep = ExecutePipeline(execute=ex, max_orders=100, threaded=exec_pipe_threaded)

    orders = Orders(config=tconfig, db_path=tconfig.orders_db_path(), reset=True)

    indicators = [
        'macd', 'sama', 'zlema', 'rsi', 'stochastic', 'ema', 'sma', 'supertrend', 
        'adx', 'squeeze', 'psar', 'vwap', 'ppo', 'cmf', 'cci', 'ao', 
        'uo', 'dpo', 'ichimoku', 'vo', 'kvo', 'eom', 'kst'
    ]

    #weights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0.5, 0.5, 1.0] # net profit: 54121.47% positive profit: 63561.37% negative profit: -9439.90%
    
    # SignalStrength2 weights:
    # net profit: 49769.38% positive profit: 55522.45% negative profit: -5753.07%
    # supertrend=0.8, kst=1.0

    # net profit: 63928.43% positive profit: 69548.39% negative profit: -5619.96%
    # ichimoku=0.5, vo=0.5, eom=0.5, kst=0.5
    weights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0, 0.5, 0.5]
    
    strategy_weights = None #dict(zip(indicators, weights))

    mtrader = MultiTrader(account=account, exec_pipe=ep, config=tconfig, orders=orders, restore_positions=False, granularity=granularity, strategy_weights=strategy_weights)

    # update quote balance before trying to open positions
    mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

    kline = Kline()
    #kline.set_dict_names(ts='start')

    first_prices = {}
    last_prices = {}

    kline_emitters: dict[str, KlineEmitter] = {}

    # emitter takes in hourly klines, and emits daily klines
    for symbol in symbols:
        kline_emitters[symbol] = KlineEmitter(src_granularity=granularity, dst_granularity=86400)

    #kline_emitter = KlineEmitter(src_granularity=granularity, dst_granularity=86400)

    # create thread
    if exec_pipe_threaded:
        exec_pipe_thread = PipelineExecutionThread(exec_pipe=ep)
        exec_pipe_thread.daemon = True
        exec_pipe_thread.start()

    # iterate through all rows in the DataFrame
    for index, row in df.iterrows():
        symbol = row['Symbol']
        if symbol in symbols:
            kline_data = {
                'ts': row['Timestamp'],
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume USDT']
            }

            if symbol not in first_prices:
                first_prices[symbol] = kline_data['close']

            #print(kline_data)
            kline.from_dict(kline_data)
            kline.symbol = symbol
            kline.granularity = granularity

            # emit daily klines
            kline_emitter = kline_emitters[symbol]
            kline_emitter.update(kline)
            if kline_emitter.ready():
                kline_daily = kline_emitter.emit()
                if kline:
                    kline_daily.symbol = symbol
                    kline_daily.granularity = kline_emitter.granularity()
                    #mtrader.market_update(symbol=symbol, kline=kline, current_price=kline.close, current_ts=kline.ts, granularity=kline_emitter.granularity())
                    mtrader.market_update_kline_other_timeframe(symbol=symbol, kline=kline_daily, granularity=kline_emitter.granularity(), preload=False)

            mtrader.market_update_kline(symbol=symbol, kline=kline, granularity=granularity)

            # update quote balance before trying to open positions
            mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

            mtrader.market_update_price(symbol=symbol, current_price=kline.close, current_ts=kline.ts, granularity=granularity)
            last_prices[symbol] = kline_data['close']

    orders.commit()
    if tconfig.log_level() >= LogLevel.INFO.value:
        print(orders.get_active_orders(symbol=None))
    
    return mtrader, first_prices, last_prices


def main(args):
    name = args.exchange
    initial_usdt = args.initial_usdt

    exchange = TraderSelectExchange(name).get_exchange()

    symbols = args.symbols.split(',')

    start_ts = int(datetime.fromisoformat(args.start_date).timestamp())
    if args.end_date == 'now':
        end_ts = int(datetime.now().timestamp())
    else:
        end_ts = int(datetime.fromisoformat(args.end_date).timestamp())

    df = pd.read_csv(args.csv_path)

    # print all unique strings from the Symbols column
    unique_symbols = df['Symbol'].unique()
    print("Symbols:", unique_symbols)

    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='mixed') #'%Y-%m-%d %H:%M:%S')
    # Convert the Date column to unix timestamp
    df['Timestamp'] = df['Date'].apply(lambda x: int(x.timestamp()))
    # Sort the DataFrame by the Date column
    df = df.sort_values(by='Date').reset_index(drop=True)
    # Convert all symbols ending with 'USDT' to '-USDT'
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace('USDT', '-USDT'))
    # Display the first few rows of the DataFrame
    print(df.head())

    # Filter the DataFrame by the Timestamp column
    df = df[(df['Timestamp'] >= start_ts) & (df['Timestamp'] <= end_ts)]


    tconfig = TraderConfig(path=f'config/{name}_trader_simulate_csv_config.json')
    if not tconfig.load_config():
        print(f"Failed to load config {tconfig.get_config_path()}")
        tconfig.save_config()
    else:
        print(f"Loaded config {tconfig.get_config_path()}")

    tconfig.set_trade_symbols(symbols)

    if args.strategy and tconfig.strategy() != args.strategy:
        tconfig.set_strategy(args.strategy)

    print(f"Using strategy: {tconfig.strategy()} db_path: {tconfig.orders_db_path()}")

    granularity = tconfig.granularity()

    market = Market(exchange=exchange, db_path=tconfig.market_db_path())
    account = AccountSimulate(exchange=exchange, market=market)
    account.load_symbol_info()
    account.load_asset_info()

    mtrader, first_prices, last_prices = run_trader(tconfig, account, exchange, symbols, df, granularity, initial_usdt)

    #if exec_pipe_threaded:
    #    exec_pipe_thread.join(timeout=5)

    if tconfig.log_level() >= LogLevel.INFO.value:
        # calculate what the profit would be if we just bought and held
        total_hold_profit = 0
        for symbol in symbols:
            profit = (last_prices[symbol] - first_prices[symbol]) / first_prices[symbol] * 100
            total_hold_profit += profit
            print(f"{symbol} buy and hold profit: {profit:.2f}%")

        print(f"\nTotal buy and hold profit: {total_hold_profit:.2f}%")

        print(account.get_account_balances())
        print("\nFinal Total USDT Balance:")
        print(account.get_total_balance("USDT", prices=last_prices))

        print("\nRemaining open positions:")
        for symbol in symbols:
            position = mtrader.position_count(symbol)
            print(f"{symbol} position_count: {position}")

        print("\nNet profit on closed positions:")
        for symbol in symbols:
            profit = mtrader.net_profit_percent(symbol)
            print(f"{symbol} net profit: {profit:.2f}%")

    total_average_profit = 0
    total_positive_profit = 0
    total_positive_count = 0

    if tconfig.log_level() >= LogLevel.INFO.value:
        print("\npositive profit on closed positions:")
    for symbol in symbols:
        profit = mtrader.positive_profit_percent(symbol)
        total_positive_profit += profit
        positive_count = mtrader.positive_profit_closed_position_count(symbol)
        total_positive_count += positive_count
        total_average_profit += mtrader.positive_average_profit_percent(symbol)
        if tconfig.log_level() >= LogLevel.INFO.value:
            print(f"{symbol} positive profit: {profit:.2f}% average profit: {mtrader.positive_average_profit_percent(symbol):.2f} count: {positive_count}")

    total_negative_profit = 0
    total_negative_count = 0

    if tconfig.log_level() >= LogLevel.INFO.value:
        print("\nnegative profit on closed positions:")
    for symbol in symbols:
        profit = mtrader.negative_profit_percent(symbol)
        total_negative_profit += profit
        negative_count = mtrader.negative_profit_closed_position_count(symbol)
        total_negative_count += negative_count
        total_average_profit += mtrader.negative_average_profit_percent(symbol)
        if tconfig.log_level() >= LogLevel.INFO.value:
            print(f"{symbol} negative profit: {profit:.2f}% average profit: {mtrader.negative_average_profit_percent(symbol):.2f} count: {negative_count}")

    total_average_profit /= (len(symbols) * 2)

    print(f"\nTotal positive profit: {total_positive_profit:.2f}%")
    print(f"Total negative profit: {total_negative_profit:.2f}%")
    print(f"Total net profit: {total_positive_profit + total_negative_profit:.2f}%")
    print(f"Total average profit: {total_average_profit:.2f}%")
    print(f"Total closed positive position count: {total_positive_count}")
    print(f"Total closed negative position count: {total_negative_count}")

    if tconfig.log_level() >= LogLevel.INFO.value:
        buys = {}
        sells = {}

        #print("\nBuys and Sells:")
        for symbol in symbols:
            buys[symbol] = mtrader.buys(symbol)
            print(f"{symbol} buy count: {len(buys[symbol])}")
            #print(f"{symbol} buys: {buys}")
            sells[symbol] = mtrader.sells(symbol)
            #print(f"{symbol} sells: {sells}")
            print(f"{symbol} sell count: {len(sells[symbol])}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trade simulation with past klines.')
    parser.add_argument('--initial_usdt', type=float, default=10000.0, help='Initial USDT amount for simulation')
    parser.add_argument('--exchange', type=str, default="cbadv", help='Account to use for simulation')
    #parser.add_argument('--granularity', type=int, default=3600, help='Granularity of klines')
    parser.add_argument('--csv_path', type=str, default='data/crypto_hourly_data/cryptotoken_full_binance_1h.csv', help='Path to the CSV file')
    parser.add_argument('--symbols', type=str, default='BTC-USDT,ETH-USDT,SOL-USDT,HBAR-USDT,DOT-USDT', help='Comma separated list of symbols')
    parser.add_argument('--strategy', type=str, default='', help='Strategy to use for simulation')
    parser.add_argument('--start_date', type=str, default='2020-08-11 06:00:00', help='Start date for klines')
    parser.add_argument('--end_date', type=str, default='2023-10-19 23:00:00', help='End date for klines')
    args = parser.parse_args()
    main(args)
