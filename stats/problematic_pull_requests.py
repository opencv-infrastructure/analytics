from collections import defaultdict

from github_api.models import PullRequest
from stats.stat import Stat


class ProblematicPullRequests(Stat):
    def __init__(self):
        self.distribution = defaultdict(list)
        self.reproducers = list()
        self.wip = list()

    def add(self, pull_request: PullRequest):
        for problem in pull_request.problems:
            self.distribution[problem.name].append(pull_request)
        if pull_request.is_reproducer and not pull_request.is_wip:
            self.reproducers.append(pull_request)
        if pull_request.is_wip:
            self.wip.append(pull_request)

