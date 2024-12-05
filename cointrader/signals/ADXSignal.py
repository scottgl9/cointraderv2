from cointrader.common.Signal import Signal
from cointrader.indicators.ADX import ADX

class ADXignal(Signal):
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.adx = ADX(period)

    def update(self, kline):
        return self.adx.update(kline)

    def increasing(self):
        return self.rsi.increasing()
    
    def decreasing(self):
        return self.rsi.decreasing()
   
    def above(self):
        return self.rsi > self.overbought
    
    def below(self):
        return self.rsi < self.oversold
    
    def increasing(self):
        return self.rsi.increasing()
    
    def decreasing(self):
        return self.rsi.decreasing()
    
    def ready(self):
        return self.adx.ready()
