import sys
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.account.Account import Account
from cointrader.market.Market import Market

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    client = TraderSelectClient(CLIENT_NAME).get_client()

    market = Market(client=client)
    account = Account(client=client, market=market)
    account.load_symbol_info()

    print(f"Acccount balances: {account.get_account_balances()}")
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))
    print("Total BTC Balance:")
    print(account.get_total_balance("BTC"))


