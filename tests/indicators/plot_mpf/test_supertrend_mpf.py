#!/usr/bin/env python3
import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse

sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.SuperTrend import SuperTrend
from cointrader.common.Kline import Kline

CLIENT_NAME = "cbadv"

def compute_true_range(df):
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = (df['High'] - df['Close'].shift(1)).abs()
    df['L-PC'] = (df['Low'] - df['Close'].shift(1)).abs()
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df.drop(['H-L', 'H-PC', 'L-PC'], axis=1, inplace=True)
    return df

def compute_atr(df, period=10):
    df['ATR'] = df['TR'].rolling(period).mean()
    return df

def supertrend(df, period=10, multiplier=3.0):
    df = compute_true_range(df)
    df = compute_atr(df, period)
    df['basic_ub'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
    df['basic_lb'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']
    df['final_ub'] = 0.0
    df['final_lb'] = 0.0
    idx_list = df.index.to_list()

    for i in range(period, len(df)):
        current_idx = idx_list[i]
        prev_idx = idx_list[i-1]
        if (df['Close'][current_idx] > df['final_ub'][prev_idx]) or (df['final_ub'][prev_idx] == 0):
            df.at[current_idx, 'final_ub'] = df['basic_ub'][current_idx]
        else:
            df.at[current_idx, 'final_ub'] = min(df['basic_ub'][current_idx], df['final_ub'][prev_idx])
        if (df['Close'][current_idx] < df['final_lb'][prev_idx]) or (df['final_lb'][prev_idx] == 0):
            df.at[current_idx, 'final_lb'] = df['basic_lb'][current_idx]
        else:
            df.at[current_idx, 'final_lb'] = max(df['basic_lb'][current_idx], df['final_lb'][prev_idx])

    df['Supertrend'] = np.nan
    trend_up = True

    for i in range(period, len(df)):
        current_idx = idx_list[i]
        prev_idx = idx_list[i-1]
        if df['Close'][current_idx] > df['final_ub'][prev_idx]:
            trend_up = True
        elif df['Close'][current_idx] < df['final_lb'][prev_idx]:
            trend_up = False
        if trend_up:
            df.at[current_idx, 'Supertrend'] = df['final_lb'][current_idx]
        else:
            df.at[current_idx, 'Supertrend'] = df['final_ub'][current_idx]

    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot SuperTrend indicator')
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
    elif granularity == 300:
        minutes = max_klines * 5
        granularity_name = "5m"
    elif granularity == 900:
        minutes = max_klines * 15
        granularity_name = "15m"
    elif granularity == 3600:
        hours = max_klines
        granularity_name = "1h"

    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    candles = exchange.market_get_klines_range(ticker, start, end, granularity)
    kline = Kline()
    kline.set_dict_names(ts='start')

    st = SuperTrend(period=10, multiplier=3)
    st_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        result = st.update(kline)
        print(result)
        if not st.ready():
            st_values.append(np.nan)
        else:
            st_values.append(result['supertrend'])
        opens.append(kline.open)
        closes.append(kline.close)
        highs.append(kline.high)
        lows.append(kline.low)
        volumes.append(kline.volume)
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)

    data = {
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)

    df = supertrend(df, period=10, multiplier=3.0)

    st_plot = mpf.make_addplot(st_values, panel=0, color='green', width=1.5)
    st_ref_plot = mpf.make_addplot(df['Supertrend'].values, panel=0, color='blue', width=1.5)

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{ticker} {granularity_name} chart with SuperTrend',
        ylabel='Price',
        addplot=[st_plot, st_ref_plot],
    )
