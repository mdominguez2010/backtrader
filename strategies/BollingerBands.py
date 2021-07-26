"""
A type of mean reversion using Bollinger Bands
"""

import math
import backtrader as bt

STOCK = 'SPY'
PCT_DIP = 0.01
PCT_JUMP = 0.05

class BollingerBands(bt.Strategy):

    params = {
        ('period', 20),
        ('devfactor', 2.0),
        ('order_percentage', 0.05),
        ('ticker', STOCK)
    }

    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(
            self.data.close,
            period = self.params.period,
            devfactor = self.params.devfactor,
            movav = bt.indicators.MovAv.Simple
        )

    def next(self):
        if self.position.size == 0:
            if self.data.close[0] <= ((1 - PCT_DIP) * self.bbands.lines.bot[0]):
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)

                print("Buy {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                
                self.buy(size=self.size)

        if self.position.size > 0:
            if self.data.close[0] > ((1 + PCT_JUMP) * self.bbands.lines.bot[0]):
                print("Sell {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))

                self.close()   