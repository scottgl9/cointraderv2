import sys
try:
    import cointrader
except ImportError:
    sys.path.append('.')

from cointrader.client.cbadv.CBADVTraderClient import CBADVTraderClient
from cointrader.config import CBADV_KEY, CBADV_SECRET

if __name__ == '__main__':
    client = CBADVTraderClient(CBADV_KEY, CBADV_SECRET)
    print("info_base_currencies_list")
    print(client.info_base_currencies_list())
    print("info_quote_currencies_list")
    print(client.info_quote_currencies_list())
    print("info_ticker_names_list")
    print(client.info_ticker_names_list())
    print("info_ticker_create")
    print(client.info_ticker_join("BTC", "USD"))
    print("info_ticker_split")
    print(client.info_ticker_split("BTC-USD"))
    print("info_ticker_get_base")
    print(client.info_ticker_get_base("BTC-USD"))
    print("info_ticker_get_quote")
    print(client.info_ticker_get_quote("BTC-USD"))
    #print("info_ticker_query")
    #print(client.info_ticker_query("BTC-USD"))
    #print("info_currency_query")
    #print(client.info_currency_query("BTC"))