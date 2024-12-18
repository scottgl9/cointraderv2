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
from cointrader.account.Account import Account
from cointrader.market.Market import Market
from cointrader.execute.TradeExecute import TraderExecute
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline
from cointrader.order.Orders import Orders
from cointrader.config import *

GRANULARITY = 300

class CBADVLive:
    def __init__(self, mtrader: MultiTrader, tconfig: TraderConfig, granularity: int = 300):
        self.prev_kline = {}
        self.mtrader = mtrader
        self.tconfig = tconfig
        self.granularity = granularity

    def on_message(self, msg):
        kline = Kline()
        kline.set_dict_names(ts='start', symbol='product_id')
        ws_object = WebsocketResponse(json.loads(msg))
        #print(f"Channel: {ws_object.channel}")
        if ws_object.channel == "subscriptions":
            print(f"Subscriptions: {ws_object}")
        elif ws_object.channel == "user":
            print(f"User: {ws_object}")
        elif ws_object.channel == "heartbeat":
            print(f"Heartbeat: {ws_object}")
        elif ws_object.channel == "candles":
            for event in ws_object.events:
                for candle in event.candles:
                    kline.from_dict(dict(candle.__dict__))
                    kline.granularity = self.granularity

                    # skip any old klines which may come in when first starting
                    if abs(int(datetime.now().timestamp()) - kline.ts) > self.granularity * 2:
                        continue
                    #print(f"{int(datetime.now().timestamp()) - kline.ts} {kline.symbol}")
                    if kline.symbol not in self.prev_kline:
                        self.prev_kline[kline.symbol] = kline
                    else:
                        prev_kline = self.prev_kline[kline.symbol]
                        # skip any duplicate klines
                        if kline.ts == prev_kline.ts:
                            continue
                        self.prev_kline[kline.symbol] = kline
                    # print only once every 30 minutes
                    if kline.ts % 1800 == 0:
                        pd.to_datetime(kline.ts, unit='s')
                        print(f"{pd.to_datetime(kline.ts, unit='s')} {kline.symbol} Low: {kline.low}, High: {kline.high}, Open: {kline.open}, Close: {kline.close} Volume: {kline.volume}")
                    self.mtrader.market_update(kline, current_price=kline.close, current_ts=kline.ts)


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
    tconfig.set_trade_symbols(trade_symbols=top_crypto)
    tconfig.save_config()

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

    mtrader = MultiTrader(account=account, execute=ex, config=tconfig, granularity=GRANULARITY)
    rt = CBADVLive(mtrader=mtrader, tconfig=tconfig)
    ws_client = WSClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
    #accnt = AccountCoinbaseAdvanced(exchange=exchange, simulate=False, live=False, logger=logger)

    running = True

    #product_ids = ["BTC-USD", "SOL-USD", "ETH-USD"]
    ws_client.open()
    ws_client.subscribe(product_ids=top_crypto, channels=['candles']) #, 'matches'])

    while running:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            ws_client.unsubscribe(product_ids=top_crypto, channels=['candles', 'heartbeats', 'user'])#, 'matches'])
            ws_client.close()
            running = False
            print("Exiting...")

if __name__ == '__main__':
    main("cbadv")
