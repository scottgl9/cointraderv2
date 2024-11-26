import sys
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    client = TraderSelectClient(CLIENT_NAME).get_client()
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