import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.indicators.SAMA import SlopeAdaptiveMovingAverage
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot ADX indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    #parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    args = parser.parse_args()
    client = TraderSelectClient(CLIENT_NAME).get_client()
    #ticker = client.info_ticker_join("BTC", "USD")
    ticker = args.ticker
    tickers = client.info_ticker_names_list()
    if ticker not in tickers:
        print("Ticker not found")
        sys.exit(1)
    granularities = client.market_get_kline_granularities()
    if GRANULARITY not in granularities:
        print("Granularity not found")
        sys.exit(1)
    max_klines = client.market_get_max_kline_count(GRANULARITY)

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

    candles = client.market_get_klines_range(ticker, start, end, GRANULARITY)
    kline = Kline()
    kline.set_dict_names(ts='start')

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

sama = SlopeAdaptiveMovingAverage()
sama_values = []

for candle in reversed(candles):
    kline.from_dict(candle)
    result = sama.update(kline)
    sama_values.append(result['ma'])
    opens.append(kline.open)
    closes.append(kline.close)
    highs.append(kline.high)
    lows.append(kline.low)
    volumes.append(kline.volume)
    date = pd.to_datetime(kline.ts, unit='s')
    dates.append(date)

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

sama_plot = mpf.make_addplot(sama_values, panel=0, color='green', width=1.5)

mpf.plot(
    df,
    type='candle',
    style='charles',
    title=f'{ticker} {granularity_name} chart with SAMA',
    ylabel='Price',
    addplot=[sama_plot],
)