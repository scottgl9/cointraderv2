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


def get_klines(market: Market, symbol: str, start_time: int, end_time: int, granularity: int) -> list:
    max_klines = market.market_get_max_kline_count(granularity)
    minutes = 0
    hours = 0
    if granularity == 60:
        minutes = max_klines
    elif granularity == 300: # 5 minutes
        minutes = max_klines * 5
    elif granularity == 900: # 15 minutes
        minutes = max_klines * 15
    elif granularity == 3600: # 1 hour
        hours = max_klines

    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())
    klines = market.market_get_klines_range(symbol, start, end, granularity)
    return klines

def main(args):
    name = args.exchange
    initial_usd = args.initial_usd

    exchange = TraderSelectExchange(name).get_exchange()

    market = Market(exchange=exchange)
    account = AccountSimulate(exchange=exchange, market=market)
    account.load_symbol_info()

    all_klines = {}

    account.update_asset_balance("USD", available=initial_usd, hold=0.0)

    ex = TraderExecuteSimulate(exchange=exchange, account=account)

    print(account.get_account_balances())
    print("Start Total USD Balance:")
    print(account.get_total_balance("USD"))

    tconfig = TraderConfig(path=f'{name}_trader_config.json')
    if not tconfig.load_config():
        tconfig.save_config()

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig)

    running = True

    symbol = 'SOL-USD'

    klines = get_klines(market, symbol, 0, 0, args.granularity)

    kline = Kline()
    kline.set_dict_names(ts='start')

    for k in klines:
        #print(k)
        kline.from_dict(k)
        kline.symbol = symbol
        mtrader.market_update(kline)

    print(account.get_account_balances())
    print("Final Total USD Balance:")
    print(account.get_total_balance("USD"))

    #while running:


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trade simulation with past klines.')
    parser.add_argument('--initial_usd', type=float, default=10000.0, help='Initial USD amount for simulation')
    parser.add_argument('--exchange', type=str, default="cbadv", help='Account to use for simulation')
    parser.add_argument('--granularity', type=int, default=300, help='Granularity of klines')
    parser.add_argument('--symbols', type=str, default='BTC-USD', help='Symbol to use for simulation')
    args = parser.parse_args()
    main(args)
