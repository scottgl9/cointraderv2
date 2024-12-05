import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.KAMA import KAMA
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse
from ta.momentum import KAMAIndicator

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot KAMA indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    #parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    args = parser.parse_args()
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    #ticker = exchange.info_ticker_join("BTC", "USD")
    ticker = args.ticker
    tickers = exchange.info_ticker_names_list()
    if ticker not in tickers:
        print("Ticker not found")
        sys.exit(1)
    granularities = exchange.market_get_kline_granularities()
    if GRANULARITY not in granularities:
        print("Granularity not found")
        sys.exit(1)
    max_klines = exchange.market_get_max_kline_count(GRANULARITY)

    minutes = 0
    hours = 0

    granularity_name = ""

    if GRANULARITY == 60:
        minutes = max_klines
        granularity_name = "1m"
    elif GRANULARITY == 300: # 5 minutes
        minutes = max_klines * 5
        granularity_name = "5m"
    elif GRANULARITY == 900: # 15 minutes
        minutes = max_klines * 15
        granularity_name = "15m"
    elif GRANULARITY == 3600: # 1 hour
        hours = max_klines
        granularity_name = "1h"

    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    candles = exchange.market_get_klines_range(ticker, start, end, GRANULARITY)
    kline = Kline()
    kline.set_dict_names(ts='start')

    kama = KAMA('KAMA', 10, 2, 30)
    kama_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = kama.update(kline)
        if kama.ready():
            kama_values.append(result)
        else :
            kama_values.append(np.nan)
        opens.append(kline.open)
        closes.append(kline.close)
        highs.append(kline.high)
        lows.append(kline.low)
        volumes.append(kline.volume)
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)
        #timestamps.append(kline.ts)

# Create a DataFrame for the candlestick chart
data = {
    'Date': dates,
    'Open': opens,
    'High': highs,
    'Low': lows,
    'Close': closes
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

kama_indicator = KAMAIndicator(close=df['Close'], window=10, pow1=2, pow2=30, fillna=True)
print(kama_indicator.kama())