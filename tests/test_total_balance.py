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
