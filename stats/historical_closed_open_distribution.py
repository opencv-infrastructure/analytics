from stats.stat import HistoricalStat

import pandas as pd


class HistoricalClosedOpenDistribution(HistoricalStat):
    def __init__(self):
        self.data = pd.DataFrame(columns=['Date', 'Open', 'Created', 'Closed'])

    def build(self, retrospective):
        for prs in retrospective:
            self.data = self.data.append({
                'Date': prs.end,
                'Open': len(prs.end_pull_requests),
                'Created': len(prs.created),
                'Closed': len(prs.closed),
            }, ignore_index=True)
        self.data = self.data.append({
            'Date': retrospective[-1].begin,
            'Open': len(retrospective[-1].begin_pull_requests),
            'Created': len(retrospective[-1].created),
            'Closed': len(retrospective[-1].closed)
        }, ignore_index=True)
