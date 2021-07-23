"""
Another type of mean reversion strategy involving pct change
"""

import math
import backtrader as bt

STOCK = "SPY"

class MeanReversion(bt.Strategy):
    
    params = (
        ('period', 1),
        ('order_percentage', 0.90),
        ('ticker', STOCK)
    )

    def __init__(self):
        self.pct_change = bt.indicators.PercentChange(
            period = self.params.period
        )

    def next(self):
        if self.position.size == 0:
            if self.pct_change[0] <= -0.06:
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)

                print("Buy {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                
                self.buy(size=self.size)
                
######### Must find the proper selling logic

        # if self.position.size > 0:
        #     if self.pct_change[0] >= 0:
        #         print("Sell {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))

        #         self.close()   