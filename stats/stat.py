import datetime

from github_api.models import PullRequest


class Stat:
    def add(self, pull_request: PullRequest):
        raise NotImplementedError(
            'Concrete stat should implement this method'
        )

    def build(self, pull_requests):
        for pr in pull_requests:
            self.add(pr)


class HistoricalStat:
    def build(self, retrospective):
        raise NotImplementedError(
            'Concrete historical stat should implement this method'
        )
