import sys
import backtrader as bt
import backtrader.analyzers as btanalyzers
import argparse
from strategies.BuyTheDip import *
from strategies.GoldenCross import *
from strategies.BuyHold import *
from strategies.BollingerBands import *
from strategies.MeanReversion import *
import datetime

# Define start year and ending year for our analysis
FROM_YEAR = 2000
TO_YEAR = 2020

# Adds an argument to bash command 
strategies = {
    "golden_cross": GoldenCross,
    "buy_hold": BuyHold,
    "buy_dip": BuyTheDip,
    "bbands": BollingerBands,
    "mean_reversion": MeanReversion
}

parser = argparse.ArgumentParser()
parser.add_argument("strategy", help="which strategy to run", type=str)
args = parser.parse_args()

if not args.strategy in strategies:
    print("Invalid strategy and/or stock, must be one of {}".format(strategies.keys()))
    sys.exit()

# Argument affects the strategy type
STRATEGY = strategies[args.strategy]
DATAPATH = './data/{}.csv'.format(STOCK)

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(STRATEGY)

# Add analyzers
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='myannualreturn')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydrawdown')

# # Add a fixed position size
# cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=DATAPATH,
    # Do not pass values before this date
    fromdate=datetime.datetime(FROM_YEAR, 1, 1),
    # Do not pass values before this date
    todate=datetime.datetime(TO_YEAR, 12, 31),
    # Do not pass values after this date
    reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(10000.0)

# Print out the starting conditions
beginning_cash = cerebro.broker.getvalue()
print('\nStarting Portfolio Value: %.2f\n' % cerebro.broker.getvalue())

# Run everything
backtest = cerebro.run()
backtest = backtest[0]

# Print out the final results
print('\nFinal Portfolio Value: %.2f\n' % cerebro.broker.getvalue())
ending_cash = cerebro.broker.getvalue()

print(f"\nTotal profit: {ending_cash - beginning_cash}\n")

print("Sharpe Ratio: ", backtest.analyzers.mysharpe.get_analysis()['sharperatio'])

# Calculate mean annual return
sum_values = 0
for val in backtest.analyzers.myannualreturn.get_analysis().values():
    sum_values += val

result = sum_values / len(backtest.analyzers.myannualreturn.get_analysis())

print("\nMean annual return: ", round(result, 4))

# Drawdown info
print("\nMax drawdown (%): ", backtest.analyzers.mydrawdown.get_analysis()['max']['drawdown'])
print("Max drawdown ($): ", backtest.analyzers.mydrawdown.get_analysis()['max']['moneydown'])
print("Max drawdown length", backtest.analyzers.mydrawdown.get_analysis()['max']['len'])

print("\n")

cerebro.plot()