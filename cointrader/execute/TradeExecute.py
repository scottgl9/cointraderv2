from cointrader.exchange.TraderExchangeBase import TraderExchangeBase
from cointrader.order.OrderResult import OrderResult
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
from .ExecuteBase import ExecuteBase

class TraderExecute(ExecuteBase):
    def __init__(self, exchange: TraderExchangeBase, account: AccountBase, config: TraderConfig):
        self._exchange = exchange
        self._account = account
        self._config = config

    def account(self) -> AccountBase:
        return self._account

    def market_buy(self, symbol: str, amount: float, current_price: float, current_ts: int) -> OrderResult:
        return self._exchange.trade_buy_market(ticker=symbol, amount=amount)
    
    def market_sell(self, symbol: str, amount: float, current_price: float, current_ts: int) -> OrderResult:
        return self._exchange.trade_sell_market(ticker=symbol, amount=amount)
    
    def limit_buy(self, symbol: str, limit_price: float, amount: float) -> OrderResult:
        return self._exchange.trade_buy_limit(ticker=symbol, amount=amount, price=limit_price)

    def limit_sell(self, symbol: str, limit_price: float, amount: float) -> OrderResult:
        return self._exchange.trade_sell_limit(ticker=symbol, amount=amount, price=limit_price)

    def stop_loss_limit_buy(self, symbol: str, limit_price: float, stop_price: float, amount: float) -> OrderResult:
        return self._exchange.trade_buy_stop_limit(ticker=symbol, amount=amount, price=limit_price, stop_price=stop_price)
    
    def stop_loss_limit_sell(self, symbol: str, limit_price: float, stop_price: float, amount: float) -> OrderResult:
        return self._exchange.trade_sell_stop_limit(ticker=symbol, amount=amount, price=limit_price, stop_price=stop_price)

    def status(self, symbol: str, order_id: str, current_price: float, current_ts: int) -> OrderResult:
        return self._exchange.trade_get_order(symbol, order_id)

    def cancel(self, symbol: str, order_id: str, current_price: float, current_ts: int) -> OrderResult:
        return self._exchange.trade_cancel_order(symbol, order_id)
