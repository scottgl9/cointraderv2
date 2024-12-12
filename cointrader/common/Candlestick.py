from .Kline import Kline
from collections import deque
from enum import Enum

class CandlestickType(Enum):
    DRAGONFLY_DOJI = 1
    GRAVESTONE_DOJI = 2
    LONG_LEGGED_DOJI = 3
    DOJI = 4
    HAMMER = 5
    INVERTED_HAMMER = 6
    SHOOTING_STAR = 7
    HANGING_MAN = 8
    MARUBOZU = 9
    SPINNING_TOP = 10
    BULLISH_ENGULFING = 11
    BEARISH_ENGULFING = 12
    PIERCING_PATTERN = 13
    DARK_CLOUD_COVER = 14
    THREE_WHITE_SOLDIERS = 15
    THREE_BLACK_CROWS = 16
    THREE_LINE_STRIKE = 17
    TWEEZER_TOP = 18
    TWEEZER_BOTTOM = 19
    UNKNOWN = 20

class CandlestickAnalyzer:
    def __init__(self, period=3):
        self._klines = deque(maxlen=period)
        self._period = period

    def reset(self):
        self._klines.clear()

    def update(self, kline: Kline):
        self._klines.append(kline)

    def is_bullish(self, kline):
        return kline.close > kline.open

    def is_bearish(self, kline):
        return kline.open > kline.close

    def is_doji(self, kline):
        return abs(kline.open - kline.close) <= (kline.high - kline.low) * 0.1

    def is_dragonfly_doji(self, kline):
        return self.is_doji(kline) and kline.high == max(kline.open, kline.close) and kline.low < min(kline.open, kline.close)

    def is_gravestone_doji(self, kline):
        return self.is_doji(kline) and kline.low == min(kline.open, kline.close) and kline.high > max(kline.open, kline.close)

    def is_long_legged_doji(self, kline):
        return self.is_doji(kline) and kline.high - kline.low > 2 * abs(kline.open - kline.close)

    def is_spinning_top(self, kline):
        body = abs(kline.open - kline.close)
        shadows = kline.high - kline.low
        return body < shadows * 0.3

    def is_hammer(self, kline):
        body = abs(kline.open - kline.close)
        lower_shadow = kline.open - kline.low if self.is_bullish(kline) else kline.close - kline.low
        upper_shadow = kline.high - kline.open if self.is_bullish(kline) else kline.high - kline.close
        return lower_shadow > 2 * body and upper_shadow < body

    def is_inverted_hammer(self, kline):
        body = abs(kline.open - kline.close)
        lower_shadow = kline.open - kline.low if self.is_bullish(kline) else kline.close - kline.low
        upper_shadow = kline.high - kline.open if self.is_bullish(kline) else kline.high - kline.close
        return upper_shadow > 2 * body and lower_shadow < body

    def is_shooting_star(self, kline):
        return self.is_inverted_hammer(kline) and self.is_bearish(kline)

    def is_hanging_man(self, kline):
        return self.is_hammer(kline) and self.is_bearish(kline)

    def is_marubozu(self, kline):
        return kline.open == kline.low or kline.close == kline.high

    def is_bullish_engulfing(self, prev_kline, kline):
        return prev_kline.close < prev_kline.open and kline.close > kline.open and kline.close > prev_kline.open and kline.open < prev_kline.close

    def is_bearish_engulfing(self, prev_kline, kline):
        return prev_kline.close > prev_kline.open and kline.close < kline.open and kline.close < prev_kline.open and kline.open > prev_kline.close

    def is_piercing_pattern(self, prev_kline, kline):
        return (
            prev_kline.close < prev_kline.open and self.is_bullish(kline) and kline.open < prev_kline.close and kline.close > (prev_kline.open + prev_kline.close) / 2
        )

    def is_dark_cloud_cover(self, prev_kline, kline):
        return (
            prev_kline.close > prev_kline.open and self.is_bearish(kline) and kline.open > prev_kline.close and kline.close < (prev_kline.open + prev_kline.close) / 2
        )

    def is_three_white_soldiers(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bullish(kline)
            and prev1_kline.close > prev1_kline.open
            and prev2_kline.close > prev2_kline.open
            and kline.open > prev1_kline.close
            and prev1_kline.open > prev2_kline.close
        )

    def is_three_black_crows(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bearish(kline)
            and prev1_kline.close < prev1_kline.open
            and prev2_kline.close < prev2_kline.open
            and kline.open < prev1_kline.close
            and prev1_kline.open < prev2_kline.close
        )

    def is_tweezer_top(self, prev_kline, kline):
        return kline.high == prev_kline.high and self.is_bearish(kline)

    def is_tweezer_bottom(self, prev_kline, kline):
        return kline.low == prev_kline.low and self.is_bullish(kline)

    def is_three_line_strike(self, prev1_kline, prev2_kline, prev3_kline, kline):
        if prev1_kline.close < prev1_kline.open and prev2_kline.close < prev2_kline.open and prev3_kline.close < prev3_kline.open:
            return self.is_bullish(kline) and kline.close > prev3_kline.open
        elif prev1_kline.close > prev1_kline.open and prev2_kline.close > prev2_kline.open and prev3_kline.close > prev3_kline.open:
            return self.is_bearish(kline) and kline.close < prev3_kline.open
        return False

    def get_candlestick_type(self):
        if len(self._klines) < 1:
            return CandlestickType.UNKNOWN

        kline = self._klines[-1]

        # Single Candlestick Patterns
        if self.is_doji(kline):
            if self.is_dragonfly_doji(kline):
                return CandlestickType.DRAGONFLY_DOJI
            elif self.is_gravestone_doji(kline):
                return CandlestickType.GRAVESTONE_DOJI
            elif self.is_long_legged_doji(kline):
                return CandlestickType.LONG_LEGGED_DOJI
            return CandlestickType.DOJI
        elif self.is_hammer(kline):
            return CandlestickType.HAMMER
        elif self.is_inverted_hammer(kline):
            return CandlestickType.INVERTED_HAMMER
        elif self.is_shooting_star(kline):
            return CandlestickType.SHOOTING_STAR
        elif self.is_hanging_man(kline):
            return CandlestickType.HANGING_MAN
        elif self.is_marubozu(kline):
            return CandlestickType.MARUBOZU
        elif self.is_spinning_top(kline):
            return CandlestickType.SPINNING_TOP

        # Multi-Candlestick Patterns
        if len(self._klines) >= 2:
            prev_kline = self._klines[-2]
            if self.is_bullish_engulfing(prev_kline, kline):
                return CandlestickType.BULLISH_ENGULFING
            elif self.is_bearish_engulfing(prev_kline, kline):
                return CandlestickType.BEARISH_ENGULFING
            elif self.is_piercing_pattern(prev_kline, kline):
                return CandlestickType.PIERCING_PATTERN
            elif self.is_dark_cloud_cover(prev_kline, kline):
                return CandlestickType.DARK_CLOUD_COVER
            elif self.is_tweezer_top(prev_kline, kline):
                return CandlestickType.TWEEZER_TOP
            elif self.is_tweezer_bottom(prev_kline, kline):
                return CandlestickType.TWEEZER_BOTTOM

        if len(self._klines) >= 3:
            prev1_kline = self._klines[-2]
            prev2_kline = self._klines[-3]
            if self.is_three_white_soldiers(prev1_kline, prev2_kline, kline):
                return CandlestickType.THREE_WHITE_SOLDIERS
            elif self.is_three_black_crows(prev1_kline, prev2_kline, kline):
                return CandlestickType.THREE_BLACK_CROWS

        if len(self._klines) >= 4:
            prev1_kline = self._klines[-2]
            prev2_kline = self._klines[-3]
            prev3_kline = self._klines[-4]
            if self.is_three_line_strike(prev1_kline, prev2_kline, prev3_kline, kline):
                return CandlestickType.THREE_LINE_STRIKE

        # Unknown Type
        return CandlestickType.UNKNOWN
