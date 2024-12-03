import matplotlib.pyplot as plt
import requests
import json
import pandas as pd
from coinbase.rest import RESTExchange
import time
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from trader.config import *

def plot_historical_data(data, title='Historical Data'):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['close'], label='Close Price')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def main():
    product_id = 'BTC-USD'
    accnt = AccountCoinbaseAdvanced(simulate=False)
    klines = accnt.get_klines(days=1, hours=0, ticker_id=product_id, granularity=3600)
    klines = json.dumps(klines)
    print(klines)
    numeric_columns = ['start', 'low', 'high', 'open', 'close', 'volume']
    df = pd.read_json(klines, orient='records')
    #df['start'] = pd.to_datetime(df['start'], unit='s')

    df[numeric_columns] = df[numeric_columns].astype(float)
    df.set_index('start', inplace=True)

    # Plot historical data
    plot_historical_data(df, title=f'Historical Data for {product_id}')

if __name__ == "__main__":
    main()