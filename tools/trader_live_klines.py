import sys
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.Account import Account
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig

def main():
    name = "cbadv"
    client = TraderSelectClient(name).get_client()
    account = Account(client=client)
    print(f'Account name: {account.name()}')
    if not account.load_symbol_info():
        print("Failed to load symbol info")
        return
    print(account.get_account_balances())
    print("Total USD Balance:")
    print(account.get_total_balance("USD"))

    tconfig = TraderConfig(path=f'{name}_trader_config.json')
    tconfig.save_config()
    mtrader = MultiTrader(account=account, config=tconfig)

if __name__ == '__main__':
    main()
