#!/usr/bin/env python3

import sys
try:
    import cointrader
except ImportError:
    sys.path.append('.')

from cointrader.account_old.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from cointrader.config import *
from coinbase.rest import RESTExchange

if __name__ == '__main__':
    exchange = RESTExchange(api_key=CBADV_KEY, api_secret=CBADV_SECRET)
    accnt = AccountCoinbaseAdvanced(exchange=exchange, simulate=False)
    print(exchange.get_product(product_id='BTC-USD'))
    print(exchange.get_accounts())
    print("getting account balances")
    balances = accnt.get_account_balances()
    print(balances)
    #print(exchange.get_fees())
    print("USD Total: {} USD".format(accnt.get_account_total_value('USD')))
    #print("BTC Total: {} BTC".format(accnt.get_account_total_value('BTC')))
    accnt.get_exchange_info()
    #ts = int(datetime.timestamp(datetime.now()))
    #print(ts)
    #print(accnt.ts_to_iso8601(ts))
    #symbols = accnt.get_all_ticker_symbols()
    #print(symbols)
    #accnt.load_exchange_info()
    #accnt_assets = accnt_info['assets']
    #assets = sorted(accnt_assets, key=lambda x: (accnt_assets[x]['usd']), reverse=True)
    #for asset in assets:
    #    print("{: >5}: {: >15} {: >10} USD\t{: >20} BTC".format(asset, accnt_assets[asset]['amount'], round(accnt_assets[asset]['usd'], 2), accnt_assets[asset]['btc']))

    #print("\nTotal balance USD = {}, BTC={}, BNB={}".format(accnt_info['total']['usd'],
    #                                                        accnt_info['total']['btc'],
    #                                                        accnt_info['total']['bnb']))
