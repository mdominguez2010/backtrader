"""
Simple buy and hold strategy
"""
import backtrader as bt

STOCK = 'BAC'

class BuyHold(bt.Strategy):

    def next(self):
        if self.position.size == 0:
            size = int(self.broker.getcash() / self.data)
            self.buy(size=size)