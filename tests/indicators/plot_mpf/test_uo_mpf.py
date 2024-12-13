#!/usr/bin/env python3
import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse

sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.UO import UltimateOscillator
from cointrader.common.Kline import Kline

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Ultimate Oscillator indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    args = parser.parse_args()
    
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    ticker = args.ticker
    granularity = args.granularity
    
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
    else:
        print("Unsupported granularity")
        sys.exit(1)

    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    candles = exchange.market_get_klines_range(ticker, start, end, granularity)
    kline = Kline()
    kline.set_dict_names(ts='start')

    uo = UltimateOscillator()
    uo_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = uo.update(kline)
        if uo.ready():
            uo_values.append(result)
        else:
            uo_values.append(np.nan)
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

    uo_plot = mpf.make_addplot(uo_values, panel=1, color='blue', width=1.5, ylabel='Ultimate Oscillator')

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{ticker} {granularity_name} chart with Ultimate Oscillator',
        ylabel='Price',
        addplot=[uo_plot],
    )
