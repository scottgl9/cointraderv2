#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
#from coinbase.rest import RESTExchange
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

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
from cointrader.market.Market import Market
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.order.Orders import Orders
from cointrader.common.Kline import Kline
from cointrader.config import *
from cointrader.indicators.EMA import EMA
from cointrader.common.KlineEmitter import KlineEmitter

def main(args):
    name = args.exchange
    initial_usdt = args.initial_usdt

    exchange = TraderSelectExchange(name).get_exchange()

    symbols = args.symbols.split(',')

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

    all_klines = {}

    account.update_asset_balance("USDT", available=initial_usdt, hold=0.0)
    tconfig.set_global_current_balance_quote(balance=initial_usdt)

    print(account.get_account_balances())
    print("Start Total USDT Balance:")
    print(account.get_total_balance("USDT"))

    ex = TraderExecuteSimulate(exchange=exchange, account=account, config=tconfig)

    orders = Orders(config=tconfig, db_path=tconfig.orders_db_path(), reset=True)

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig, orders=orders, restore_positions=False, granularity=granularity)

    # update quote balance before trying to open positions
    mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

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

    kline = Kline()
    #kline.set_dict_names(ts='start')

    first_prices = {}
    last_prices = {}

    kline_emitters: dict[str, KlineEmitter] = {}

    # emitter takes in hourly klines, and emits daily klines
    for symbol in symbols:
        kline_emitters[symbol] = KlineEmitter(src_granularity=granularity, dst_granularity=86400)

    #kline_emitter = KlineEmitter(src_granularity=granularity, dst_granularity=86400)

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
                    mtrader.market_update_kline_other_timeframe(symbol=symbol, kline=kline_daily, granularity=kline_emitter.granularity())

            mtrader.market_update_kline(symbol=symbol, kline=kline, granularity=granularity)

            # update quote balance before trying to open positions
            mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

            mtrader.market_update_price(symbol=symbol, current_price=kline.close, current_ts=kline.ts, granularity=granularity)
            last_prices[symbol] = kline_data['close']

    orders.commit()

    print(orders.get_active_orders(symbol=None))

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

    total_positive_profit = 0

    print("\npositive profit on closed positions:")
    for symbol in symbols:
        profit = mtrader.positive_profit_percent(symbol)
        total_positive_profit += profit
        print(f"{symbol} positive profit: {profit:.2f}%")

    total_negative_profit = 0

    print("\nnegative profit on closed positions:")
    for symbol in symbols:
        profit = mtrader.negative_profit_percent(symbol)
        total_negative_profit += profit
        print(f"{symbol} negative profit: {profit:.2f}%")

    print(f"\nTotal positive profit: {total_positive_profit:.2f}%")
    print(f"Total negative profit: {total_negative_profit:.2f}%")
    print(f"Total net profit: {total_positive_profit + total_negative_profit:.2f}%")

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
