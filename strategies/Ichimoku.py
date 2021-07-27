"""
Momentum
Ichimoku cloud break out strategy
"""

import math
import backtrader as bt
from backtrader.indicators.basicops import Highest, Lowest

class Ichimoku(bt.Strategy):

    lines = ('tenkan_sen', 'kijun_sen',
             'senkou_span_a', 'senkou_span_b', 'chikou_span',)
    params = (
        ('tenkan', 9),
        ('kijun', 26),
        ('senkou', 52),
        ('senkou_lead', 26),  # forward push
        ('chikou', 26),
        ('order_percentage', 0.05),  # backwards push
    )

    def __init__(self):

        self.ichimoku_list = []

        for d in self.datas:

            self.ichimoku = bt.indicators.Ichimoku(
                d,
                tenkan = self.params.tenkan,
                kijun = self.params.kijun,
                senkou = self.params.senkou,
                senkou_lead = self.params.senkou_lead,
                chikou = self.params.chikou
            )

            self.ichimoku_list.append(self.ichimoku)

    def next(self):

        for i, d in enumerate(self.datas):

            if self.getposition(d).size == 0:
                if self.data.close[0] > self.ichimoku_list[i].lines.senkou_span_a[0] > self.ichimoku_list[i].lines.senkou_span_b[0]:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close)

                    self.buy(data=d, size=self.size)

            if self.getposition(d).size > 0:
                if self.data.close[0] <= self.ichimoku_list[i].lines.senkou_span_a[0] or self.data.close[0] <= self.ichimoku_list[i].lines.senkou_span_b[0]:

                    self.close(data=d)      