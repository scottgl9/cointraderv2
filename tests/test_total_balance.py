import sys
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.account.Account import Account
from cointrader.market.Market import Market

CLIENT_NAME = "cbadv"

def main(name):
    exchange = TraderSelectExchange(name).get_exchange()

    market = Market(exchange=exchange)
    account = Account(exchange=exchange, market=market)
    account.load_symbol_info()

    print(f"Acccount balances: {account.get_account_balances()}")
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))
    print("Total BTC Balance:")
    print(account.get_total_balance("BTC"))


if __name__ == '__main__':
    main(CLIENT_NAME)
