#!/usr/bin/env python3
import logging
from coinbase.websocket import WSExchange, WebsocketResponse
from coinbase.rest import RESTExchange

import json
import sys
import time
try:
    import cointrader
except ImportError:
    sys.path.append('.')

#from cointrader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from cointrader.config import *

class CBADVRealTime:
    low = 0.0
    high = 0.0
    open = 0.0
    close = 0.0
    def on_message(self, msg):
        ws_object = WebsocketResponse(json.loads(msg))
        if ws_object.channel == "candles":
            for event in ws_object.events:
                for candle in event.candles:
                    print(candle)
                    self.low = candle.low
                    self.high = candle.high
                    self.open = candle.open
                    self.close = candle.close
                    print(f"Low: {self.low}, High: {self.high}, Open: {self.open}, Close: {self.close}")
        #print(ws_object.channel)
        # if ws_object.channel == "ticker" :
        #     for event in ws_object.events:
        #         print(event)
        #         #for ticker in event.tickers:
        #         #    print(ticker)
        #         #    print(ticker.product_id + ": " + ticker.price)
        # elif ws_object.channel == "matches":
        #     for event in ws_object.events:
        #         print(event)
        #         #for match in event.matches:
        #         #    print(match)

if __name__ == '__main__':
    logging.getLogger("coinbase").setLevel(logging.WARNING)
    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.WARNING)
    exchange = RESTExchange(api_key=CBADV_KEY, api_secret=CBADV_SECRET)
    rt = CBADVRealTime()
    ws_exchange = WSExchange(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
    #accnt = AccountCoinbaseAdvanced(exchange=exchange, simulate=False, live=False, logger=logger)

    running = True

    product_ids = ["BTC-USD", "SOL-USD", "ETH-USD"]
    ws_exchange.open()
    ws_exchange.subscribe(product_ids=product_ids, channels=['candles']) #, 'matches'])

    while running:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            ws_exchange.unsubscribe(product_ids=product_ids, channels=['candles'])#, 'matches'])
            ws_exchange.close()
            running = False
            print("Exiting...")