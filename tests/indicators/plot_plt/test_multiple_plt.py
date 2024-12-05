import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.EMA import EMA
from cointrader.indicators.SuperSmoother import SuperSmoother
from cointrader.indicators.ZLEMA import ZLEMA
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot EMA indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    # add condition to check if EMA is used
    parser.add_argument('--ema', action='store_true', help='Show EMA')
    parser.add_argument('--zlema', action='store_true', help='Show ZLEMA')
    args = parser.parse_args()
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    #ticker = exchange.info_ticker_join("BTC", "USD")
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

    if args.zlema:
        zlema24 = ZLEMA('ZLEMA', 24)
        zlema24_values = []
        zlema12 = ZLEMA('ZLEMA', 12)
    zlema12_values = []
    smoother = SuperSmoother(period=12)
    smoother_values = []
    if args.ema:
        ema12 = EMA(period=12)
        ema12_values = []
        ema24 = EMA(period=24)
        ema24_values = []

    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        if args.zlema:
            result = zlema24.update(kline)
            zlema24_values.append(result)
            result = zlema12.update(kline)
            zlema12_values.append(result)
        result = smoother.update(kline)
        smoother_values.append(result)
        if args.ema:
            result = ema12.update(kline)
            ema12_values.append(result)
            result = ema24.update(kline)
            ema24_values.append(result)
        opens.append(kline.open)
        closes.append(kline.close)
        highs.append(kline.high)
        lows.append(kline.low)
        volumes.append(kline.volume)
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)
        #timestamps.append(kline.ts)

    figures = []

    plt.figure(figsize=(14, 7))
    fig, = plt.plot(dates, closes, label='Close Prices', color='blue')
    figures.append(fig)

    if args.ema:
        fig, = plt.plot(dates, ema12_values, label='EMA 12', color='red')
        figures.append(fig)
        fig, = plt.plot(dates, ema24_values, label='EMA 24', color='green')
        figures.append(fig)
    #fig, = plt.plot(dates, smoother_values, label='SuperSmoother 12', color='purple')
    #figures.append(fig)

    if args.zlema:
        fig, = plt.plot(dates, zlema24_values, label='ZLEMA 24', color='orange')
        figures.append(fig)
        fig, = plt.plot(dates, zlema12_values, label='ZLEMA 12', color='black')
        figures.append(fig)

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{ticker} Plot multiple indicators')
    plt.legend(handles=figures)
    plt.grid(True)
    plt.show()