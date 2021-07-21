import backtrader as bt
from BuyTheDip import *
from GoldenCross import *
import datetime

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(GoldenCross)

cerebro.addsizer(bt.sizers.FixedSize, stake=100)

datapath = './data/MSFT.csv'

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    # Do not pass values before this date
    fromdate=datetime.datetime(2015, 1, 1),
    # Do not pass values before this date
    todate=datetime.datetime(2020, 12, 31),
    # Do not pass values after this date
    reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(1000000.0)

# # Print out the starting conditions
# beginning_cash = cerebro.broker.getvalue()
# print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# # Print out the final result
# print('Final Portfolio Value: %.2f\n' % cerebro.broker.getvalue())
# ending_cash = cerebro.broker.getvalue()

# print(f"Total profit: {ending_cash - beginning_cash}")

cerebro.plot()