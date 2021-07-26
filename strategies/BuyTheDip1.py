"""
Simple Buy-The-Dip strategy: If stock is down for 3 consecutive days, then buy
Sell after desired number of days.
"""

import math
import backtrader as bt

N_DAYS_HOLD = 5

class BuyTheDip1(bt.Strategy):
    params = (
        ('order_percentage', 0.05),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose_list = []

        for d in self.datas:

            self.dataclose = d.close

            self.dataclose_list.append(self.dataclose)

    def next(self):
        for i, d in enumerate(self.datas):
            if self.getposition(d).size == 0:
                if self.dataclose_list[i][0] < self.dataclose_list[i][-1]:
                    if self.dataclose_list[i][-1] < self.dataclose_list[i][-2]:
                        if self.dataclose_list[i][-2] < self.dataclose_list[i][-3]:
                            amount_to_invest = (self.params.order_percentage * self.broker.cash)
                            self.size = math.floor(amount_to_invest / self.dataclose_list[i])

                            self.buy(data=d, size=self.size)

            if self.getposition(d).size > 0:
                if len(self) >= (N_DAYS_HOLD):
                    self.close(data=d)