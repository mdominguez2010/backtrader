# https://www.backtrader.com/blog/2019-07-19-rebalancing-conservative/rebalancing-conservative/
# See conservative_formula.pdf in 'Other' folder
'''
Selection criteria:
1. Low volatility
2. High Net Payout Yield
3. High Momentum
4. Rebalancing every month
'''

import argparse
import datetime
import glob
import os.path
import backtrader as bt
import backtrader.analyzers as btanalyzers

class NetPayOutData(bt.feeds.GenericCSVData):
    lines = ('npy',)  # add a line containing the net payout yield
    params = dict(
        npy=6,  # npy field is in the 6th column (0 based index)
        dtformat='%Y-%m-%d',  # fix date format a yyyy-mm-dd
        timeframe=bt.TimeFrame.Days,  # fixed the timeframe
        openinterest=-1,  # -1 indicates there is no openinterest field
    )


class St(bt.Strategy):
    params = dict(
        selcperc=0.10,  # percentage of stocks to select from the universe
        rperiod=1,  # period for the returns calculation, default 1 period
        vperiod=36,  # lookback period for volatility - default 36 periods
        mperiod=12,  # lookback period for momentum - default 12 periods
        reserve=0.05  # 5% reserve capital
    )

    def log(self, arg):
        print('{} {}'.format(self.datetime.date(), arg))

    def __init__(self):
        # calculate 1st the amount of stocks that will be selected
        self.selnum = int(len(self.datas) * self.p.selcperc)

        # allocation perc per stock
        # reserve kept to make sure orders are not rejected due to
        # margin. Prices are calculated when known (close), but orders can only
        # be executed next day (opening price). Price can gap upwards
        self.perctarget = (1.0 - self.p.reserve) / self.selnum

        # returns, volatilities and momentums
        rs = [bt.ind.PctChange(d, period=self.p.rperiod) for d in self.datas]
        vs = [bt.ind.StdDev(ret, period=self.p.vperiod) for ret in rs]
        ms = [bt.ind.ROC(d, period=self.p.mperiod) for d in self.datas]

        # simple rank formula: (momentum * net payout) / volatility
        # the highest ranked: low vol, large momentum, large payout
        self.ranks = {d: d.npy * m / v for d, v, m in zip(self.datas, vs, ms)}

    def next(self):
        # sort data and current rank
        ranks = sorted(
            self.ranks.items(),  # get the (d, rank), pair
            key=lambda x: x[1][0],  # use rank (elem 1) and current time "0"
            reverse=True,  # highest ranked 1st ... please
        )

        # put top ranked in dict with data as key to test for presence
        rtop = dict(ranks[:self.selnum])

        # For logging purposes of stocks leaving the portfolio
        rbot = dict(ranks[self.selnum:])

        # prepare quick lookup list of stocks currently holding a position
        posdata = [d for d, pos in self.getpositions().items() if pos]

        # remove those no longer top ranked
        # do this first to issue sell orders and free cash
        for d in (d for d in posdata if d not in rtop):
            # self.log('Leave {} - Rank {:.2f}'.format(d._name, rbot[d][0]))
            self.order_target_percent(d, target=0.0)

        # rebalance those already top ranked and still there
        for d in (d for d in posdata if d in rtop):
            # self.log('Rebal {} - Rank {:.2f}'.format(d._name, rtop[d][0]))
            self.order_target_percent(d, target=self.perctarget)
            del rtop[d]  # remove it, to simplify next iteration

        # issue a target order for the newly top ranked stocks
        # do this last, as this will generate buy orders consuming cash
        for d in rtop:
            # self.log('Enter {} - Rank {:.2f}'.format(d._name, rtop[d][0]))
            self.order_target_percent(d, target=self.perctarget)


def add_analyzers(cerebro):

    # Add analyzers
    analyzers_dict = {
        btanalyzers.SharpeRatio: 'mysharpe',
        btanalyzers.AnnualReturn: 'myannualreturn',
        btanalyzers.Returns: 'myreturn',
        btanalyzers.DrawDown: 'mydrawdown',
        btanalyzers.Transactions: 'mytransactions',
        btanalyzers.TradeAnalyzer: 'myanalyzer',
        btanalyzers.VWR: 'myvwr',
        btanalyzers.SQN: 'mysqn'
    }
    
    for key in analyzers_dict.keys():
        cerebro.addanalyzer(key, _name=analyzers_dict[key])
    
    return cerebro

def print_analyzers(analysis):

    print("\n*** Analysis ***")
    print("Sharpe Ratio: %.3f" % analysis.analyzers.mysharpe.get_analysis()['sharperatio'])
    print("Variability-Weighted Return: %.3f" % analysis.analyzers.myvwr.get_analysis()['vwr'])
    print("Mean annual return (pct): %.2f" % analysis.analyzers.myreturn.get_analysis()['rnorm100'], "%")
    print("Max drawdown (pct): %.2f" % analysis.analyzers.mydrawdown.get_analysis()['max']['drawdown'], "%")
    print("Max drawdown ($): %.0f" % analysis.analyzers.mydrawdown.get_analysis()['max']['moneydown'])
    print("Max drawdown length (days): %.0f" % analysis.analyzers.mydrawdown.get_analysis()['max']['len'])
    print("SQN: %.3f" % analysis.analyzers.mysqn.get_analysis()['sqn']) # As defined by Van K: scaled of 1 (below avg) to 7 (Holy Grail)

    print("\n*** PnL ***")
    print("Total Net: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['pnl']['net']['total'])
    print("Average Net: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['pnl']['net']['average'])

    print("\n*** Won ***")
    print("Number of winners: %.0f" % analysis.analyzers.myanalyzer.get_analysis()['won']['total'])
    print("Total profit - winners: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['won']['pnl']['total'])
    print("Average profit per winner: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['won']['pnl']['average'])
    print("Max profit: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['won']['pnl']['max'])

    print("\n*** Lost ***")
    print("Number of losers: %.0f" % analysis.analyzers.myanalyzer.get_analysis()['lost']['total'])
    print("Total loss - losers: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['lost']['pnl']['total'])
    print("Average loss per loser: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['lost']['pnl']['average'])
    print("Max loss: %.2f" % analysis.analyzers.myanalyzer.get_analysis()['lost']['pnl']['max'])
    total_accuracy = (analysis.analyzers.myanalyzer.get_analysis()['won']['total'] / (analysis.analyzers.myanalyzer.get_analysis()['won']['total'] + analysis.analyzers.myanalyzer.get_analysis()['lost']['total'])) * 100
    print("Total accuracy: %.2f" % total_accuracy, "%")



def run(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()

    # Data feed kwargs
    dkwargs = dict(**eval('dict(' + args.dargs + ')'))

    # Parse from/to-date
    dtfmt, tmfmt = '%Y-%m-%d', 'T%H:%M:%S'
    if args.fromdate:
        fmt = dtfmt + tmfmt * ('T' in args.fromdate)
        dkwargs['fromdate'] = datetime.datetime.strptime(args.fromdate, fmt)

    if args.todate:
        fmt = dtfmt + tmfmt * ('T' in args.todate)
        dkwargs['todate'] = datetime.datetime.strptime(args.todate, fmt)

    # add all the data files available in the directory datadir
    for fname in glob.glob(os.path.join(args.datadir, '*')):
        data = NetPayOutData(dataname=fname, **dkwargs)
        cerebro.adddata(data)

    # add strategy
    cerebro.addstrategy(St, **eval('dict(' + args.strat + ')'))

    # add analyzers
    add_analyzers(cerebro)

    # set the cash
    cerebro.broker.setcash(args.cash)
    print('\nStarting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    backtest = cerebro.run()  # execute it all
    analysis = backtest[0] # to perform analysis

    # Basic performance evaluation ... final value ... minus starting cash
    pnl = cerebro.broker.get_value() - args.cash
    print("Ending Portfolio Value: %.2f" % cerebro.broker.get_value())
    print("PnL (inc. Unrealized Gain/Loss): {:.2f}".format(pnl))
    print(analysis.analyzers.myanalyzer.get_analysis()['total']['total'], 'total transactions,', analysis.analyzers.myanalyzer.get_analysis()['total']['open'], 'open,', analysis.analyzers.myanalyzer.get_analysis()['total']['closed'], 'closed\n')

    # print analyzers
    print_analyzers(analysis)

def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=('Rebalancing with the Conservative Formula'),
    )

    parser.add_argument('--datadir', required=True,
                        help='Directory with data files')

    parser.add_argument('--dargs', default='',
                        metavar='kwargs', help='kwargs in k1=v1,k2=v2 format')

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in k1=v1,k2=v2 format')

    parser.add_argument('--cash', default=100000.0, type=float,
                        metavar='kwargs', help='kwargs in k1=v1,k2=v2 format')

    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in k1=v1,k2=v2 format')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()