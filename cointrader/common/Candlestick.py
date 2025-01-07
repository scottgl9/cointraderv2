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
    BULLISH_MARUBOZU = 9
    BEARISH_MARUBOZU = 10
    SPINNING_TOP = 11
    BULLISH_ENGULFING = 12
    BEARISH_ENGULFING = 13
    PIERCING_PATTERN = 14
    DARK_CLOUD_COVER = 15
    THREE_WHITE_SOLDIERS = 16
    THREE_BLACK_CROWS = 17
    THREE_LINE_STRIKE = 18
    TWEEZER_TOP = 19
    TWEEZER_BOTTOM = 20
    MORNING_STAR = 21
    EVENING_STAR = 22
    RISING_THREE_METHODS = 23
    FALLING_THREE_METHODS = 24
    BULLISH_HARAMI = 25
    BEARISH_HARAMI = 26
    ABANDONED_BABY = 27
    UPSIDE_TASUKI_GAP = 28
    DOWNSIDE_TASUKI_GAP = 29
    THREE_INSIDE_UP = 30
    THREE_INSIDE_DOWN = 31
    BULLISH_TRI_STAR = 32
    BEARISH_TRI_STAR = 33
    TOWER_BOTTOM = 34
    TOWER_TOP = 35
    KICKER = 36
    BULLISH_HARAMI_CROSS = 37
    BEARISH_HARAMI_CROSS = 38
    BULLISH_BELT_HOLD = 39
    BEARISH_BELT_HOLD = 40
    STICK_SANDWICH = 41
    MATCHING_LOW = 42
    MATCHING_HIGH = 43
    HIGH_WAVE = 44
    UNKNOWN = 45

class CandlestickAnalyzer:
    def __init__(self, period=6):
        self._klines = deque(maxlen=period)
        self._period = period

    def reset(self):
        self._klines.clear()

    def ready(self):
        return len(self._klines) == self._period

    def update(self, kline: Kline):
        self._klines.append(kline.copy())

    def is_bullish(self, kline):
        return kline.close > kline.open

    def is_bearish(self, kline):
        return kline.open > kline.close

    def is_doji(self, kline):
        return abs(kline.open - kline.close) <= (kline.high - kline.low) * 0.1

    def is_dragonfly_doji(self, kline):
        return (
            self.is_doji(kline)
            and kline.high == max(kline.open, kline.close)
            and kline.low < min(kline.open, kline.close)
        )

    def is_gravestone_doji(self, kline):
        return (
            self.is_doji(kline)
            and kline.low == min(kline.open, kline.close)
            and kline.high > max(kline.open, kline.close)
        )

    def is_long_legged_doji(self, kline):
        return (
            self.is_doji(kline)
            and (kline.high - kline.low) > 2 * abs(kline.open - kline.close)
        )

    def is_spinning_top(self, kline):
        body = abs(kline.open - kline.close)
        shadows = kline.high - kline.low
        return body < shadows * 0.3

    def is_hammer(self, kline):
        body = abs(kline.open - kline.close)
        lower_shadow = (
            kline.open - kline.low if self.is_bullish(kline) else kline.close - kline.low
        )
        upper_shadow = (
            kline.high - kline.open if self.is_bullish(kline) else kline.high - kline.close
        )
        return (lower_shadow > 2 * body) and (upper_shadow < body)

    def is_inverted_hammer(self, kline):
        body = abs(kline.open - kline.close)
        lower_shadow = (
            kline.open - kline.low if self.is_bullish(kline) else kline.close - kline.low
        )
        upper_shadow = (
            kline.high - kline.open if self.is_bullish(kline) else kline.high - kline.close
        )
        return (upper_shadow > 2 * body) and (lower_shadow < body)

    def is_shooting_star(self, kline):
        return self.is_inverted_hammer(kline) and self.is_bearish(kline)

    def is_hanging_man(self, kline):
        return self.is_hammer(kline) and self.is_bearish(kline)

    def is_bullish_marubozu(self, kline):
        candle_range = kline.high - kline.low
        if candle_range == 0:
            return False

        # Real body is (close - open)
        body = kline.close - kline.open
        upper_wick = kline.high - kline.close
        lower_wick = kline.open - kline.low

        # Suppose “minimal” wicks means each wick <= 5% of total range.
        wick_threshold = 0.05 * candle_range

        return (
            self.is_bullish(kline) and
            (lower_wick <= wick_threshold) and
            (upper_wick <= wick_threshold) and
            # body must be a large chunk of the total range
            (body >= 0.9 * candle_range)  # e.g., 90% or more
        )

    def is_bearish_marubozu(self, kline):
        candle_range = kline.high - kline.low
        if candle_range == 0:
            return False

        # Real body is (open - close) if bearish
        body = kline.open - kline.close
        upper_wick = kline.high - kline.open
        lower_wick = kline.close - kline.low

        wick_threshold = 0.05 * candle_range

        return (
            self.is_bearish(kline) and
            (lower_wick <= wick_threshold) and
            (upper_wick <= wick_threshold) and
            (body >= 0.9 * candle_range)
        )

    def is_bullish_engulfing(self, prev_kline, kline):
        return (
            prev_kline.close < prev_kline.open
            and kline.close > kline.open
            and kline.close > prev_kline.open
            and kline.open < prev_kline.close
        )

    def is_bearish_engulfing(self, prev_kline, kline):
        return (
            prev_kline.close > prev_kline.open
            and kline.close < kline.open
            and kline.close < prev_kline.open
            and kline.open > prev_kline.close
        )

    def is_piercing_pattern(self, prev_kline, kline):
        return (
            prev_kline.close < prev_kline.open
            and self.is_bullish(kline)
            and (kline.open < prev_kline.close)
            and (kline.close > (prev_kline.open + prev_kline.close) / 2)
        )

    def is_dark_cloud_cover(self, prev_kline, kline):
        return (
            prev_kline.close > prev_kline.open
            and self.is_bearish(kline)
            and (kline.open > prev_kline.close)
            and (kline.close < (prev_kline.open + prev_kline.close) / 2)
        )

    def is_three_white_soldiers(self, prev2_kline, prev1_kline, kline):
        """
        Checks for Three White Soldiers pattern using the classic definition:
        
        - Candle #1 (prev2_kline) is bullish.
        - Candle #2 (prev1_kline) is bullish and opens within Candle #1's real body,
          and closes higher than Candle #1's close.
        - Candle #3 (kline) is bullish and opens within Candle #2's real body,
          and closes higher than Candle #2's close.
        """
        if not (
            self.is_bullish(prev2_kline)
            and self.is_bullish(prev1_kline)
            and self.is_bullish(kline)
        ):
            return False

        # Candle #2 opens within Candle #1's body (between Candle #1's open & close)
        if not (prev2_kline.open <= prev1_kline.open <= prev2_kline.close):
            return False

        # Candle #2 closes above Candle #1's close
        if not (prev1_kline.close > prev2_kline.close):
            return False

        # Candle #3 opens within Candle #2's body
        if not (prev1_kline.open <= kline.open <= prev1_kline.close):
            return False

        # Candle #3 closes above Candle #2's close
        if not (kline.close > prev1_kline.close):
            return False

        # Optional: short upper shadow on the 3rd candle
        upper_shadow = kline.high - kline.close
        body = kline.close - kline.open
        if upper_shadow > body * 0.5:
            return False

        return True

    def is_three_black_crows(self, prev2_kline, prev1_kline, kline):
        """
        Three Black Crows (classic definition):
          1) Candle #1 (prev2_kline) is bearish.
          2) Candle #2 (prev1_kline) is bearish and opens within Candle #1's real body,
             then closes below Candle #1's close.
          3) Candle #3 (kline) is bearish and opens within Candle #2's real body,
             then closes below Candle #2's close.
          (Optional) short lower shadows.
        """
        if not (
            self.is_bearish(prev2_kline)
            and self.is_bearish(prev1_kline)
            and self.is_bearish(kline)
        ):
            return False

        # Candle #2 opens within Candle #1's real body ([close, open] for bearish #1)
        if not (prev2_kline.close <= prev1_kline.open <= prev2_kline.open):
            return False

        # Candle #2 closes below Candle #1's close
        if not (prev1_kline.close < prev2_kline.close):
            return False

        # Candle #3 opens within Candle #2's real body
        if not (prev1_kline.close <= kline.open <= prev1_kline.open):
            return False

        # Candle #3 closes below Candle #2's close
        if not (kline.close < prev1_kline.close):
            return False

        # Optional: short lower shadow on Candle #3
        lower_shadow = kline.close - kline.low
        body = kline.open - kline.close
        if lower_shadow > 0.5 * body:
            return False

        return True

    def is_tweezer_top(self, prev_kline, kline):
        return (kline.high == prev_kline.high) and self.is_bearish(kline)

    def is_tweezer_bottom(self, prev_kline, kline):
        return (kline.low == prev_kline.low) and self.is_bullish(kline)

    def is_three_line_strike(self, prev1_kline, prev2_kline, prev3_kline, kline):
        # Bearish run, then a bullish strike?
        if (
            prev1_kline.close < prev1_kline.open
            and prev2_kline.close < prev2_kline.open
            and prev3_kline.close < prev3_kline.open
        ):
            return self.is_bullish(kline) and (kline.close > prev3_kline.open)
        # Bullish run, then a bearish strike?
        elif (
            prev1_kline.close > prev1_kline.open
            and prev2_kline.close > prev2_kline.open
            and prev3_kline.close > prev3_kline.open
        ):
            return self.is_bearish(kline) and (kline.close < prev3_kline.open)
        return False

    def is_bullish_harami(self, prev_kline, kline):
        return (
            self.is_bearish(prev_kline)
            and self.is_bullish(kline)
            and (kline.open > prev_kline.close)
            and (kline.close < prev_kline.open)
        )

    def is_bearish_harami(self, prev_kline, kline):
        return (
            self.is_bullish(prev_kline)
            and self.is_bearish(kline)
            and (kline.open < prev_kline.close)
            and (kline.close > prev_kline.open)
        )

    def is_bullish_harami_cross(self, prev_kline, kline):
        """
        Bullish Harami Cross pattern:
          1) The first candle is bearish.
          2) The second candle is a doji.
          3) That doji is fully inside the first candle's real body.
        """
        if not self.is_bearish(prev_kline):
            return False
        if not self.is_doji(kline):
            return False
        # Bearish body range is [close, open]
        if not (prev_kline.close < kline.open < prev_kline.open):
            return False
        return True

    def is_bearish_harami_cross(self, prev_kline, kline):
        """
        Bearish Harami Cross pattern:
          1) The first candle is bullish.
          2) The second candle is a doji.
          3) That doji is fully inside the first candle's real body.
        """
        if not self.is_bullish(prev_kline):
            return False
        if not self.is_doji(kline):
            return False
        # Bullish body range is [open, close]
        if not (prev_kline.open < kline.open < prev_kline.close):
            return False
        return True

    def is_morning_star(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bearish(prev1_kline)
            and self.is_doji(prev2_kline)
            and self.is_bullish(kline)
            and (kline.close > (prev1_kline.close + prev1_kline.open) / 2)
        )

    def is_evening_star(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bullish(prev1_kline)
            and self.is_doji(prev2_kline)
            and self.is_bearish(kline)
            and (kline.close < (prev1_kline.close + prev1_kline.open) / 2)
        )

    def is_abandoned_baby(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bearish(prev1_kline)
            and self.is_doji(prev2_kline)
            and self.is_bullish(kline)
            and (prev2_kline.low > prev1_kline.close)
            and (prev2_kline.low > kline.open)
        )

    def is_rising_three_methods(self, prev1_kline, prev2_kline, prev3_kline, kline):
        return (
            self.is_bullish(prev1_kline)
            and self.is_bearish(prev2_kline)
            and self.is_bearish(prev3_kline)
            and (prev3_kline.close > prev1_kline.open)
            and self.is_bullish(kline)
            and (kline.close > prev1_kline.close)
        )

    def is_falling_three_methods(self, prev1_kline, prev2_kline, prev3_kline, kline):
        return (
            self.is_bearish(prev1_kline)
            and self.is_bullish(prev2_kline)
            and self.is_bullish(prev3_kline)
            and (prev3_kline.close < prev1_kline.open)
            and self.is_bearish(kline)
            and (kline.close < prev1_kline.close)
        )

    def is_upside_tasuki_gap(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bullish(prev1_kline)
            and self.is_bullish(prev2_kline)
            and (prev2_kline.open > prev1_kline.close)
            and self.is_bearish(kline)
            and (kline.close > prev1_kline.close)
        )

    def is_downside_tasuki_gap(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bearish(prev1_kline)
            and self.is_bearish(prev2_kline)
            and (prev2_kline.open < prev1_kline.close)
            and self.is_bullish(kline)
            and (kline.close < prev1_kline.close)
        )

    def is_three_inside_up(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bearish(prev1_kline)
            and self.is_bullish(prev2_kline)
            and (prev2_kline.open > kline.low)
            and (prev2_kline.close < prev1_kline.open)
            and self.is_bullish(kline)
            and (kline.close > prev1_kline.high)
        )

    def is_three_inside_down(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_bullish(prev1_kline)
            and self.is_bearish(prev2_kline)
            and (prev2_kline.open < prev1_kline.close)
            and (prev2_kline.close > prev1_kline.open)
            and self.is_bearish(kline)
            and (kline.close < prev1_kline.low)
        )

    def is_bullish_tri_star(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_doji(prev1_kline)
            and self.is_doji(prev2_kline)
            and self.is_doji(kline)
            and (prev2_kline.low < prev1_kline.low)
            and (prev2_kline.low < kline.low)
        )

    def is_bearish_tri_star(self, prev1_kline, prev2_kline, kline):
        return (
            self.is_doji(prev1_kline)
            and self.is_doji(prev2_kline)
            and self.is_doji(kline)
            and (prev2_kline.high > prev1_kline.high)
            and (prev2_kline.high > kline.high)
        )

    def is_tower_bottom(self):
        if len(self._klines) < 6:
            return False
        bearish_candles = all(self.is_bearish(k) for k in self._klines[:3])
        bullish_candles = all(self.is_bullish(k) for k in self._klines[3:])
        return bearish_candles and bullish_candles

    def is_tower_top(self):
        if len(self._klines) < 6:
            return False
        bullish_candles = all(self.is_bullish(k) for k in self._klines[:3])
        bearish_candles = all(self.is_bearish(k) for k in self._klines[3:])
        return bullish_candles and bearish_candles

    def is_kicker(self, prev_kline, kline):
        if self.is_bearish(prev_kline) and self.is_bullish(kline):
            return kline.open > prev_kline.high
        elif self.is_bullish(prev_kline) and self.is_bearish(kline):
            return kline.open < prev_kline.low
        return False

    def is_bullish_belt_hold(self, kline):
        """
        Bullish Belt Hold (single candle)
        Common definition:
          1) Candle is bullish (close > open).
          2) The open is very close to the low (little/no lower shadow).
          3) The candle has a relatively large body compared to its total range.
        """
        if not self.is_bullish(kline):
            return False

        candle_range = kline.high - kline.low
        if candle_range == 0:
            return False

        body = kline.close - kline.open
        lower_shadow = kline.open - kline.low

        near_low = (lower_shadow <= 0.1 * candle_range)   # e.g. <= 10% of total range
        large_body = (body >= 0.6 * candle_range)         # body >= 60% of total range
        return near_low and large_body

    def is_bearish_belt_hold(self, kline):
        """
        Bearish Belt Hold (single candle)
        Common definition:
          1) Candle is bearish (open > close).
          2) The open is very close to the high (little/no upper shadow).
          3) The candle has a relatively large body compared to its total range.
        """
        if not self.is_bearish(kline):
            return False

        candle_range = kline.high - kline.low
        if candle_range == 0:
            return False

        body = kline.open - kline.close
        upper_shadow = kline.high - kline.open

        near_high = (upper_shadow <= 0.1 * candle_range)
        large_body = (body >= 0.6 * candle_range)
        return near_high and large_body

    def is_stick_sandwich(self, prev2_kline, prev1_kline, kline):
        """
        Stick Sandwich (3-candle pattern)
          1) Candle #1 (prev2_kline) is bearish.
          2) Candle #2 (prev1_kline) is bullish and closes above Candle #1's close.
          3) Candle #3 (kline) is bearish and closes exactly at Candle #1's close.
        """
        # Candle #1: Bearish
        if not self.is_bearish(prev2_kline):
            return False

        # Candle #2: Bullish, closes above Candle #1’s close
        if not self.is_bullish(prev1_kline):
            return False
        if not (prev1_kline.close > prev2_kline.close):
            return False

        # Candle #3: Bearish, closes at the same price as Candle #1’s close
        if not self.is_bearish(kline):
            return False

        # Exact match or within a small tolerance
        return abs(kline.close - prev2_kline.close) < 1e-8

    def is_matching_low(self, prev_kline, kline):
        """
        Matching Low (2-candle pattern)
          1) Candle #1 is bearish.
          2) Candle #2 is also bearish (or optionally could be bullish).
          3) Both candles share the same close.
        """
        if not self.is_bearish(prev_kline):
            return False
        if not self.is_bearish(kline):
            return False
        return abs(kline.close - prev_kline.close) < 1e-8

    def is_matching_high(self, prev_kline, kline):
        """
        Matching High (2-candle pattern)
          1) Candle #1 is bullish.
          2) Candle #2 is also bullish (or optionally could be bearish).
          3) Both candles share the same close.
        """
        if not self.is_bullish(prev_kline):
            return False
        if not self.is_bullish(kline):
            return False
        return abs(kline.close - prev_kline.close) < 1e-8

    def is_high_wave(self, kline):
        """
        High Wave (single candle)
          1) Very small real body relative to total range.
          2) Very long upper and lower shadows, each at least as large as the body.
        """
        candle_range = kline.high - kline.low
        if candle_range == 0:
            return False

        body = abs(kline.close - kline.open)
        upper_shadow = kline.high - max(kline.open, kline.close)
        lower_shadow = min(kline.open, kline.close) - kline.low

        small_body = (body <= 0.3 * candle_range)
        long_upper = (upper_shadow >= body)
        long_lower = (lower_shadow >= body)
        return small_body and long_upper and long_lower

    def get_candlestick_type(self):
        if len(self._klines) < 1:
            return CandlestickType.UNKNOWN

        kline = self._klines[-1]

        # ---------- 6-Candle Patterns ----------
        if len(self._klines) >= 6:
            if self.is_tower_bottom():
                return CandlestickType.TOWER_BOTTOM
            elif self.is_tower_top():
                return CandlestickType.TOWER_TOP

        # ---------- 4-Candle Patterns ----------
        if len(self._klines) >= 4:
            prev1_kline = self._klines[-2]
            prev2_kline = self._klines[-3]
            prev3_kline = self._klines[-4]

            if self.is_three_line_strike(prev1_kline, prev2_kline, prev3_kline, kline):
                return CandlestickType.THREE_LINE_STRIKE
            elif self.is_abandoned_baby(prev1_kline, prev2_kline, kline):
                return CandlestickType.ABANDONED_BABY

        # ---------- 3-Candle Patterns ----------
        if len(self._klines) >= 3:
            prev1_kline = self._klines[-2]
            prev2_kline = self._klines[-3]

            # Notice we pass (prev2, prev1, kline) to match the docstrings.
            if self.is_three_white_soldiers(prev2_kline, prev1_kline, kline):
                return CandlestickType.THREE_WHITE_SOLDIERS
            elif self.is_three_black_crows(prev2_kline, prev1_kline, kline):
                return CandlestickType.THREE_BLACK_CROWS
            elif self.is_morning_star(prev1_kline, prev2_kline, kline):
                return CandlestickType.MORNING_STAR
            elif self.is_evening_star(prev1_kline, prev2_kline, kline):
                return CandlestickType.EVENING_STAR
            elif self.is_rising_three_methods(prev1_kline, prev2_kline, kline):
                return CandlestickType.RISING_THREE_METHODS
            elif self.is_falling_three_methods(prev1_kline, prev2_kline, kline):
                return CandlestickType.FALLING_THREE_METHODS
            elif self.is_three_inside_up(prev1_kline, prev2_kline, kline):
                return CandlestickType.THREE_INSIDE_UP
            elif self.is_three_inside_down(prev1_kline, prev2_kline, kline):
                return CandlestickType.THREE_INSIDE_DOWN
            elif self.is_bullish_tri_star(prev1_kline, prev2_kline, kline):
                return CandlestickType.BULLISH_TRI_STAR
            elif self.is_bearish_tri_star(prev1_kline, prev2_kline, kline):
                return CandlestickType.BEARISH_TRI_STAR
            elif self.is_stick_sandwich(prev2_kline, prev1_kline, kline):
                return CandlestickType.STICK_SANDWICH
            elif self.is_upside_tasuki_gap(prev2_kline, prev1_kline, kline):
                return CandlestickType.UPSIDE_TASUKI_GAP
            elif self.is_downside_tasuki_gap(prev2_kline, prev1_kline, kline):
                return CandlestickType.DOWNSIDE_TASUKI_GAP

        # ---------- 2-Candle Patterns ----------
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
            elif self.is_bullish_harami(prev_kline, kline):
                return CandlestickType.BULLISH_HARAMI
            elif self.is_bearish_harami(prev_kline, kline):
                return CandlestickType.BEARISH_HARAMI
            elif self.is_kicker(prev_kline, kline):
                return CandlestickType.KICKER
            elif self.is_bullish_harami_cross(prev_kline, kline):
                return CandlestickType.BULLISH_HARAMI_CROSS
            elif self.is_bearish_harami_cross(prev_kline, kline):
                return CandlestickType.BEARISH_HARAMI_CROSS
            elif self.is_matching_low(prev_kline, kline):
                return CandlestickType.MATCHING_LOW
            elif self.is_matching_high(prev_kline, kline):
                return CandlestickType.MATCHING_HIGH

        # ---------- Single-Candle Patterns ----------
        if self.is_high_wave(kline):
            return CandlestickType.HIGH_WAVE
        elif self.is_doji(kline):
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
        elif self.is_bullish_marubozu(kline):
            return CandlestickType.BULLISH_MARUBOZU
        elif self.is_bearish_marubozu(kline):
            return CandlestickType.BEARISH_MARUBOZU
        elif self.is_spinning_top(kline):
            return CandlestickType.SPINNING_TOP
        elif self.is_bullish_belt_hold(kline):
            return CandlestickType.BULLISH_BELT_HOLD
        elif self.is_bearish_belt_hold(kline):
            return CandlestickType.BEARISH_BELT_HOLD

        # Unknown Type
        return CandlestickType.UNKNOWN
