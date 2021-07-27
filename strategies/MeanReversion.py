"""
Mean Reversion
Another type of mean reversion strategy revolving around a SMA
"""

import math
import backtrader as bt

class MeanReversion(bt.Strategy):
    
    params = (
        ('period', 20),
        ('order_percentage', 0.05),
        ('dip_size', 0.025),
    )

    def __init__(self):

        self.moving_average_list = []

        for d in self.datas:

            self.moving_average = bt.indicators.SMA(
                d,
                period=self.params.period,
                plotname=f"{self.params.period} day moving average"
            )

            self.moving_average_list.append(self.moving_average)

    def next(self):

        for i, d in enumerate(self.datas):
            if self.getposition(d).size == 0:
                if ((self.data.close[0] / self.moving_average_list[i][0]) - 1) <= -self.params.dip_size:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close[0])

                    self.buy(data=d, size=self.size)

            if self.getposition(d).size > 0:
                if self.data.close[0] >= self.moving_average_list[i][0]:

                    self.close(data=d)

