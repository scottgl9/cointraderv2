#!/usr/bin/env python3
import sys
import mplfinance as mpf
import pandas as pd
import numpy as np
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.HeikinAshi import HeikinAshi
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
import argparse

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Heikin-Ashi indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol (ex. BTC-USD)', default='BTC-USD')
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

    heikinashi = HeikinAshi()
    ha_opens = []
    ha_closes = []
    ha_highs = []
    ha_lows = []
    dates = []

    for candle in reversed(candles):
        kline.from_dict(candle)
        ha_kline = heikinashi.update(kline)
        if ha_kline is None:
            ha_opens.append(np.nan)
            ha_closes.append(np.nan)
            ha_highs.append(np.nan)
            ha_lows.append(np.nan)
        else:
            ha_opens.append(ha_kline['open'])
            ha_closes.append(ha_kline['close'])
            ha_highs.append(ha_kline['high'])
            ha_lows.append(ha_kline['low'])
        date = pd.to_datetime(kline.ts, unit='s')
        dates.append(date)

    data = {
        'Date': dates,
        'Open': ha_opens,
        'High': ha_highs,
        'Low': ha_lows,
        'Close': ha_closes
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{ticker} {granularity_name} Heikin-Ashi chart',
        ylabel='Price',
    )
