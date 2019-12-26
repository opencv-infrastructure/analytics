from collections import defaultdict, namedtuple
from functools import partial

import numpy as np

from github_api.models import PullRequest
from stats.stat import Stat
from utils.date_utils import utc_now



DEFAULT_AGE_BOUNDS = (7, 14, 31, 180, 365)


def dict_of_list_generator(keys):
    return {k: list() for k in keys}


PullRequestWithAge = namedtuple('PullRequestWithAge', ['pr', 'age'])


class AgeDistribution(Stat):
    def __init__(self, time_point=utc_now(), age_bounds=DEFAULT_AGE_BOUNDS):
        self._time_point = time_point
        self._lower_bound = partial(np.searchsorted, age_bounds)
        self._age_categories = (
            f'< {age_bounds[0]} days',
            *(f'{l}-{r} days' for l, r in zip(age_bounds, age_bounds[1:])),
            f'> {age_bounds[-1]} days'
        )
        self.distribution = defaultdict(partial(
            dict_of_list_generator, self._age_categories
        ))
        self.ages_distribution = dict_of_list_generator(self._age_categories)

    def add(self, pull_request: PullRequest):
        pr_age = pull_request.get_age(self._time_point)
        age_category = self._age_categories[self._lower_bound(pr_age)]
        self.ages_distribution[age_category].append(
            PullRequestWithAge(pull_request, pr_age)
        )
        for category in pull_request.categories:
            category_stats = self.distribution[category]
            category_stats[age_category].append(pull_request)

    def export_results(self, path_to_page, path_to_resources):
        a
