# Thik file is used to define a trade size strategy based on the ATR of the price.
from cointrader.common.TradeSizeBase import TradeSizeBase
from cointrader.account.AccountBase import AccountBase
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.common.Kline import Kline
from cointrader.indicators.ATR import ATR

class ATRSize(TradeSizeBase):
    def __init__(self, name='trade_size_atr', symbol=None, account=None, config=None):
        super().__init__(name=name, symbol=symbol, account=account, config=config)
        self._max_position_quote_size = self._config.max_position_quote_size()
        self._atr_period = 14
        self._atr_threshold = 0.02
        self._atr = ATR(period=self._atr_period)

    def reset(self):
        self._atr.reset()

    def ready(self) -> bool:
        return self._atr.ready()

    def get_base_trade_size(self, current_price: float, current_ts: int) -> float:
        if current_price > 0:
            quote_size = self._get_scaled_trade_size_quote(current_price)
            if quote_size is None:
                return None
            
            size = self._account.round_base(self._symbol, quote_size / current_price)
            if size < self._account.get_base_min_size(self._symbol):
                print(f"{self._symbol} Size too small: {size}")
                return None
            return size
        return None

    def get_quote_trade_size(self, current_price: float, current_ts: int) -> float:
        return self._get_scaled_trade_size_quote(current_price)

    def update(self, kline: Kline):
        self._atr.update(kline)

    def _get_scaled_trade_size_quote(self, current_price: float) -> float:
        """
        Compute the quote size dynamically based on ATR.
        For example:
        - Compute ATR% = ATR / current_price.
        - If ATR% > atr_threshold, scale down the position size proportionally.
        - If ATR% < atr_threshold, use closer to the full max position size.

        You can adjust the scaling logic as desired:
        Here, if ATR% == atr_threshold -> we use 50% of max size.
        Above threshold, reduce further; below threshold, approach max size.
        """
        max_quote = self._max_position_quote_size
        if current_price <= 0 or not self._atr.ready():
            # If we don't have a valid price or indicator isn't ready, just return None or a safe default
            return None

        current_atr = self._atr.get_last_value()
        if current_atr is None:
            return None

        atr_percent = current_atr / current_price  # ATR as fraction of price

        # Simple linear scaling logic:
        # If atr_percent == 0, size = max
        # If atr_percent == atr_threshold, size = 0.5 * max
        # If atr_percent > atr_threshold, less than 0.5 * max (down to a minimum)
        # If atr_percent < atr_threshold, between 0.5 * max and max

        # Define min and max scaling factors (between what fractions of max size we scale):
        min_scale = 0.1   # minimum 10% of max size in extremely volatile conditions
        mid_scale = 0.5   # scale at threshold
        max_scale = 1.0   # maximum is full size when volatility is very low

        if atr_percent > self._atr_threshold:
            # Above threshold, scale between mid_scale and min_scale
            # The further above threshold, the closer to min_scale.
            # For simplicity: scale linearly with a max cap on how big it can get.
            # For example, if atr_percent is twice the threshold, go to min_scale.
            # Linear interpolation:
            # at atr_threshold => mid_scale
            # at 2 * atr_threshold => min_scale
            # More general formula:
            # scale = mid_scale + (min_scale - mid_scale) * ((atr_percent - atr_threshold) / atr_threshold)
            # This scales linearly from mid_scale at threshold to min_scale at double threshold.
            factor = (atr_percent - self._atr_threshold) / self._atr_threshold
            scale = mid_scale + (min_scale - mid_scale) * factor
            # Prevent going below min_scale
            scale = max(scale, min_scale)
        else:
            # Below threshold, scale between mid_scale and max_scale
            # at atr_percent = 0 => max_scale
            # at atr_percent = atr_threshold => mid_scale
            # scale = max_scale - (max_scale - mid_scale) * (atr_percent / atr_threshold)
            factor = (atr_percent / self._atr_threshold)
            scale = max_scale - (max_scale - mid_scale) * factor
            # Prevent going above max_scale
            scale = min(scale, max_scale)

        return max_quote * scale
