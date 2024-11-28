# Currently not working correcrly *FIXME*
import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.indicators.EMA import EMA
from cointrader.indicators.IchimokuCloud import IchimokuCloud
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Ichimoku Cloud indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    args = parser.parse_args()
    client = TraderSelectClient(CLIENT_NAME).get_client()
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

    ichimoku = IchimokuCloud()
    tenkan_sen_values = []
    kijun_sen_values = []
    senkou_span_a_values = []
    senkou_span_b_values = []
    chikou_span_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = ichimoku.update(kline)
        if ichimoku.ready():
            tenkan_sen_values.append(result['tenkan_sen'])
            kijun_sen_values.append(result['kijun_sen'])
            senkou_span_a_values.append(result['senkou_span_a'])
            senkou_span_b_values.append(result['senkou_span_b'])
            chikou_span_values.append(result['chikou_span'])
            print(f"Tenkan Sen: {result['tenkan_sen']}, Kijun Sen: {result['kijun_sen']}, Senkou Span A: {result['senkou_span_a']}, Senkou Span B: {result['senkou_span_b']}, Chikou Span: {result['chikou_span']}")
        else:
            tenkan_sen_values.append(np.nan)
            kijun_sen_values.append(np.nan)
            senkou_span_a_values.append(np.nan)
            senkou_span_b_values.append(np.nan)
            chikou_span_values.append(np.nan)
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

tenkan_sen_plot = mpf.make_addplot(tenkan_sen_values, panel=0, color='blue', width=1.5)
kijun_sen_plot = mpf.make_addplot(kijun_sen_values, panel=0, color='red', width=1.5)
senkou_span_a_plot = mpf.make_addplot(senkou_span_a_values, panel=0, color='green', width=1.5)
senkou_span_b_plot = mpf.make_addplot(senkou_span_b_values, panel=0, color='brown', width=1.5)
chikou_span_plot = mpf.make_addplot(chikou_span_values, panel=0, color='purple', width=1.5)

mpf.plot(
    df,
    type='candle',
    style='charles',
    title=f'{ticker} {granularity_name} chart with Ichimoku Cloud',
    ylabel='Price',
    addplot=[tenkan_sen_plot, kijun_sen_plot, senkou_span_a_plot, senkou_span_b_plot, chikou_span_plot],
)