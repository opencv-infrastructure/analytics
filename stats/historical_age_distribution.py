from stats import AgeDistribution
from stats.stat import HistoricalStat


class HistoricalAgeDistribution(HistoricalStat):
    def __init__(self):
        self.distribution = {}

    def build(self, retrospective):
        for prs in retrospective:
            age_distribution = AgeDistribution(prs.end)
            for pr in prs.end_pull_requests:
                age_distribution.add(pr)
            self.distribution[prs.end] = age_distribution.ages_distribution