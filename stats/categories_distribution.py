from github_api.models import PullRequest
from collections import defaultdict

from stats.stat import Stat


class CategoriesDistribution(Stat):
    def __init__(self):
        self.distribution = defaultdict(list)
        self.with_auto_assigned_categories = list()
        self.total_pull_requests = 0

    def add(self, pull_request: PullRequest):
        self.total_pull_requests += 1
        for category in pull_request.categories:
            self.distribution[category].append(pull_request)
        if pull_request.are_categories_auto_assigned:
            self.with_auto_assigned_categories.append(pull_request)
