"""
Mean Reversion
A type of mean reversion using Bollinger Bands
"""

import math
import backtrader as bt

PCT_DIP = 0.01
PCT_JUMP = 0.05

class BollingerBands(bt.Strategy):

    params = {
        ('period', 20),
        ('devfactor', 2.0),
        ('order_percentage', 0.01)
    }

    def __init__(self):

        self.bbands_list = []

        for d in self.datas:

            self.bbands = bt.indicators.BollingerBands(
                d,
                period = self.params.period,
                devfactor = self.params.devfactor,
                movav = bt.indicators.MovAv.Simple
            )

            self.bbands_list.append(self.bbands)

    def next(self):

        for i, d in enumerate(self.datas):
            if self.getposition(d).size == 0:
                if self.data.close[0] <= ((1 - PCT_DIP) * self.bbands_list[i].lines.bot[0]):
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close)
                    
                    self.buy(data=d, size=self.size)

            if self.getposition(d).size > 0:
                if self.data.close[0] > ((1 + PCT_JUMP) * self.bbands_list[i].lines.bot[0]):

                    self.close(data=d)   