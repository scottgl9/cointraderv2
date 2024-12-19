#!/usr/bin/env python3
import sys
#sys.path.append('./tests')
sys.path.append('.')
#from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
#from cointrader.account.Account import Account
#from cointrader.market.Market import Market
import ccxt
from cointrader.config import CBADV_KEY, CBADV_SECRET
from cointrader.common.SymbolInfo import SymbolInfo

CLIENT_NAME = "ccxt"

_excluded_currency_list = ['EUR', 'GBP', 'CDE', 'INTX']

def info_ticker_parse(ticker, response) -> SymbolInfo:
    """Parse ticker information from product info"""
    result = SymbolInfo()
    result.base_name = response['base']
    result.quote_name = response['quote']
    info = response['info']
    if 'price' in info:
        result.price = float(info['price'])
    else:
        result.price = 0.0

    result.base_min_size = float(info['base_min_size'])
    result.base_step_size = float(info['base_increment'])
    result.quote_min_size = float(info['quote_min_size'])
    result.quote_step_size = float(info['quote_increment'])

    def get_precision(step_size: float) -> int:
        step_size_str = f"{step_size:.10f}".rstrip('0')
        if '.' in step_size_str:
            return len(step_size_str.split('.')[1])
        return 0

    result.base_precision = get_precision(result.base_step_size)
    result.quote_precision = get_precision(result.quote_step_size)

    return result

def info_ticker_query_all(products) -> dict[str, SymbolInfo]:
    """Query all tickers"""
    result = {}
    for product in products:
        #if product['trading_disabled']:
        #    continue

        excluded = False

        for exclude in _excluded_currency_list:
            if str(product['info']['product_id']).endswith(f"-{exclude}"):
                excluded = True
                break

        if excluded:
            continue

        #print(product['info']['product_id'])

        symbol_info = info_ticker_parse(product['info']['product_id'], product)
        result[product['info']['product_id']] = symbol_info
    return result

def main(name):
    #exchange = TraderSelectExchange(name).get_exchange()
    client = ccxt.coinbaseadvanced({
            'apiKey': CBADV_KEY,
            'secret': CBADV_SECRET,
        })
    
    products = client.fetch_markets()
    info = info_ticker_query_all(products)
    for i in info.values():
        print(i)

    return

    market = Market(exchange=exchange)
    account = Account(exchange=exchange, market=market)
    account.load_symbol_info()
    account.load_asset_info()

    print(f"Acccount balances:")
    balances = account.get_account_balances()
    for currency, (balance, hold) in balances.items():
        total = balance + hold
        if total > 0.0:
            print(f"{currency}: {total}")
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))
    print("Total BTC Balance:")
    print(account.get_total_balance("BTC"))


if __name__ == '__main__':
    main(CLIENT_NAME)
