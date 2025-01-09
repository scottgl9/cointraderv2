from .SignalStrength import SignalStrength

# Signal strength strategy for other timeframe
class SignalStrengthOther(SignalStrength):
    def __init__(self, symbol: str, name='signal_strength_other', granularity=0, weights=None):
        weights = {
            'supertrend': 0.8,
            'kst': 1.0,
            'vwap': 0.8,
            'ema': 1.0,
            'rsi': 1.0,
        }
        super().__init__(symbol=symbol, name=name, granularity=granularity, weights=weights)
