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
    BULLISH_ABANDONED_BABY = 45
    BEARISH_ABANDONED_BABY = 46
    UNKNOWN = 47

class CandlestickBias(Enum):
    UNKNOWN = 0
    BULLISH = 1
    BEARISH = 2
    NEUTRAL = 3

class CandlestickCategory(Enum):
    UNKNOWN= 0
    REVERSAL = 1
    CONTINUATION = 2
    INDECISION = 3
    BREAKOUT = 4

class CandlestickClassification:
    def __init__(self):
        self.pattern_classification = {
            CandlestickType.DRAGONFLY_DOJI: {
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.GRAVESTONE_DOJI: {
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.LONG_LEGGED_DOJI: {
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.INDECISION
            },
            CandlestickType.DOJI: {
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.INDECISION
            },
            CandlestickType.HAMMER: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.INVERTED_HAMMER: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.SHOOTING_STAR: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.HANGING_MAN: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BULLISH_MARUBOZU: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.BREAKOUT
            },
            CandlestickType.BEARISH_MARUBOZU: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.BREAKOUT
            },
            CandlestickType.SPINNING_TOP: {
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.INDECISION
            },
            CandlestickType.BULLISH_ENGULFING: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BEARISH_ENGULFING: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.PIERCING_PATTERN: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.DARK_CLOUD_COVER: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.THREE_WHITE_SOLDIERS: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.THREE_BLACK_CROWS: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.THREE_LINE_STRIKE: {
                # Could be bullish or bearish, but often considered a continuation pattern
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.TWEEZER_TOP: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.TWEEZER_BOTTOM: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.MORNING_STAR: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.EVENING_STAR: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.RISING_THREE_METHODS: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.FALLING_THREE_METHODS: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.BULLISH_HARAMI: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BEARISH_HARAMI: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BULLISH_ABANDONED_BABY: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BEARISH_ABANDONED_BABY: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.UPSIDE_TASUKI_GAP: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.DOWNSIDE_TASUKI_GAP: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.CONTINUATION
            },
            CandlestickType.THREE_INSIDE_UP: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.THREE_INSIDE_DOWN: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BULLISH_TRI_STAR: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BEARISH_TRI_STAR: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.TOWER_BOTTOM: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.TOWER_TOP: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.KICKER: {
                # Often a large bullish or bearish shift; commonly seen as breakout
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.BREAKOUT
            },
            CandlestickType.BULLISH_HARAMI_CROSS: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BEARISH_HARAMI_CROSS: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BULLISH_BELT_HOLD: {
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.BEARISH_BELT_HOLD: {
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.STICK_SANDWICH: {
                # Typically interpreted as bullish reversal
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.MATCHING_LOW: {
                # Suggests bullish support
                "bias": CandlestickBias.BULLISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.MATCHING_HIGH: {
                # Suggests bearish resistance
                "bias": CandlestickBias.BEARISH,
                "category": CandlestickCategory.REVERSAL
            },
            CandlestickType.HIGH_WAVE: {
                "bias": CandlestickBias.NEUTRAL,
                "category": CandlestickCategory.INDECISION
            },
            CandlestickType.UNKNOWN: {
                "bias": CandlestickBias.UNKNOWN,
                "category": CandlestickCategory.UNKNOWN
            }
        }

    def classify(self, candlestick_type: CandlestickType):
        return self.pattern_classification.get(candlestick_type, {
            "bias": CandlestickBias.UNKNOWN,
            "category": CandlestickCategory.UNKNOWN
        })

class CandlestickAnalyzer:
    def __init__(self, period=6):
        self._klines = deque(maxlen=period)
        self._period = period
        self._classifier = CandlestickClassification()

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

    def has_small_body(self, kline, threshold=0.2):
        """Return True if this candle has a body <= threshold * (high-low)."""
        candle_range = kline.high - kline.low
        if candle_range <= 0:
            return False
        body = abs(kline.close - kline.open)
        return (body <= threshold * candle_range)

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

    def is_three_white_soldiers(
        self, prev2_kline, prev1_kline, kline, overlap_threshold=0.05
    ):
        """
        Relaxed Three White Soldiers:
        1) All three candles bullish.
        2) Each candle opens within the previous candle's body +/- overlap_threshold.
        3) Each candle closes above the previous candle's close.
        4) (Optional) short upper shadow on the last candle.

        overlap_threshold = 0.05 allows up to 5% “outside” the prior candle’s body
        if you want partial overlap.
        """

        # 1) All three must be bullish
        if not (self.is_bullish(prev2_kline) and self.is_bullish(prev1_kline) and self.is_bullish(kline)):
            return False

        # The body range for Candle #1 is [min(open, close), max(open, close)] = [prev2_kline.open, prev2_kline.close]
        body1_low = min(prev2_kline.open, prev2_kline.close)
        body1_high = max(prev2_kline.open, prev2_kline.close)
        body1_range = body1_high - body1_low

        # 2) Candle #2 opens within Candle #1's body ± overlap_threshold
        #    meaning: open2 is within [body1_low - threshold, body1_high + threshold]
        relaxed_low = body1_low - body1_range * overlap_threshold
        relaxed_high = body1_high + body1_range * overlap_threshold

        if not (relaxed_low <= prev1_kline.open <= relaxed_high):
            return False

        # Candle #2 closes above Candle #1's close
        if not (prev1_kline.close > prev2_kline.close):
            return False

        # Repeat for Candle #3 relative to Candle #2
        body2_low = min(prev1_kline.open, prev1_kline.close)
        body2_high = max(prev1_kline.open, prev1_kline.close)
        body2_range = body2_high - body2_low

        relaxed_low2 = body2_low - body2_range * overlap_threshold
        relaxed_high2 = body2_high + body2_range * overlap_threshold

        if not (relaxed_low2 <= kline.open <= relaxed_high2):
            return False

        # Candle #3 closes above Candle #2's close
        if not (kline.close > prev1_kline.close):
            return False

        # Optional: short upper shadow on Candle #3
        upper_shadow = kline.high - kline.close
        body = kline.close - kline.open
        if upper_shadow > body * 0.5:
            return False

        return True

    def is_three_black_crows(
        self, prev2_kline, prev1_kline, kline, overlap_threshold=0.05
    ):
        """
        Relaxed Three Black Crows:
        1) All three candles bearish.
        2) Each candle opens within the previous candle's body ± overlap_threshold.
        3) Each candle closes below the previous candle's close.
        4) (Optional) short lower shadow on the last candle.
        """

        # 1) All three must be bearish
        if not (self.is_bearish(prev2_kline) and self.is_bearish(prev1_kline) and self.is_bearish(kline)):
            return False

        # Candle #1's body
        body1_low = min(prev2_kline.close, prev2_kline.open)
        body1_high = max(prev2_kline.close, prev2_kline.open)
        body1_range = body1_high - body1_low

        relaxed_low = body1_low - body1_range * overlap_threshold
        relaxed_high = body1_high + body1_range * overlap_threshold

        # Candle #2 opens within Candle #1's body ± threshold
        if not (relaxed_low <= prev1_kline.open <= relaxed_high):
            return False

        # Candle #2 closes below Candle #1's close
        if not (prev1_kline.close < prev2_kline.close):
            return False

        # Candle #2's body
        body2_low = min(prev1_kline.close, prev1_kline.open)
        body2_high = max(prev1_kline.close, prev1_kline.open)
        body2_range = body2_high - body2_low

        relaxed_low2 = body2_low - body2_range * overlap_threshold
        relaxed_high2 = body2_high + body2_range * overlap_threshold

        # Candle #3 opens within Candle #2's body ± threshold
        if not (relaxed_low2 <= kline.open <= relaxed_high2):
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
        """
        Relaxed Morning Star:
        1) First candle is bearish.
        2) Second candle has a 'small body' (not necessarily a doji).
        3) Third candle is bullish and closes above halfway into candle #1's body.
        """
        # 1) First candle is bearish
        if not self.is_bearish(prev1_kline):
            return False

        # 2) Second candle has a small real body
        if not self.has_small_body(prev2_kline, threshold=0.2):
            return False

        # 3) Third candle is bullish
        if not self.is_bullish(kline):
            return False

        # Closes above the midpoint of Candle #1's body
        midpoint_1 = (prev1_kline.close + prev1_kline.open) / 2.0
        return (kline.close > midpoint_1)

    def is_evening_star(self, prev1_kline, prev2_kline, kline):
        """
        Relaxed Evening Star:
        1) First candle is bullish.
        2) Second candle has a 'small body'.
        3) Third candle is bearish and closes below halfway into candle #1's body.
        """
        if not self.is_bullish(prev1_kline):
            return False
        if not self.has_small_body(prev2_kline, threshold=0.2):
            return False
        if not self.is_bearish(kline):
            return False

        midpoint_1 = (prev1_kline.close + prev1_kline.open) / 2.0
        return (kline.close < midpoint_1)


    def is_bullish_abandoned_baby(self, prev_kline, doji_kline, kline, gap_threshold=0.003):
        """
        Bullish Abandoned Baby pattern (crypto-friendly):
        1) First candle is strongly bearish.
        2) Second candle is a doji that is "abandoned" below (gaps down).
        3) Third candle is strongly bullish, "gapping up" from the doji.
        gap_threshold is a float e.g. 0.003 => 0.3%
        """
        # 1) Must be bearish
        if not self.is_bearish(prev_kline):
            return False

        # 2) Must be doji
        if not self.is_doji(doji_kline):
            return False

        # Check "gap down" by percentage
        # doji_kline.high < prev_kline.close * (1 - gap_threshold)
        if not (doji_kline.high < prev_kline.close * (1 - gap_threshold)):
            return False

        # 3) Third candle is bullish
        if not self.is_bullish(kline):
            return False

        # Check "gap up" by percentage
        # doji_kline.low > kline.open * (1 + gap_threshold)
        if not (doji_kline.low > kline.open * (1 + gap_threshold)):
            return False

        return True


    def is_bearish_abandoned_baby(self, prev_kline, doji_kline, kline, gap_threshold=0.003):
        """
        Bearish Abandoned Baby pattern (crypto-friendly):
        1) First candle is strongly bullish.
        2) Second candle is a doji that is "abandoned" above.
        3) Third candle is strongly bearish, "gapping down" from the doji.
        """
        if not self.is_bullish(prev_kline):
            return False
        if not self.is_doji(doji_kline):
            return False

        # Gap up: doji_kline.low > prev_kline.close * (1 + gap_threshold)
        if not (doji_kline.low > prev_kline.close * (1 + gap_threshold)):
            return False

        if not self.is_bearish(kline):
            return False

        # Gap down: doji_kline.high < kline.open * (1 - gap_threshold)
        if not (doji_kline.high < kline.open * (1 - gap_threshold)):
            return False

        return True


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

    def is_upside_tasuki_gap(self, prev1_kline, prev2_kline, kline, gap_threshold=0.003):
        """
        Upside Tasuki Gap (crypto-friendly):
        1) Candle #1 and Candle #2 both bullish.
        2) Candle #2 'opens' above Candle #1's close by gap_threshold% or more.
        3) Candle #3 is bearish but does not fully close the gap (closes above Candle #1's close).
        """
        if not (self.is_bullish(prev1_kline) and self.is_bullish(prev2_kline)):
            return False

        # Gap up: prev2_kline.open >= prev1_kline.close * (1 + gap_threshold)
        if not (prev2_kline.open >= prev1_kline.close * (1 + gap_threshold)):
            return False

        if not self.is_bearish(kline):
            return False

        # Partial fill: kline.close > prev1_kline.close
        return (kline.close > prev1_kline.close)

    def is_downside_tasuki_gap(self, prev1_kline, prev2_kline, kline, gap_threshold=0.003):
        """
        Downside Tasuki Gap (crypto-friendly):
        1) Candle #1 and Candle #2 both bearish.
        2) Candle #2 opens below Candle #1's close by gap_threshold% or more.
        3) Candle #3 is bullish but does not fully close the gap (closes below Candle #1's close).
        """
        if not (self.is_bearish(prev1_kline) and self.is_bearish(prev2_kline)):
            return False

        # Gap down: prev2_kline.open <= prev1_kline.close * (1 - gap_threshold)
        if not (prev2_kline.open <= prev1_kline.close * (1 - gap_threshold)):
            return False

        if not self.is_bullish(kline):
            return False

        # Partial fill: kline.close < prev1_kline.close
        return (kline.close < prev1_kline.close)

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

    def is_kicker(self, prev_kline, kline, gap_threshold=0.003):
        """
        Kicker (crypto-friendly):
        - If previous candle is bearish, next candle is bullish with open 
            at least gap_threshold% above prev_kline.high.
        - If previous candle is bullish, next candle is bearish with open 
            at least gap_threshold% below prev_kline.low.
        """
        if self.is_bearish(prev_kline) and self.is_bullish(kline):
            # Instead of kline.open > prev_kline.high, do:
            return kline.open >= prev_kline.high * (1 + gap_threshold)

        elif self.is_bullish(prev_kline) and self.is_bearish(kline):
            # Instead of kline.open < prev_kline.low, do:
            return kline.open <= prev_kline.low * (1 - gap_threshold)

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
        return abs(kline.close - prev2_kline.close) < 1e-6

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
        return abs(kline.close - prev_kline.close) < 1e-6

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
        return abs(kline.close - prev_kline.close) < 1e-6

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
            elif self.is_bullish_abandoned_baby(prev1_kline, prev2_kline, kline):
                return CandlestickType.BULLISH_ABANDONED_BABY
            elif self.is_bearish_abandoned_baby(prev1_kline, prev2_kline, kline):
                return CandlestickType.BEARISH_ABANDONED_BABY

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
        if self.is_doji(kline):
            if self.is_dragonfly_doji(kline):
                return CandlestickType.DRAGONFLY_DOJI
            elif self.is_gravestone_doji(kline):
                return CandlestickType.GRAVESTONE_DOJI
            elif self.is_long_legged_doji(kline):
                return CandlestickType.LONG_LEGGED_DOJI
            return CandlestickType.DOJI
        elif self.is_high_wave(kline):
            return CandlestickType.HIGH_WAVE
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
    
    def get_candlestick_info(self, type: CandlestickType):
        return self._classifier.classify(type)
