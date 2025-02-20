#!/usr/bin/env python3
import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.EMA import EMA
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot EMA indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    parser.add_argument('--threshold', type=float, help='Threshold for valid crossover', default=0.1)
    args = parser.parse_args()
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    ticker = args.ticker
    granularity = args.granularity
    threshold = args.threshold
    tickers = exchange.info_ticker_names_list()
    if ticker not in tickers:
        print("Ticker not found")
        sys.exit(1)
    granularities = exchange.market_get_kline_granularities()
    if granularity not in granularities:
        print("Granularity not found")
        sys.exit(1)
    max_klines = exchange.market_get_max_kline_count(granularity)

    minutes = 0
    hours = 0

    granularity_name = ""

    if granularity == 60:
        minutes = max_klines
        granularity_name = "1m"
    elif granularity == 300: # 5 minutes
        minutes = max_klines * 5
        granularity_name = "5m"
    elif granularity == 900: # 15 minutes
        minutes = max_klines * 15
        granularity_name = "15m"
    elif granularity == 3600: # 1 hour
        hours = max_klines
        granularity_name = "1h"
    elif granularity == 86400:
        hours = max_klines * 24
        granularity_name = "1d"


    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    candles = exchange.market_get_klines_range(ticker, start, end, granularity)
    kline = Kline()
    kline.set_dict_names(ts='start')

    ema12 = EMA(period=12)
    ema12_values = []
    ema24 = EMA(period=24)
    ema24_values = []
    ema_diff_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        ema12_value = ema12.update(kline)
        ema24_value = ema24.update(kline)
        ema12_values.append(ema12_value)
        ema24_values.append(ema24_value)
        ema_diff_values.append((ema12_value - ema24_value) / ema24_value * 100)
        opens.append(kline.open)
        closes.append(kline.close)
        highs.append(kline.high)
        lows.append(kline.low)
        volumes.append(kline.volume)
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)

    # Calculate the moving average of the EMA differences
    ema_diff_ma = pd.Series(ema_diff_values).rolling(window=12).mean()

    # Filter out weak crossovers
    valid_crossovers = ema_diff_ma > threshold

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

    ema12_plot = mpf.make_addplot(ema12_values, panel=0, color='blue', width=1.5)
    ema24_plot = mpf.make_addplot(ema24_values, panel=0, color='red', width=1.5)
    valid_crossovers_plot = mpf.make_addplot(ema_diff_values, panel=1, color='green', width=1.5)

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{ticker} {granularity_name} chart with EMA12 and EMA24',
        ylabel='Price',
        addplot=[ema12_plot, ema24_plot, valid_crossovers_plot],

    )
