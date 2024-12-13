#!/usr/bin/env python3
import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.ATR import ATR
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
import argparse
from ta.volatility import AverageTrueRange
from ta.utils import dropna

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot ATR indicator')
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

    atr = ATR('ATR', 14)
    atr_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = atr.update(kline)
        if atr.ready():
            atr_values.append(result)
        else:
            atr_values.append(np.nan)
        opens.append(kline.open)
        closes.append(kline.close)
        highs.append(kline.high)
        lows.append(kline.low)
        volumes.append(kline.volume)
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)

    # Create a DataFrame for the candlestick chart
    data = {
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }
    df = pd.DataFrame(data)
    df = dropna(df)

    print(atr_values)

    atr_indicator = AverageTrueRange(high=pd.Series(highs), low=pd.Series(lows), close=pd.Series(closes), window=14, fillna=True)
    df['atr'] = atr_indicator.average_true_range()

    # Create a figure with two subplots
    fig, (ax1, ax3, ax2) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Plot ATR on the first subplot
    ax1.plot(dates, df['atr'].values, label='ATR (ta)', color='red')
    ax1.plot(dates, atr_values, label='ATR (custom)', color='green')
    ax1.set_title(f'ATR Indicator Comparison for {ticker}')
    ax1.set_ylabel('ATR Value')
    ax1.legend()

    ax3.plot(dates, atr_values, label='ATR (custom)', color='blue')
    ax3.set_title(f'Close Price for {ticker}')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Close Price')
    ax3.legend()

    # Plot close values on the second subplot
    ax2.plot(dates, df['close'].values, label='Close Price', color='blue')
    ax2.set_title(f'Close Price for {ticker}')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Close Price')
    ax2.legend()

    # Show the plot
    plt.show()
