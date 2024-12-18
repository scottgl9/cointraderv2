#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
#from coinbase.rest import RESTExchange

import json
import sys
import time
from datetime import datetime, timedelta

try:
    import cointrader
except ImportError:
    sys.path.append('.')

import pandas as pd

from collections import deque
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.account.Account import Account
from cointrader.market.Market import Market
from cointrader.execute.TradeExecute import TraderExecute
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline
from cointrader.order.Orders import Orders
from cointrader.config import *
import sys
import select

GRANULARITY = 300

class CBADVLive:
    def __init__(self, mtrader: MultiTrader, market: Market, tconfig: TraderConfig, granularity: int = 300):
        self.prev_kline = {}
        self.mtrader: MultiTrader = mtrader
        self.market = market
        self.tconfig = tconfig
        self.granularity = granularity
        self._last_ts = 0

    def fetch_preload_klines(self, symbol: str, granularity: int):
        klines = []
        max_klines = self.market.market_get_max_kline_count(granularity)

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

        end = datetime.now() - timedelta(seconds=granularity)
        start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
        end = int(end.timestamp())

        candles = self.market.market_get_klines_range(symbol, start, end, granularity)

        for candle in reversed(candles):
            kline = Kline()
            kline.set_dict_names(ts='start')
            kline.from_dict(candle)
            kline.granularity = granularity
            klines.append(kline)
            #self.mtrader.market_preload(symbol, kline)
        return klines

    def on_message(self, msg):
        kline = Kline()
        kline.set_dict_names(ts='start', symbol='product_id')
        ws_object = WebsocketResponse(json.loads(msg))
        #print(f"Channel: {ws_object.channel}")
        if ws_object.channel == "subscriptions":
            print(f"Subscriptions: {ws_object}")
        #elif ws_object.channel == "user":
        #    print(f"User: {ws_object}")
        elif ws_object.channel == "heartbeat":
            print(f"Heartbeat: {ws_object}")
        elif ws_object.channel == "candles":
            for event in ws_object.events:
                for candle in event.candles:
                    kline.from_dict(dict(candle.__dict__))
                    kline.granularity = self.granularity

                    # skip any old klines which may come in when first starting
                    #if abs(int(datetime.now().timestamp()) - kline.ts) > self.granularity * 2:
                    #    continue
                    #print(f"{int(datetime.now().timestamp()) - kline.ts} {kline.symbol}")
                    if kline.symbol not in self.prev_kline:
                        print(f"Pre-loading klines for {kline.symbol}")
                        klines = self.fetch_preload_klines(kline.symbol, self.granularity)
                        self.prev_kline[kline.symbol] = klines[-1]
                        self.mtrader.market_preload(kline.symbol, klines)
                        # if we already fetched the kline, skip it
                        if klines[-1].ts >= kline.ts:
                            self._last_ts = kline[-1].ts
                            continue
                        else:
                            self.prev_kline[kline.symbol] = kline
                    else:
                        prev_kline = self.prev_kline[kline.symbol]
                        # skip any old klines or duplicates
                        if kline.ts <= prev_kline.ts:
                            self._last_ts = prev_kline.ts
                            continue
                        self.prev_kline[kline.symbol] = kline
                    # print only once every 30 minutes
                    if kline.ts != self._last_ts: # and kline.ts % 1800 == 0:
                        pd.to_datetime(kline.ts, unit='s')
                        print(f"{pd.to_datetime(kline.ts, unit='s')} {kline.symbol} Low: {kline.low}, High: {kline.high}, Open: {kline.open}, Close: {kline.close} Volume: {kline.volume}")
                    self.mtrader.market_update(kline, current_price=kline.close, current_ts=kline.ts, granularity=self.granularity)
                    self._last_ts = kline.ts


def main(name):
    exchange = TraderSelectExchange(name).get_exchange()

    # top 35 cryptocurrencies
    top_crypto = [
        "BTC-USD",  # Bitcoin
        "ETH-USD",  # Ethereum
        "BNB-USD",  # Binance Coin
        "XRP-USD",  # XRP
        "SOL-USD",  # Solana
        "DOGE-USD", # Dogecoin
        "ADA-USD",  # Cardano
        "TRX-USD",  # TRON
        "AVAX-USD", # Avalanche
        "LINK-USD", # Chainlink
        "SHIB-USD", # Shiba Inu
        "TON-USD",  # Toncoin
        "SUI-USD",  # Sui
        "DOT-USD",  # Polkadot
        "XLM-USD",  # Stellar
        "HBAR-USD", # Hedera
        "BCH-USD",  # Bitcoin Cash
        "UNI-USD",  # Uniswap
        "PEPE-USD", # Pepe
        "LTC-USD",  # Litecoin
        "LEO-USD",  # UNUS SED LEO
        "NEAR-USD", # NEAR Protocol
        "APT-USD",  # Aptos
        "ICP-USD",  # Internet Computer
        "AAVE-USD", # Aave
        "ETC-USD",  # Ethereum Classic
        "POL-USD",  # POL (ex-MATIC)
        "BGB-USD",  # Bitget Token
        "RNDR-USD", # Render
        "CRO-USD",  # Cronos
        "VET-USD",  # VeChain
        "FET-USD",  # Fetch.ai
        "ARB-USD",  # Arbitrum
        "TAO-USD",  # Bittensor
        "FIL-USD"   # Filecoin
    ]

    tconfig = TraderConfig(path=f'config/{name}_trader_live_config.json')
    if not tconfig.load_config():
        print(f"Failed to load config {tconfig.get_config_path()}")
        tconfig.save_config()

    tconfig.set_trade_symbols(trade_symbols=top_crypto)

    market = Market(exchange=exchange, db_path=tconfig.market_db_path())
    account = Account(exchange=exchange, market=market)
    account.load_symbol_info()
    account.load_asset_info()

    print(f'Account name: {account.name()}')
    if not account.load_symbol_info():
        print("Failed to load symbol info")
        return
    print(account.get_account_balances())
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))

    ex = TraderExecute(exchange=exchange, account=account, config=tconfig)

    orders = Orders(config=tconfig, db_path=tconfig.orders_db_path(), reset=False)

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig, orders=orders, granularity=GRANULARITY)
    rt = CBADVLive(mtrader=mtrader, market=market, tconfig=tconfig)
    ws_client = WSClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
    #accnt = AccountCoinbaseAdvanced(exchange=exchange, simulate=False, live=False, logger=logger)

    running = True

    channels = ['heartbeats', 'user', 'candles']

    #product_ids = ["BTC-USD", "SOL-USD", "ETH-USD"]
    ws_client.open()
    ws_client.subscribe(product_ids=top_crypto, channels=channels) #, 'matches'])

    while running:
        try:
            # Wait for 1 second or until input is available
            i, _, _ = select.select([sys.stdin], [], [], 1)
            if i:
                input_char = sys.stdin.readline().strip()
                if input_char == 'q':
                    ws_client.unsubscribe(product_ids=top_crypto, channels=channels)
                    ws_client.close()
                    running = False
                    print("Exiting...")
        except (KeyboardInterrupt, SystemExit):
            ws_client.unsubscribe(product_ids=top_crypto, channels=channels)
            ws_client.close()
            running = False
            print("Exiting...")
        except Exception as e:
            print(f"Error: {e}")
            ws_client.unsubscribe(product_ids=top_crypto, channels=channels)
            ws_client.close()
            running = False

if __name__ == '__main__':
    main("cbadv")
