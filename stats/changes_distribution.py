from collections import defaultdict
from functools import partial

from github_api.models import PullRequest, ChangeType
from stats.stat import Stat


def dict_of_dicts_generator(keys):
    return dict.fromkeys(keys, 0)


class ChangesDistribution(Stat):
    def __init__(self):
        self.distribution = defaultdict(partial(
            dict_of_dicts_generator, ChangeType
        ))

    def add(self, pull_request: PullRequest):
        changes_by_category = pull_request.get_changes_by_category(False)
        for category, changes in changes_by_category.items():
            for change_type, amount in changes.items():
                self.distribution[category][change_type] += amount
