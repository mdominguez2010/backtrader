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
#DATAPATH = './data/{}.csv'.format(STOCK)

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(STRATEGY)

# Add analyzers
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='myannualreturn')
cerebro.addanalyzer(btanalyzers.Returns, _name='myreturn')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydrawdown')
cerebro.addanalyzer(btanalyzers.Transactions, _name='mytransactions')
cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='myanalyzer')
cerebro.addanalyzer(btanalyzers.VWR, _name='myvwr')

# # Add a fixed position size
# cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# Create a Data Feed
stock_list = [
    'AAL', 'AAPL', 'AMZN', 'BA', 'BABA',
    'BAC', 'BBY', 'C', 'CAH', 'CCL',
    'COF', 'COP', 'CPB', 'CVS', 'CVX',
    'DE', 'DIA', 'EEM', 'EWW', 'EWZ',
    'F', 'FSLR', 'FXE', 'FXI', 'GLD',
    'GPS', 'HD', 'IBB', 'IBM', 'IWM',
    'JD', 'JNJ', 'JNK', 'JPM', 'K',
    'KO', 'KR', 'LOW', 'LVS', 'M',
    'MGM', 'MS', 'MSFT', 'NFLX', 'NKE',
    'PYPL', 'QQQ', 'RACE', 'RSX', 'SLV',
    'SPY', 'T', 'TBT', 'TGT', 'TLT',
    'TSLA', 'TWTR', 'V', 'VXX', 'VZ',
    'WFC', 'WMT', 'X', 'XLF', 'XLV']

for stock in stock_list:

    data = bt.feeds.YahooFinanceCSVData(
        dataname='./data/{}.csv'.format(stock),
        # Do not pass values before this date
        fromdate=datetime.datetime(FROM_YEAR, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(TO_YEAR, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data, name=stock)

# Set our desired cash start
cerebro.broker.setcash(1000000.0)

# Print out results
print("\n*** Results ***")
beginning_cash = cerebro.broker.getvalue()
print('Starting Portfolio Value: %.3f' % cerebro.broker.getvalue())

# Run everything
backtest = cerebro.run()
backtest = backtest[0]

# Final Results
print('Final Portfolio Value: %.3f' % cerebro.broker.getvalue())
ending_cash = cerebro.broker.getvalue()
print(f"Total profit: %.3f" % (ending_cash - beginning_cash))
print(backtest.analyzers.myanalyzer.get_analysis()['total']['total'], 'total transactions,', backtest.analyzers.myanalyzer.get_analysis()['total']['open'], 'open,', backtest.analyzers.myanalyzer.get_analysis()['total']['closed'], 'closed')


# Analysis
print("\n*** Analysis ***")
print("Sharpe Ratio: %.3f" % backtest.analyzers.mysharpe.get_analysis()['sharperatio'])
print("Variability-Weighted Return: %.3f" % backtest.analyzers.myvwr.get_analysis()['vwr'])
print("Mean annual return (pct): %.2f" % backtest.analyzers.myreturn.get_analysis()['rnorm100'], "&")
print("Max drawdown (pct): %.2f" % backtest.analyzers.mydrawdown.get_analysis()['max']['drawdown'], "%")
print("Max drawdown ($): %.0f" % backtest.analyzers.mydrawdown.get_analysis()['max']['moneydown'])
print("Max drawdown length (days): %.0f" % backtest.analyzers.mydrawdown.get_analysis()['max']['len'])
print("\n")

transactions = False

if transactions:
    print("*** Transaction breakdown ***")
    for key in backtest.analyzers.mytransactions.get_analysis().keys():
        print("Date:", key.date(), "| Symbol:", backtest.analyzers.mytransactions.get_analysis()[key][0][3], "| Price:%.2f" % backtest.analyzers.mytransactions.get_analysis()[key][0][1], "| Type:", ["Buy" if  x < 0 else "Sell" for x in [backtest.analyzers.mytransactions.get_analysis()[key][0][4]]][0], "| N_Shares:", backtest.analyzers.mytransactions.get_analysis()[key][0][0])
else:
    print("Transactions not printed")

#cerebro.plot()