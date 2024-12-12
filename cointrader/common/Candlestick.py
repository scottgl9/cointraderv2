class CandlestickAnalyzer:
    def __init__(self, open_price, close_price, high_price, low_price):
        self.open = open_price
        self.close = close_price
        self.high = high_price
        self.low = low_price

    def is_bullish(self):
        return self.close > self.open

    def is_bearish(self):
        return self.open > self.close

    def is_doji(self):
        return abs(self.open - self.close) <= (self.high - self.low) * 0.1

    def is_dragonfly_doji(self):
        return self.is_doji() and self.high == max(self.open, self.close) and self.low < min(self.open, self.close)

    def is_gravestone_doji(self):
        return self.is_doji() and self.low == min(self.open, self.close) and self.high > max(self.open, self.close)

    def is_long_legged_doji(self):
        return self.is_doji() and self.high - self.low > 2 * abs(self.open - self.close)

    def is_spinning_top(self):
        body = abs(self.open - self.close)
        shadows = self.high - self.low
        return body < shadows * 0.3

    def is_hammer(self):
        body = abs(self.open - self.close)
        lower_shadow = self.open - self.low if self.is_bullish() else self.close - self.low
        upper_shadow = self.high - self.open if self.is_bullish() else self.high - self.close
        return lower_shadow > 2 * body and upper_shadow < body

    def is_inverted_hammer(self):
        body = abs(self.open - self.close)
        lower_shadow = self.open - self.low if self.is_bullish() else self.close - self.low
        upper_shadow = self.high - self.open if self.is_bullish() else self.high - self.close
        return upper_shadow > 2 * body and lower_shadow < body

    def is_shooting_star(self):
        return self.is_inverted_hammer() and self.is_bearish()

    def is_hanging_man(self):
        return self.is_hammer() and self.is_bearish()

    def is_marubozu(self):
        return self.open == self.low or self.close == self.high

    def is_bullish_engulfing(self, prev_open, prev_close):
        return prev_close < prev_open and self.close > self.open and self.close > prev_open and self.open < prev_close

    def is_bearish_engulfing(self, prev_open, prev_close):
        return prev_close > prev_open and self.close < self.open and self.close < prev_open and self.open > prev_close

    def is_piercing_pattern(self, prev_open, prev_close):
        return (
            prev_close < prev_open and self.is_bullish() and self.open < prev_close and self.close > (prev_open + prev_close) / 2
        )

    def is_dark_cloud_cover(self, prev_open, prev_close):
        return (
            prev_close > prev_open and self.is_bearish() and self.open > prev_close and self.close < (prev_open + prev_close) / 2
        )

    def is_morning_star(self, prev_open, prev_close, next_open, next_close):
        return (
            prev_close < prev_open
            and self.is_doji()
            and next_close > next_open
            and next_close > prev_open
        )

    def is_evening_star(self, prev_open, prev_close, next_open, next_close):
        return (
            prev_close > prev_open
            and self.is_doji()
            and next_close < next_open
            and next_close < prev_open
        )

    def is_three_white_soldiers(self, prev1_open, prev1_close, prev2_open, prev2_close):
        return (
            self.is_bullish()
            and prev1_close > prev1_open
            and prev2_close > prev2_open
            and self.open > prev1_close
            and prev1_open > prev2_close
        )

    def is_three_black_crows(self, prev1_open, prev1_close, prev2_open, prev2_close):
        return (
            self.is_bearish()
            and prev1_close < prev1_open
            and prev2_close < prev2_open
            and self.open < prev1_close
            and prev1_open < prev2_close
        )

    def is_tweezer_top(self, prev_high):
        return self.high == prev_high and self.is_bearish()

    def is_tweezer_bottom(self, prev_low):
        return self.low == prev_low and self.is_bullish()

    def is_three_line_strike(self, prev1_open, prev1_close, prev2_open, prev2_close, prev3_open, prev3_close):
        if prev1_close < prev1_open and prev2_close < prev2_open and prev3_close < prev3_open:
            return self.is_bullish() and self.close > prev3_open
        elif prev1_close > prev1_open and prev2_close > prev2_open and prev3_close > prev3_open:
            return self.is_bearish() and self.close < prev3_open
        return False

    def get_candlestick_type(self, **kwargs):
        # Single Candlestick Patterns
        if self.is_doji():
            if self.is_dragonfly_doji():
                return "Dragonfly Doji"
            elif self.is_gravestone_doji():
                return "Gravestone Doji"
            elif self.is_long_legged_doji():
                return "Long-Legged Doji"
            return "Doji"
        elif self.is_hammer():
            return "Hammer"
        elif self.is_inverted_hammer():
            return "Inverted Hammer"
        elif self.is_shooting_star():
            return "Shooting Star"
        elif self.is_hanging_man():
            return "Hanging Man"
        elif self.is_marubozu():
            return "Marubozu"
        elif self.is_spinning_top():
            return "Spinning Top"

        # Multi-Candlestick Patterns
        prev_open = kwargs.get("prev_open")
        prev_close = kwargs.get("prev_close")
        prev_high = kwargs.get("prev_high")
        prev_low = kwargs.get("prev_low")
        next_open = kwargs.get("next_open")
        next_close = kwargs.get("next_close")
        prev1_open = kwargs.get("prev1_open")
        prev1_close = kwargs.get("prev1_close")
        prev2_open = kwargs.get("prev2_open")
        prev2_close = kwargs.get("prev2_close")
        prev3_open = kwargs.get("prev3_open")
        prev3_close = kwargs.get("prev3_close")

        if prev_open and prev_close:
            if self.is_bullish_engulfing(prev_open, prev_close):
                return "Bullish Engulfing"
            elif self.is_bearish_engulfing(prev_open, prev_close):
                return "Bearish Engulfing"
            elif self.is_piercing_pattern(prev_open, prev_close):
                return "Piercing Pattern"
            elif self.is_dark_cloud_cover(prev_open, prev_close):
                return "Dark Cloud Cover"
            elif self.is_tweezer_top(prev_high):
                return "Tweezer Top"
            elif self.is_tweezer_bottom(prev_low):
                return "Tweezer Bottom"
        if prev1_open and prev1_close and prev2_open and prev2_close:
            if self.is_three_white_soldiers(prev1_open, prev1_close, prev2_open, prev2_close):
                return "Three White Soldiers"
            elif self.is_three_black_crows(prev1_open, prev1_close, prev2_open, prev2_close):
                return "Three Black Crows"
        if prev1_open and prev1_close and prev2_open and prev2_close and prev3_open and prev3_close:
            if self.is_three_line_strike(prev1_open, prev1_close, prev2_open, prev2_close, prev3_open, prev3_close):
                return "Three Line Strike"

        # Unknown Type
        return "Unknown"