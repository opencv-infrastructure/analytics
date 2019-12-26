import logging

from github_api.models import PullRequestsDiff, PullRequest

from utils.serialization import load, dump


class PullRequestsCache:
    def __init__(self, cache_file):
        self._cache_file = cache_file

    def load(self):
        logging.info(f'Loading pull requests from {self._cache_file.name}')
        cache = load(self._cache_file)
        return tuple(map(PullRequest.from_json, cache['pull_requests'])), \
               PullRequestsDiff.from_json(cache['diff'])

    def save(self, pull_requests, pull_requests_diff):
        cache_structure = {
            'pull_requests': pull_requests,
            'diff': pull_requests_diff
        }
        dump(cache_structure, self._cache_file)
        logging.info(f'Pull requests are saved {self._cache_file.name}')
