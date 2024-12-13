#!/usr/bin/env python3
import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.RSI import RSI
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
import argparse
from ta.momentum import RSIIndicator
from ta.utils import dropna

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot RSI indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    args = parser.parse_args()
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
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

    rsi = RSI('RSI', 14)
    rsi_values = []

    closes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = rsi.update(kline)
        if rsi.ready():
            rsi_values.append(result)
        else:
            rsi_values.append(np.nan)
        closes.append(kline.close)
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)

    print(rsi_values)

    # Create a DataFrame for the candlestick chart
    data = {
        'close': closes
    }
    df = pd.DataFrame(data)
    df = dropna(df)

    rsi_indicator = RSIIndicator(close=pd.Series(closes), window=14, fillna=True)
    df['rsi'] = rsi_indicator.rsi()

    # plot RSI side by side to validate the indicator works correctly
    plt.figure(figsize=(14, 7))
    plt.plot(dates, df['rsi'].values, label='RSI (ta)', color='red')
    plt.plot(dates, rsi_values, label='RSI (custom)', color='green')
    plt.title(f'RSI Indicator Comparison for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.legend()
    plt.show()
