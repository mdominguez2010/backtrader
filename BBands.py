"""
Mean reversion using Bollinger Bands
"""

import math
import backtrader as bt
from . import MovAv, StdDev

STOCK = 'SPY'

class BBands(bt.Strategy):
    params = {
        ('period', 20),
        ('devfactor', 2.0),
        ('movav', MovAv),
        ('order_percentage', 0.90),
        ('ticker', STOCK)
    }

    def __init__(self):
        self.lines.mid = ma = self.params.movav(
            self.data.close,
            period = self.params.period,
            plotname="20 Day Moving Average"
        )

        stddev = self.params.devfactor * StdDev(
            self.data.close,
            ma,
            period=self.params.period,
            movav=self.params.movav
        )

        self.lines.top = ma + stddev

        self.lines.bot = ma - stddev