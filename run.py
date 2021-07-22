import sys
import backtrader as bt
import argparse
from BuyTheDip import *
from GoldenCross import *
from BuyHold import *
import datetime

# Adds an argument to bash command 
strategies = {
    "golden_cross": GoldenCross,
    "buy_hold": BuyHold,
    "buy_dip": BuyTheDip
}

parser = argparse.ArgumentParser()
parser.add_argument("strategy", help="which strategy to run", type=str)
args = parser.parse_args()

if not args.strategy in strategies:
    print("Invalid strategy, must be one of {}".format(strategies.keys()))
    sys.exit()

STRATEGY = strategies[args.strategy]
DATAPATH = './data/MSFT.csv'

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(STRATEGY)

#cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=DATAPATH,
    # Do not pass values before this date
    fromdate=datetime.datetime(2000, 1, 1),
    # Do not pass values before this date
    todate=datetime.datetime(2020, 12, 31),
    # Do not pass values after this date
    reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(1000000.0)

# Print out the starting conditions
beginning_cash = cerebro.broker.getvalue()
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f\n' % cerebro.broker.getvalue())
ending_cash = cerebro.broker.getvalue()

print(f"Total profit: {ending_cash - beginning_cash}")

cerebro.plot()