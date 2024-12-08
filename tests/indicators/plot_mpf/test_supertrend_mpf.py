import sys
import mplfinance as mpf
import numpy as np
import pandas as pd
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.indicators.SuperTrend import SuperTrend
from cointrader.common.Kline import Kline
from datetime import datetime, timedelta
import argparse

CLIENT_NAME = "cbadv"
GRANULARITY = 3600

def compute_true_range(df):
    # True Range is the maximum of the following: 
    # current high - current low,
    # abs(current high - previous close),
    # abs(current low - previous close)
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = (df['High'] - df['Close'].shift(1)).abs()
    df['L-PC'] = (df['Low'] - df['Close'].shift(1)).abs()

    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df.drop(['H-L', 'H-PC', 'L-PC'], axis=1, inplace=True)

    return df

def compute_atr(df, period=10):
    # ATR is typically a rolling mean (or EMA) of the True Range.
    # Here we use a simple moving average, but you can change to EMA if desired.
    df['ATR'] = df['TR'].rolling(period).mean()
    return df

def supertrend(df, period=10, multiplier=3.0):
    # First, compute True Range and ATR
    df = compute_true_range(df)
    df = compute_atr(df, period)

    # Basic Upper & Lower Bands
    df['basic_ub'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
    df['basic_lb'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']

    # Initialize the final upper and lower band columns
    df['final_ub'] = 0.0
    df['final_lb'] = 0.0

    # Convert index to a list for indexing convenience
    # Not strictly necessary, but can help readability
    idx_list = df.index.to_list()

    # Calculate final_ub and final_lb iteratively
    for i in range(period, len(df)):
        current_idx = idx_list[i]
        prev_idx = idx_list[i-1]

        # final_ub calculation
        if (df['Close'][current_idx] > df['final_ub'][prev_idx]) or (df['final_ub'][prev_idx] == 0):
            df.at[current_idx, 'final_ub'] = df['basic_ub'][current_idx]
        else:
            df.at[current_idx, 'final_ub'] = min(df['basic_ub'][current_idx], df['final_ub'][prev_idx])

        # final_lb calculation
        if (df['Close'][current_idx] < df['final_lb'][prev_idx]) or (df['final_lb'][prev_idx] == 0):
            df.at[current_idx, 'final_lb'] = df['basic_lb'][current_idx]
        else:
            df.at[current_idx, 'final_lb'] = max(df['basic_lb'][current_idx], df['final_lb'][prev_idx])

    # Determine the Supertrend
    df['Supertrend'] = np.nan
    trend_up = True  # Initial guess

    for i in range(period, len(df)):
        current_idx = idx_list[i]
        prev_idx = idx_list[i-1]

        # Check for trend change
        if df['Close'][current_idx] > df['final_ub'][prev_idx]:
            trend_up = True
        elif df['Close'][current_idx] < df['final_lb'][prev_idx]:
            trend_up = False

        # Assign Supertrend based on trend direction
        if trend_up:
            df.at[current_idx, 'Supertrend'] = df['final_lb'][current_idx]
        else:
            df.at[current_idx, 'Supertrend'] = df['final_ub'][current_idx]

    return df

# Example usage:
# Suppose you have a DataFrame with Date, Open, High, Low, Close columns
# df = pd.read_csv('some_price_data.csv', parse_dates=['Date'])
# df.set_index('Date', inplace=True)
# df = supertrend(df, period=10, multiplier=3.0)
# Now, df['Supertrend'] column contains the Supertrend values.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot SuperTrend indicator')
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
