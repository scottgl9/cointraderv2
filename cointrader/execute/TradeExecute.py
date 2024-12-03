from cointrader.client.TraderClientBase import TraderClientBase
from cointrader.order.OrderResult import OrderResult
from cointrader.account.AccountBase import AccountBase
from .ExecuteBase import ExecuteBase

class TraderExecute(ExecuteBase):
    def __init__(self, client: TraderClientBase, account: AccountBase):
        self._client = client
    
    def market_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        return self._client.trade_buy_market(symbol, amount)
    
    def market_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        return self._client.trade_sell_market(symbol, amount)
    
    def limit_buy(self, symbol: str, price: float, amount: float) -> OrderResult:
        return self._client.trade_buy_limit(symbol, price, amount)
    
    def limit_sell(self, symbol: str, price: float, amount: float) -> OrderResult:
        return self._client.trade_sell_limit(symbol, price, amount)
    
    def stop_loss_buy(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        return self._client.trade_buy_stop_limit(symbol, price, stop_price, amount)
    
    def stop_loss_sell(self, symbol: str, price: float, stop_price: float, amount: float) -> OrderResult:
        return self._client.trade_sell_stop_limit(symbol, price, stop_price, amount)

    def status(self, symbol: str, order_id: str, price: float = 0) -> OrderResult:
        return self._client.trade_get_order(symbol, order_id)

    def cancel(self, symbol: str, order_id: str, price: float = 0) -> OrderResult:
        return self._client.trade_cancel_order(symbol, order_id)
