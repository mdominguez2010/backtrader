"""
This is a good strategy for bull markets
"""

import math
import backtrader as bt

STOCK = 'SPY'

class GoldenCross(bt.Strategy):
    params = (
        ('fast', 50),
        ('slow', 200),
        ('order_percentage', 0.90),
        ('ticker', STOCK)
    )

    def __init__(self):
        self.crossovers = []

        for d in self.datas:
            self.fast_moving_average = bt.indicators.SMA(
                d,
                period=self.params.fast,
                plotname='50 day moving average'
            )

            self.slow_moving_average = bt.indicators.SMA(
                d,
                period=self.params.slow,
                plotname='200 day moving average'
            )

            self.crossovers.append(bt.indicators.CrossOver(
                self.fast_moving_average,
                self.slow_moving_average
                )
            )
    
    def next(self):
        for i, d in enumerate(self.datas):
            if self.getposition(d).size == 0:
                if self.crossovers[i] > 0:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close)
                    # print("{} Buy {} shares of {} at {}".format(
                    #     self.datas[0].datetime.date(0),
                    #     self.size,
                    #     self.params.ticker,
                    #     self.data.close[0]))

                    self.buy(data=d, size=self.size)

            if self.getposition(d).size > 0:
                if self.crossovers[i] < 0:
                    # print("{} Sell {} shares of {} at {}".format(
                    #     self.datas[0].datetime.date(0),
                    #     self.size,
                    #     self.params.ticker,
                    #     self.data.close[0]))
                    self.close(data=d)
