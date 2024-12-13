#!/usr/bin/env python3
import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse

sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.RSI import RSI
from cointrader.indicators.ZLEMA import ZLEMA
from cointrader.indicators.SLOPE import SlopeIndicator
from cointrader.common.Kline import Kline

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Slope indicator')
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

    slope = SlopeIndicator()
    zlema12 = ZLEMA(period=12)
    zlema24 = ZLEMA(period=24)
    slope_values = []
    slope_zlema12_values = []
    slope_zlema24_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = slope.update(kline)
        if slope.ready() and result is not None:
            slope_values.append(result)
            slope_zlema12_values.append(zlema12.update_with_value(slope.get_last_value()))
            slope_zlema24_values.append(zlema24.update_with_value(slope.get_last_value()))
        else:
            slope_values.append(np.nan)
            slope_zlema12_values.append(np.nan)
            slope_zlema24_values.append(np.nan)

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

    print(slope_values)

    slope_plot = mpf.make_addplot(slope_values, panel=1, color='blue', width=1.5, ylabel='Slope')
    slope_zlema12 = mpf.make_addplot(slope_zlema12_values, panel=1, color='red', width=1.5, ylabel='Slope')
    slope_zlema24 = mpf.make_addplot(slope_zlema24_values, panel=1, color='green', width=1.5, ylabel='Slope')

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{ticker} {granularity_name} chart with Slope',
        ylabel='Price',
        addplot=[slope_plot, slope_zlema12, slope_zlema24],
    )
