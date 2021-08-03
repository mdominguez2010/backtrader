import sys
import backtrader as bt
import backtrader.analyzers as btanalyzers
import argparse
from strategies.BuyTheDip import *
from strategies.GoldenCross import *
from strategies.BuyHold import *
from strategies.Ichimoku import *
from strategies.BollingerBands import *
from strategies.MeanReversion import *
import datetime
import time

# Time it
start = time.time()

transactions = False
plot = False

# Define start year and ending year for our analysis
FROM_YEAR = 2000
TO_YEAR = 2021
STRATEGY = [Ichimoku]


# # Adds an argument to bash command 
# strategies = {
#     "golden_cross": GoldenCross,
#     "buy_hold": BuyHold,
#     "buy_dip": BuyTheDip,
#     "ichimoku": Ichimoku,
#     "bbands": BollingerBands,
#     "mean_reversion": MeanReversion,
#     "momentum": Momentum
# }

# parser = argparse.ArgumentParser()
# parser.add_argument("strategy", help="which strategy to run", type=str)
# args = parser.parse_args()

# if not args.strategy in strategies:
#     print("Invalid strategy and/or stock, must be one of {}".format(strategies.keys()))
#     sys.exit()

# # Argument affects the strategy type
# STRATEGY = strategies[args.strategy]


# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy(ies)
for strategy in STRATEGY:
    cerebro.addstrategy(strategy)

# Add analyzers
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='myannualreturn')
cerebro.addanalyzer(btanalyzers.Returns, _name='myreturn')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydrawdown')
cerebro.addanalyzer(btanalyzers.Transactions, _name='mytransactions')
cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='myanalyzer')
cerebro.addanalyzer(btanalyzers.VWR, _name='myvwr')
cerebro.addanalyzer(btanalyzers.SQN, _name='mysqn')

# # Add a fixed position size
# cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# Create a Data Feed
stock_list = ['MSFT']
# stock_list = [
#     'AAL', 'AAPL', 'AMD', 'AMZN', 'BA',
#     'BABA', 'BAC', 'BBY', 'BIDU', 'BLK',
#     'BOX', 'BX', 'C', 'CAH', 'CCL',
#     'CLX', 'COF', 'COP', 'COST', 'CPB',
#     'CRM', 'CVS', 'CVX', 'CZR', 'DAL',
#     'DE', 'DECK', 'DIA', 'DVN', 'EEM',
#     'EWW', 'EWZ', 'F', 'FB', 'FSLR',
#     'FXE', 'FXI', 'GE', 'GLD', 'GOOG',
#     'GPRO', 'GPS', 'HD', 'IBB',
#     'IBM', 'IBND', 'IWM', 'JD', 'JNJ',
#     'JNK', 'JPM', 'K', 'KHC', 'KO',
#     'KR', 'LOW', 'LVS', 'M', 'MGM',
#     'MS', 'MSFT', 'MU', 'NFLX', 'NKE',
#     'PFE', 'PYPL', 'QQQ', 'RACE', 'RSX',
#     'SLV', 'SPY', 'STMP', 'T', 'TBT',
#     'TGT', 'TLT', 'TSLA', 'TWTR', 'USO',
#     'V', 'VB', 'VXX', 'VZ', 'WFC',
#     'WMT', 'X', 'XLF', 'XLV', 'YELP'
#     ]

for stock in stock_list:

    data = bt.feeds.YahooFinanceCSVData(
        dataname='./data/{}.csv'.format(stock),
        # Do not pass values before this date
        fromdate=datetime.datetime(FROM_YEAR, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(TO_YEAR, 7, 26),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data, name=stock)

# Set our desired cash start
cerebro.broker.setcash(100000.0)

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
print(f"Total profit (inc. Unrealized Gain/Loss): %.3f" % (ending_cash - beginning_cash))
print(backtest.analyzers.myanalyzer.get_analysis()['total']['total'], 'total transactions,', backtest.analyzers.myanalyzer.get_analysis()['total']['open'], 'open,', backtest.analyzers.myanalyzer.get_analysis()['total']['closed'], 'closed\n')

print("*** Streak ***")
print("Current win streak: ", backtest.analyzers.myanalyzer.get_analysis()['streak']['won']['current'])
print("Longest win streak: ", backtest.analyzers.myanalyzer.get_analysis()['streak']['won']['longest'])

print("\n*** PnL ***")
print("Total Net: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['pnl']['net']['total'])
print("Average Net: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['pnl']['net']['average'])

print("\n*** Won ***")
print("Number of winners: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['won']['total'])
print("Total profit - winners: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['won']['pnl']['total'])
print("Average profit per winner: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['won']['pnl']['average'])
print("Max profit: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['won']['pnl']['max'])

print("\n*** Lost ***")
print("Number of losers: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['lost']['total'])
print("Total loss - losers: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['lost']['pnl']['total'])
print("Average loss per loser: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['lost']['pnl']['average'])
print("Max loss: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['lost']['pnl']['max'])
total_accuracy = (backtest.analyzers.myanalyzer.get_analysis()['won']['total'] / (backtest.analyzers.myanalyzer.get_analysis()['won']['total'] + backtest.analyzers.myanalyzer.get_analysis()['lost']['total'])) * 100
print("Total accuracy: %.2f" % total_accuracy, "%")

print("\n*** Long Transactions ***")
# print("Number of long transactions: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['long']['total'])
# print("Total PnL: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['long']['pnl']['total'])
# print("Average PnL: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['long']['pnl']['average'])
# print("Average loss: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['long']['pnl']['average'])
# print("Number of winners: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['long']['won'])
# print("Number of Losers: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['long']['lost'])
# long_accuracy = (backtest.analyzers.myanalyzer.get_analysis()['long']['won'] / (backtest.analyzers.myanalyzer.get_analysis()['long']['won'] + backtest.analyzers.myanalyzer.get_analysis()['long']['lost'])) * 100
# print("Long accuracy: %.2f" % long_accuracy, "%")


print("\n*** Short Transactions ***")
# print("Number of short transactions: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['short']['total'])
# print("Total PnL: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['short']['pnl']['total'])
# print("Average PnL: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['short']['pnl']['average'])
# print("Average loss: %.2f" % backtest.analyzers.myanalyzer.get_analysis()['short']['pnl']['average'])
# print("Number of winners: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['short']['won'])
# print("Number of Losers: %.0f" % backtest.analyzers.myanalyzer.get_analysis()['short']['lost'])
# short_accuracy = 0
# print("Short accuracy: %.2f" % short_accuracy, "%")

print("\n*** len ***")
#print(backtest.analyzers.myanalyzer.get_analysis()['len'])

# Analysis
print("\n*** Analysis ***")
print("Sharpe Ratio: %.3f" % backtest.analyzers.mysharpe.get_analysis()['sharperatio'])
print("Variability-Weighted Return: %.3f" % backtest.analyzers.myvwr.get_analysis()['vwr'])
print("Mean annual return (pct): %.2f" % backtest.analyzers.myreturn.get_analysis()['rnorm100'], "%")
print("Max drawdown (pct): %.2f" % backtest.analyzers.mydrawdown.get_analysis()['max']['drawdown'], "%")
print("Max drawdown ($): %.0f" % backtest.analyzers.mydrawdown.get_analysis()['max']['moneydown'])
print("Max drawdown length (days): %.0f" % backtest.analyzers.mydrawdown.get_analysis()['max']['len'])
print("SQN: %.3f" % backtest.analyzers.mysqn.get_analysis()['sqn']) # As defined by Van K: scaled of 1 (below avg) to 7 (Holy Grail)
print("\n")

if transactions:
    print("*** Transactions ***")
    for key in backtest.analyzers.mytransactions.get_analysis().keys():
        print("Date:", key.date(), "| Symbol:", backtest.analyzers.mytransactions.get_analysis()[key][0][3], "| Price:%.2f" % backtest.analyzers.mytransactions.get_analysis()[key][0][1], "| Type:", ["Buy" if  x < 0 else "Sell" for x in [backtest.analyzers.mytransactions.get_analysis()[key][0][4]]][0], "| N_Shares:", backtest.analyzers.mytransactions.get_analysis()[key][0][0])
else:
    print("Transactions not printed")

if plot:
    cerebro.plot()

end = time.time()
run_time = end - start
print("Program run time: %.2f" % run_time, "seconds\n")