"""
Another type of mean reversion strategy involving pct change
"""

import math
import backtrader as bt

class MeanReversion(bt.Strategy):
    
    params = (
        ('period', 1),
        ('order_percentage', 0.05),
    )

    def __init__(self):
        self.pct_change_list = []

        for d in self.datas:
            self.pct_change = bt.indicators.PercentChange(
                d,
                period = self.params.period
            )

            self.pct_change_list.append(self.pct_change)

    def next(self):
        for i, d in enumerate(self.datas):
            if self.getposition(d).size == 0:
                if self.pct_change_list[i] <= -0.04:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close)
                    
                    self.buy(data = d, size=self.size)
                    
    ######### Must find the proper selling logic #########

            if self.getposition(d).size > 0:
                if self.pct_change_list[i] > 0.01:

                    self.close(data=d)   