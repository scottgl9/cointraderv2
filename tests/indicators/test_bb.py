import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.indicators.BB import BollingerBands
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Bollinger Bands indicator')
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

    bb = BollingerBands(period=20, std_dev=2)
    bb_upper_values = []
    bb_middle_values = []
    bb_lower_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = bb.update(kline)
        if not bb.ready():
            result['upper'] = np.nan
            result['middle'] = np.nan
            result['lower'] = np.nan
        upper = result['upper']
        middle = result['middle']
        lower = result['lower']
        bb_upper_values.append(upper)
        bb_middle_values.append(middle)
        bb_lower_values.append(lower)
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

bb_upper_plot = mpf.make_addplot(bb_upper_values, panel=0, color='blue', width=1.5)
bb_middle_plot = mpf.make_addplot(bb_middle_values, panel=0, color='red', width=1.5)
bb_lower_plot = mpf.make_addplot(bb_lower_values, panel=0, color='blue', width=1.5)

mpf.plot(
    df,
    type='candle',
    style='charles',
    title=f'{ticker} {granularity_name} chart with Bollinger Bands',
    ylabel='Price',
    addplot=[bb_upper_plot, bb_middle_plot, bb_lower_plot],
)