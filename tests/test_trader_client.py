import sys
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    print("info_base_currencies_list")
    print(exchange.info_base_currencies_list())
    print("info_quote_currencies_list")
    print(exchange.info_quote_currencies_list())
    print("info_ticker_names_list")
    print(exchange.info_ticker_names_list())
    print("info_ticker_create")
    print(exchange.info_ticker_join("BTC", "USD"))
    print("info_ticker_split")
    print(exchange.info_ticker_split("BTC-USD"))
    print("info_ticker_get_base")
    print(exchange.info_ticker_get_base("BTC-USD"))
    print("info_ticker_get_quote")
    print(exchange.info_ticker_get_quote("BTC-USD"))
    #print("info_ticker_query")
    #print(exchange.info_ticker_query("BTC-USD"))
    #print("info_currency_query")
    #print(exchange.info_currency_query("BTC"))