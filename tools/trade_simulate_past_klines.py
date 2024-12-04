#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
#from coinbase.rest import RESTExchange
from datetime import datetime, timedelta

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
from cointrader.common.Kline import Kline
from cointrader.config import *


def main(args):
    name = args.exchange
    initial_usd = args.initial_usd

    exchange = TraderSelectExchange(name).get_exchange()

    market = Market(exchange=exchange, db_path=args.db_path)
    account = AccountSimulate(exchange=exchange, market=market)
    account.load_symbol_info()
    account.load_asset_info()

    all_klines = {}
    symbols = args.symbols.split(',')

    account.update_asset_balance("USD", available=initial_usd, hold=0.0)

    ex = TraderExecuteSimulate(exchange=exchange, account=account)

    print(account.get_account_balances())
    print("Start Total USD Balance:")
    print(account.get_total_balance("USD"))

    tconfig = TraderConfig(path=f'{name}_trader_config.json')
    if not tconfig.load_config():
        tconfig.save_config()

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig)

    start_ts = int(datetime.fromisoformat(args.start_date).timestamp())
    if args.end_date == 'now':
        end_ts = int(datetime.now().timestamp())
    else:
        end_ts = int(datetime.fromisoformat(args.end_date).timestamp())

    kline_count = 0

    for symbol in symbols:
        all_klines[symbol] = market.market_get_klines_range(symbol, start_ts=start_ts, end_ts=end_ts, granularity=args.granularity, store_db=True)
        kline_count = len(all_klines[symbol])

    kline = Kline()
    #kline.set_dict_names(ts='start')

    for i in range(kline_count):
        for symbol in symbols:
            k = all_klines[symbol][i]
            #print(k)
            kline.from_dict(k)
            kline.symbol = symbol
            mtrader.market_update(kline)

    print(account.get_account_balances())
    print("Final Total USD Balance:")
    print(account.get_total_balance("USD"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trade simulation with past klines.')
    parser.add_argument('--initial_usd', type=float, default=10000.0, help='Initial USD amount for simulation')
    parser.add_argument('--exchange', type=str, default="cbadv", help='Account to use for simulation')
    parser.add_argument('--granularity', type=int, default=300, help='Granularity of klines')
    parser.add_argument('--db_path', type=str, default='market_data.db', help='Path to the database file')
    parser.add_argument('--symbols', type=str, default='BTC-USD,ETH-USD,SOL-USD', help='Comma separated list of symbols')
    parser.add_argument('--start_date', type=str, default='2024-12-02', help='Start date for klines')
    parser.add_argument('--end_date', type=str, default='now', help='End date for klines')
    args = parser.parse_args()
    main(args)
