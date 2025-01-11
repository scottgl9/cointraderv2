#!/usr/bin/env python3
import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.ATR import ATR
from cointrader.indicators.WILLR import WILLR
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
import argparse

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot WILLR indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol (ex. BTC-USD)', default='BTC-USD')
    parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    args = parser.parse_args()

    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    ticker = args.ticker
    tickers = exchange.info_ticker_names_list()
    if ticker not in tickers:
        print("Ticker not found")
        sys.exit(1)
    granularities = exchange.market_get_kline_granularities()
    if args.granularity not in granularities:
        print("Granularity not found")
        sys.exit(1)
    max_klines = exchange.market_get_max_kline_count(args.granularity)

    minutes = 0
    hours = 0

    granularity_name = ""

    if args.granularity == 60:
        minutes = max_klines
        granularity_name = "1m"
    elif args.granularity == 300: # 5 minutes
        minutes = max_klines * 5
        granularity_name = "5m"
    elif args.granularity == 900: # 15 minutes
        minutes = max_klines * 15
        granularity_name = "15m"
    elif args.granularity == 3600: # 1 hour
        hours = max_klines
        granularity_name = "1h"

    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    candles = exchange.market_get_klines_range(ticker, start, end, args.granularity)
    kline = Kline()
    kline.set_dict_names(ts='start')

    willr = WILLR(period=14)
    willr_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = willr.update(kline)
        if result is None:
            result = np.nan
        willr_values.append(result)
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

    willr_plot = mpf.make_addplot(willr_values, panel=1, color='blue', width=1.5)

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{ticker} {granularity_name} chart with WILLR',
        ylabel='Price',
        addplot=[willr_plot],
        panel_ratios=(3, 1),
    )
