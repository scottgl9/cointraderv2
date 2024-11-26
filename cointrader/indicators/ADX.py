from cointrader.common.Indicator import Indicator
from cointrader.common.Kline import Kline
from .ATR import ATR
from .WMA import WMA

class ADX(Indicator):
    """ADX indicator using ATR for True Range and WMA for smoothing."""
    def __init__(self, name='adx', period=14):
        super().__init__(name)
        self.period = period
        self.atr = ATR(period=period)
        self.plus_dm_wma = WMA(period=period)
        self.minus_dm_wma = WMA(period=period)
        self.adx_wma = WMA(period=period)
        self.reset()

    def update(self, kline: Kline):
        # Update ATR to calculate True Range (TR)
        tr = self.atr.update(kline)
        if self._last_kline is None:
            print(f"Initializing with first kline: {kline}")
            self._last_kline = kline
            return None  # Not enough data yet

        # Debug: Print current and previous Kline
        print(f"Previous Kline: High={self._last_kline.high}, Low={self._last_kline.low}")
        print(f"Current Kline: High={kline.high}, Low={kline.low}")

        # Calculate Upward and Downward Movement
        up_move = kline.high - self._last_kline.high
        down_move = self._last_kline.low - kline.low

        # Calculate Directional Movement (DM)
        plus_dm = up_move if up_move > down_move and up_move > 0 else 0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0

        # Debug DM values
        print(f"TR: {tr}, Up Move: {up_move}, Down Move: {down_move}, +DM: {plus_dm}, -DM: {minus_dm}")

        # Smooth +DM and -DM using WMA
        smoothed_plus_dm = self.plus_dm_wma.update(plus_dm)
        smoothed_minus_dm = self.minus_dm_wma.update(minus_dm)

        if tr is None or smoothed_plus_dm is None or smoothed_minus_dm is None:
            self._last_kline = kline
            print(f"Insufficient data for smoothing: TR={tr}, Smoothed +DM={smoothed_plus_dm}, Smoothed -DM={smoothed_minus_dm}")
            return None  # Not enough data yet

        # Calculate Directional Indicators (+DI, -DI)
        plus_di = 100 * (smoothed_plus_dm / tr)
        minus_di = 100 * (smoothed_minus_dm / tr)

        # Debug DI values
        print(f"+DI: {plus_di}, -DI: {minus_di}")

        # Calculate DX
        di_sum = plus_di + minus_di
        di_diff = abs(plus_di - minus_di)
        dx = 100 * (di_diff / di_sum) if di_sum != 0 else 0

        # Debug DX value
        print(f"DX: {dx}")

        # Smooth DX to get ADX
        adx = self.adx_wma.update(dx)
        self._last_kline = kline
        self._last_value = adx

        # Debug ADX value
        print(f"ADX: {adx}")

        return adx

    def reset(self):
        self.atr.reset()
        self.plus_dm_wma.reset()
        self.minus_dm_wma.reset()
        self.adx_wma.reset()
        self._last_kline = None
        self._last_value = None

    def get_last_value(self):
        return self._last_value

    def ready(self) -> bool:
        return self.atr.ready() and self.plus_dm_wma.ready() and self.minus_dm_wma.ready() and self.adx_wma.ready()
