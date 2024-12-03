#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
#from coinbase.rest import RESTExchange

import json
import sys
import time

try:
    import cointrader
except ImportError:
    sys.path.append('.')

import pandas as pd

from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.account.Account import Account
from cointrader.market.Market import Market
from cointrader.execute.TradeExecute import TraderExecute
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline
from cointrader.config import *

class CBADVLive:
    def __init__(self, mtrader: MultiTrader, tconfig: TraderConfig):
        self.prev_klines = {}
        self.mtrader = mtrader
        self.tconfig = tconfig

    def on_message(self, msg):
        kline = Kline()
        kline.set_dict_names(ts='start', symbol='product_id')
        ws_object = WebsocketResponse(json.loads(msg))
        if ws_object.channel == "candles":
            for event in ws_object.events:
                for candle in event.candles:
                    kline.from_dict(dict(candle.__dict__))
                    if kline.symbol not in self.prev_klines:
                        self.prev_klines[kline.symbol] = kline
                    else:
                        prev_kline = self.prev_klines[kline.symbol]
                        if kline.ts == prev_kline.ts:
                            continue
                        self.prev_klines[kline.symbol] = kline
                    pd.to_datetime(kline.ts, unit='s')
                    print(f"{pd.to_datetime(kline.ts, unit='s')} {kline.symbol} Low: {kline.low}, High: {kline.high}, Open: {kline.open}, Close: {kline.close} Volume: {kline.volume}")

def main(name):
    exchange = TraderSelectExchange(name).get_exchange()

    market = Market(exchange=exchange)
    account = Account(exchange=exchange, market=market)
    account.load_symbol_info()

    print(f'Account name: {account.name()}')
    if not account.load_symbol_info():
        print("Failed to load symbol info")
        return
    print(account.get_account_balances())
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))

    tconfig = TraderConfig(path=f'{name}_trader_config.json')
    tconfig.save_config()

    ex = TraderExecute(exchange=exchange, account=account)

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig)
    rt = CBADVLive(mtrader=mtrader, tconfig=tconfig)
    ws_client = WSClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
    #accnt = AccountCoinbaseAdvanced(exchange=exchange, simulate=False, live=False, logger=logger)

    running = True

    product_ids = ["BTC-USD", "SOL-USD", "ETH-USD"]
    ws_client.open()
    ws_client.subscribe(product_ids=product_ids, channels=['candles']) #, 'matches'])

    while running:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            ws_client.unsubscribe(product_ids=product_ids, channels=['candles'])#, 'matches'])
            ws_client.close()
            running = False
            print("Exiting...")

if __name__ == '__main__':
    main("cbadv")
