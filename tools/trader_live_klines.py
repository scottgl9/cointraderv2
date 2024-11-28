from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.Account import Account
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig

def main():
    name = "cbadv"
    client = TraderSelectClient(name).get_client()
    account = Account(client=client)
    if not account.load_symbol_info():
        pass
    account.load_symbol_info()
    print(account.get_account_balances())
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))

    mtrader = MultiTrader(client=client, account=account, symbols=["BTCUSD"], config=TraderConfig())
