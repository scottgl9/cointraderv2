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

def main(args):
    name = args.exchange
    initial_usd = args.initial_usd

    exchange = TraderSelectExchange(name).get_exchange()

    tconfig = TraderConfig(path=f'{name}_trader_config.json')
    if not tconfig.load_config():
        tconfig.save_config()

    if tconfig.strategy() != args.strategy:
        tconfig.set_strategy(args.strategy)

    market = Market(exchange=exchange, db_path=tconfig.market_db_path())
    account = AccountSimulate(exchange=exchange, market=market)
    account.load_symbol_info()
    account.load_asset_info()

    all_klines = {}
    symbols = args.symbols.split(',')

    account.update_asset_balance("USD", available=initial_usd, hold=0.0)

    print(account.get_account_balances())
    print("Start Total USD Balance:")
    print(account.get_total_balance("USD"))

    ex = TraderExecuteSimulate(exchange=exchange, account=account, config=tconfig)

    orders = Orders(db_path=tconfig.orders_db_path(), reset=True)

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig, orders=orders, granularity=args.granularity)

    start_ts = int(datetime.fromisoformat(args.start_date).timestamp())
    if args.end_date == 'now':
        end_ts = int(datetime.now().timestamp())
    else:
        end_ts = int(datetime.fromisoformat(args.end_date).timestamp())

    kline_count = 0

    emas = {}
    ema_values = {}


    # determin which symbol has the fewest klines
    lowest_kline_count = 0

    print(f"Getting klines for {args.start_date} to {args.end_date}")

    # get all klines for each symbol stored in the market db
    for symbol in symbols:
        all_klines[symbol] = market.market_get_stored_klines_range(symbol, start_ts=start_ts, end_ts=end_ts, granularity=args.granularity)
        kline_count = len(all_klines[symbol])
        if lowest_kline_count == 0 or kline_count < lowest_kline_count:
            lowest_kline_count = kline_count
        emas[symbol] = EMA(period=12)
        ema_values[symbol] = []

    print(f"Simulating with {lowest_kline_count} klines")

    kline = Kline()
    #kline.set_dict_names(ts='start')

    for i in range(lowest_kline_count):
        for symbol in symbols:
            k = all_klines[symbol][i]
            #print(k)
            kline.from_dict(k)
            kline.symbol = symbol
            kline.granularity = args.granularity
            mtrader.market_update(kline=kline, current_price=kline.close, current_ts=kline.ts)
            value = emas[symbol].update(kline)
            ema_values[symbol].append(value)

    orders.commit()

    last_prices = {}
    for symbol in symbols:
        last_prices[symbol] = all_klines[symbol][-1]['close']

    print(account.get_account_balances())
    print("\nFinal Total USD Balance:")
    print(account.get_total_balance("USD", prices=last_prices))

    print("\nRemaining open positions:")
    for symbol in symbols:
        position = mtrader.position_count(symbol)
        print(f"{symbol} position_count: {position}")

    print("\nNet profit on closed positions:")
    for symbol in symbols:
        profit = mtrader.net_profit_percent(symbol)
        print(f"{symbol} net profit: {profit:.2f}%")

    buys = {}
    sells = {}

    #print("\nBuys and Sells:")
    for symbol in symbols:
        buys[symbol] = mtrader.buys(symbol)
        #print(f"{symbol} buys: {buys}")
        sells[symbol] = mtrader.sells(symbol)
        #print(f"{symbol} sells: {sells}")

    if args.plot:
        for symbol in symbols:
            klines = all_klines[symbol]
            times = [datetime.fromtimestamp(k['ts']) for k in klines]
            closes = [k['close'] for k in klines]
            buy_times = [datetime.fromtimestamp(buy['ts']) for buy in buys[symbol]]
            buy_prices = [buy['price'] for buy in buys[symbol]]
            sell_times = [datetime.fromtimestamp(sell['ts']) for sell in sells[symbol]]
            sell_prices = [sell['price'] for sell in sells[symbol]]

            plt.figure()
            plt.plot(times, closes, label=symbol)
            #plt.plot(times, ema_values[symbol], label='EMA')
            plt.scatter(buy_times, buy_prices, color='green', marker='^', label='Buys')
            plt.scatter(sell_times, sell_prices, color='red', marker='v', label='Sells')
            plt.title(f"{symbol} Price Over Time")
            plt.xlabel("Time")
            plt.ylabel("Price")
            plt.legend()
            plt.grid(True)
            plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trade simulation with past klines.')
    parser.add_argument('--initial_usd', type=float, default=10000.0, help='Initial USD amount for simulation')
    parser.add_argument('--exchange', type=str, default="cbadv", help='Account to use for simulation')
    parser.add_argument('--granularity', type=int, default=300, help='Granularity of klines')
    parser.add_argument('--symbols', type=str, default='BTC-USD,ETH-USD,SOL-USD', help='Comma separated list of symbols')
    parser.add_argument('--start_date', type=str, default='2024-12-02', help='Start date for klines')
    parser.add_argument('--end_date', type=str, default='now', help='End date for klines')
    parser.add_argument('--plot', action='store_true', help='Plot the results')
    parser.add_argument('--strategy', type=str, default='Default', help='Strategy to use for simulation')
    args = parser.parse_args()
    main(args)
