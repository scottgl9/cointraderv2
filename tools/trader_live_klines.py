#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse, WSClientConnectionClosedException, WSClientException
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
from threading import RLock, Thread
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.account.Account import Account
from cointrader.market.Market import Market
from cointrader.execute.TradeExecute import TraderExecute
from cointrader.execute.pipeline.ExecutePipeline import ExecutePipeline
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline
from cointrader.order.Orders import Orders
from cointrader.common.KlineEmitter import KlineEmitter
from cointrader.config import *
import sys
import select

GRANULARITY = 300

def fetch_preload_klines(market: Market, symbol: str, granularity: int):
    klines = []
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

    end = datetime.now() #- timedelta(seconds=granularity)
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    candles = market.market_get_klines_range(symbol, start, end, granularity)

    for candle in reversed(candles):
        kline = Kline()
        kline.set_dict_names(ts='start')
        kline.from_dict(candle)
        kline.granularity = granularity
        klines.append(kline)
        #self.mtrader.market_preload(symbol, kline)
    return klines

class PipelineExecutionThread(Thread):
    def __init__(self, exec_pipe: ExecutePipeline):
        Thread.__init__(self)
        self._exec_pipe = exec_pipe

    def run(self):
        while True:
            self._exec_pipe.process_order_requests()
            time.sleep(10 / 1000) # sleep for 10ms

class CBADVLive:
    def __init__(self, mtrader: MultiTrader, market: Market, tconfig: TraderConfig, granularity: int = 300):
        self.prev_kline = {}
        self.mtrader: MultiTrader = mtrader
        self.market = market
        self.tconfig = tconfig
        self.granularity = granularity
        self.running = True
        self.last_ts = 0
        self.lock = RLock()
        self.kline_queue = deque(maxlen=100)

    def on_message(self, msg):
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
                    kline = Kline()
                    kline.set_dict_names(ts='start', symbol='product_id')
                    kline.from_dict(dict(candle.__dict__))
                    kline.granularity = self.granularity

                    # print only once every 15 minutes
                    #if kline.ts != self._last_ts and kline.ts % 900 == 0:
                    #pd.to_datetime(kline.ts, unit='s')
                    #print(f"{pd.to_datetime(kline.ts, unit='s')} {kline.symbol} Low: {kline.low}, High: {kline.high}, Open: {kline.open}, Close: {kline.close} Volume: {kline.volume}")

                    with self.lock:
                        self.kline_queue.append(kline)


def main(name):
    OTHER_TIMEFRAME = 1800
    exchange = TraderSelectExchange(name).get_exchange()

    # top 35 cryptocurrencies
    top_crypto = [
        "BTC-USD",  # Bitcoin
        "ETH-USD",  # Ethereum
        "XRP-USD",  # XRP
        "SOL-USD",  # Solana
        "DOGE-USD", # Dogecoin
        "ADA-USD",  # Cardano
        "AVAX-USD", # Avalanche
        "LINK-USD", # Chainlink
        "SHIB-USD", # Shiba Inu
        "SUI-USD",  # Sui
        "DOT-USD",  # Polkadot
        "XLM-USD",  # Stellar
        "HBAR-USD", # Hedera
        "BCH-USD",  # Bitcoin Cash
        "UNI-USD",  # Uniswap
        "PEPE-USD", # Pepe
        "LTC-USD",  # Litecoin
        "NEAR-USD", # NEAR Protocol
        "APT-USD",  # Aptos
        "ICP-USD",  # Internet Computer
        "AAVE-USD", # Aave
        "ETC-USD",  # Ethereum Classic
        "POL-USD",  # POL (ex-MATIC)
        "RNDR-USD", # Render
        "CRO-USD",  # Cronos
        "VET-USD",  # VeChain
        "FET-USD",  # Fetch.ai
        "ARB-USD",  # Arbitrum
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

    ep = ExecutePipeline(execute=ex, max_orders=100, threaded=True)

    orders = Orders(config=tconfig, db_path=tconfig.orders_db_path(), reset=False)

    mtrader = MultiTrader(account=account, exec_pipe=ep, config=tconfig, orders=orders, restore_positions=True, granularity=GRANULARITY)

    # update quote balance before trying to open positions
    mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

    rt = CBADVLive(mtrader=mtrader, market=market, tconfig=tconfig)
    ws_client = WSClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
    #accnt = AccountCoinbaseAdvanced(exchange=exchange, simulate=False, live=False, logger=logger)

    running = True

    channels = ['heartbeats', 'user', 'candles']

    symbols = account.get_symbol_list()

    prev_kline = {}
    last_ts = 0
    last_price_check_ts = 0
    trading_symbol_list = top_crypto

    kline_emitters: dict[str, KlineEmitter] = {}

    # preload klines
    for symbol in trading_symbol_list:
        if symbol not in symbols:
            print(f"Symbol {symbol} not in list of symbols")
            continue

        print(f"Pre-loading klines for {symbol}")
        klines = fetch_preload_klines(market, symbol, GRANULARITY)
        prev_kline[symbol] = klines[-1]
        last_ts = prev_kline[symbol].ts
        mtrader.market_preload(symbol, klines)

        # emitter takes in 5m klines, and emits 15m klines
        kline_emitters[symbol] = KlineEmitter(src_granularity=GRANULARITY, dst_granularity=OTHER_TIMEFRAME)
        for kline in klines:
            kline_emitters[symbol].update(kline)
            if kline_emitters[symbol].ready():
                kline_15m = kline_emitters[symbol].emit()
                kline_emitters[symbol].reset()
                if kline_15m:
                    mtrader.market_update_kline_other_timeframe(symbol, kline_15m, OTHER_TIMEFRAME, preload=True)
        time.sleep(1)

    exec_pipe_thread = PipelineExecutionThread(exec_pipe=ep)
    exec_pipe_thread.daemon = True
    exec_pipe_thread.start()

    #product_ids = ["BTC-USD", "SOL-USD", "ETH-USD"]
    ws_client.open()
    ws_client.subscribe(product_ids=top_crypto, channels=channels)
    #ws_client.run_forever_with_exception_check()

    while running:
        try:
            if not rt.running:
                running = False
                break
            if not exec_pipe_thread.is_alive():
                print("Pipeline execution thread is not alive, restarting...")
                exec_pipe_thread = PipelineExecutionThread(exec_pipe=ep)
                exec_pipe_thread.start()

            # Wait for 1 second or until input is available
            i, _, _ = select.select([sys.stdin], [], [], 1)
            if i:
                input_char = sys.stdin.readline().strip()
                if input_char == 'q':
                    running = False
                    print("Exiting...")
    
            # every 60 seconds, get all prices
            current_ts = int(datetime.now().timestamp())
            if last_price_check_ts == 0 or current_ts - last_price_check_ts >= 60:
                last_price_check_ts = current_ts
                prices = account.get_all_prices()
                #print(f"Prices: {prices}")

                # update quote balance before trying to open positions (only do this once every 60 seconds)
                mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

                for symbol in trading_symbol_list:
                    if symbol in prices:
                        mtrader.market_update_price(symbol=symbol, current_price=prices[symbol], current_ts=current_ts, granularity=GRANULARITY)
                    else:
                        print(f"Symbol {symbol} not in prices")

            with rt.lock:
                klines = []
                while len(rt.kline_queue) > 0:
                    kline = rt.kline_queue.popleft()
                    if kline.ts <= prev_kline[kline.symbol].ts:
                        continue
                    klines.append(kline)
                    #print(kline)

            for kline in klines:
                # emit 15m klines for other timeframe strategies
                kline_emitter = kline_emitters[kline.symbol]
                kline_emitter.update(kline)
                if kline_emitter.ready():
                    kline_15m = kline_emitter.emit()
                    kline_15m.symbol = kline.symbol
                    kline_15m.granularity = kline_emitter.granularity()
                    mtrader.market_update_kline_other_timeframe(kline.symbol, kline_15m, kline_emitter.granularity(), preload=False)

                # print only once every 30 minutes
                if kline.ts != last_ts and kline.ts % OTHER_TIMEFRAME == 0:
                    pd.to_datetime(kline.ts, unit='s')
                    print(f"{pd.to_datetime(kline.ts, unit='s')} {kline.symbol} Low: {kline.low}, High: {kline.high}, Open: {kline.open}, Close: {kline.close} Volume: {kline.volume}")
                mtrader.market_update_kline(symbol=kline.symbol, kline=kline, granularity=GRANULARITY)
                prev_kline[kline.symbol] = kline
                last_ts = kline.ts

        except (KeyboardInterrupt, SystemExit):
            running = False
            print("Exiting...")
        except (WSClientConnectionClosedException, WSClientException) as e:
            # may need to restart websocket connection
            print(f"Error exception: {e}")
            print("Restarting websocket client...")
            # try to close feed, ignore any errors
            try:
                ws_client.unsubscribe(product_ids=top_crypto, channels=channels)
                ws_client.close()
            except:
                pass
            time.sleep(1)
            ws_client = WSClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
            if not ws_client:
                running = False
            else:
                ws_client.open()
                ws_client.subscribe(product_ids=top_crypto, channels=channels)


    if ws_client:
        ws_client.unsubscribe(product_ids=top_crypto, channels=channels)
        ws_client.close()
    
    #exec_pipe_thread.join(timeout=5)

if __name__ == '__main__':
    main("cbadv")
