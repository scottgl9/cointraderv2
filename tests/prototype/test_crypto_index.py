import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.EMA import EMA
from cointrader.indicators.ZLEMA import ZLEMA
from cointrader.indicators.SuperTrend import SuperTrend
from cointrader.indicators.RSI import RSI
from cointrader.indicators.proto.MANormalize import MANormalize
from cointrader.indicators.ROC import ROC
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
import argparse

CLIENT_NAME = "cbadv"
GRANULARITY = 86400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot EMA indicator')
    parser.add_argument('--ticker', type=str, help='Ticker symbol', default='BTC-USD')
    #parser.add_argument('--granularity', type=int, help='Granularity in seconds', default=3600)
    args = parser.parse_args()
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    #ticker = exchange.info_ticker_join("BTC", "USD")
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
    elif GRANULARITY == 86400:
        hours = max_klines * 24
        granularity_name = "1d"

    end = datetime.now()
    start = int((end - timedelta(hours=hours, minutes=minutes)).timestamp())
    end = int(end.timestamp())

    symbols_with_weights = {
        'BTC-USD': 0.25,
        'ETH-USD': 0.2,
        'XRP-USD': 0.1,
        'ADA-USD': 0.1,
        'SOL-USD': 0.05,
        'DOGE-USD': 0.05,
        'MATIC-USD': 0.05,
        'LTC-USD': 0.05,
        'LINK-USD': 0.025,
        'AVAX-USD': 0.025,
        'ATOM-USD': 0.025,
        'ALGO-USD': 0.025,
        'VET-USD': 0.025,
        'HBAR-USD': 0.025
    }

    index_values = []
    btc_values = []
    weighted_klines = []
    dates = []

    for ticker in symbols_with_weights.keys():
        print("ticker: ", ticker)
        candles = exchange.market_get_klines_range(ticker, start, end, GRANULARITY)
        kline = Kline()
        kline.set_dict_names(ts='start')
        closes = []
        opens = []
        highs = []
        lows = []
        volumes = []

        count = 0
        roc = ROC(period=20) #MANormalize(period=50)
        roc_values = []

        for candle in reversed(candles):
            kline.from_dict(candle)
            if ticker == 'BTC-USD':
                btc_values.append(kline.close)
            closes.append(kline.close)
            opens.append(kline.open)
            highs.append(kline.high)
            lows.append(kline.low)
            volumes.append(kline.volume)
            result = roc.update(kline)
            if result is not None:
                roc_values.append(result)
                date = pd.to_datetime(kline.ts, unit='s')
                dates.append(date)
            #if date not in dates:
            #    dates.append(date)
            count += 1

        #weighted_closes = np.array(closes) * symbols_with_weights[ticker]
        #weighted_opens = np.array(opens) * symbols_with_weights[ticker]
        #weighted_highs = np.array(highs) * symbols_with_weights[ticker]
        #weighted_lows = np.array(lows) * symbols_with_weights[ticker]
        #weighted_volumes = np.array(volumes) * symbols_with_weights[ticker]
        weighted_rocs = np.array(roc_values) * symbols_with_weights[ticker]
        if len(index_values) == 0:
            print(len(weighted_rocs))
            print(len(index_values))
            index_values = weighted_rocs #weighted_closes
        else:
            print(len(weighted_rocs))
            print(len(index_values))
            index_values += weighted_rocs #weighted_closes

    print(len(index_values))
    print(len(dates))

    dates = dates[:len(index_values)]
    btc_values = btc_values[:len(index_values)]
    print(len(dates))


    index_ema = EMA(period=20)
    index_ema_values = []
    index_ema_24 = EMA(period=50)
    index_ema_24_values = []

    index_zlema = ZLEMA(period=12)
    index_zlema_values = []
    st = SuperTrend(period=12)
    st_values = []

    for value in index_values:
        result = index_ema.update_with_value(value)
        index_ema_values.append(result)
        result = index_ema_24.update_with_value(value)
        index_ema_24_values.append(result)
        #result = index_zlema.update_value(value)
        #index_zlema_values.append(result)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    ax1.plot(dates, index_values, label='Index Values', color='blue')
    ax1.plot(dates, index_ema_values, label='Index EMA 12', color='red')
    ax1.plot(dates, index_ema_24_values, label='Index EMA 24', color='green')
    ax1.set_ylabel('Index Value')
    ax1.set_title('Top 15 Cryptocurrency Index and EMA')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(dates, btc_values, label='BTC Values', color='orange')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('BTC Value')
    ax2.set_title('BTC Values')
    ax2.legend()
    ax2.grid(True)

    plt.show()