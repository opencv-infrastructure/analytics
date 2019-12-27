import logging

from github_api.models import Repository, Label, Change
from github_api.models import PullRequest, PullRequestsDiff

from utils.date_utils import DateRange

SEARCH_DATE_FORMAT = '%Y-%m-%d'


class RepositoryApi:
    def __init__(self, connection, repo_json):
        self._connection = connection
        self._logger = logging.getLogger('github_api')
        self._repository = Repository.from_json(repo_json)

    @property
    def info(self):
        return self._repository

    def load_open_pull_requests(self, load_files=True):
        self._logger.info('Loading pull requests with "open" state')
        pull_requests = tuple(
            map(PullRequest.from_json,
                self._connection.paginate_get(
                    f'{self._repository.api_url}/pulls'
                ))
        )
        self._logger.info(f'{len(pull_requests)} pull requests are loaded')
        if load_files:
            self._logger.info('Loading changed files for pull requests...')
            for pr in pull_requests:
                pr.changed_files = tuple(self.load_pull_request_files(pr))
            self._logger.info('Pull requests files are loaded')
        return tuple(pull_requests)

    def load_pull_requests_diff(self, date_range: DateRange):
        self._logger.info(f'Loading diff for date range {date_range}')
        return PullRequestsDiff(
            date_range,
            self.load_created_pull_requests(date_range),
            self.load_closed_pull_requests(date_range)
        )

    def load_closed_pull_requests(self, date_range: DateRange):
        from_date = date_range.start.strftime(SEARCH_DATE_FORMAT)
        to_date = date_range.end.strftime(SEARCH_DATE_FORMAT)
        self._logger.info(f'Loading closed pull requests in range {date_range}')
        end_point = f'{self._connection.url_base}/search/issues'
        query = f'repo:{self._repository.full_name}+type:pr+' \
                f'closed:{from_date}..{to_date}'
        pull_requests = list(
            map(PullRequest.from_json,
                self._connection.search(end_point, params={'q': query,
                                                           'per_page': 100}))
        )
        self._logger.debug(f'Found {len(pull_requests)} closed pull requests')
        return pull_requests

    def load_created_pull_requests(self, date_range: DateRange):
        from_date = date_range.start.strftime(SEARCH_DATE_FORMAT)
        to_date = date_range.end.strftime(SEARCH_DATE_FORMAT)
        self._logger.info(
            f'Loading created pull requests from date range {date_range}'
        )
        end_point = f'{self._connection.url_base}/search/issues'
        query = f'repo:{self._repository.full_name}+type:pr+' \
                f'created:{from_date}..{to_date}'
        pull_requests = list(
            map(PullRequest.from_json,
                self._connection.search(end_point, params={'q': query,
                                                           'per_page': 100}))
        )
        self._logger.debug(f'Found {len(pull_requests)} created pull requests')
        return pull_requests

    def load_labels(self):
        self._logger.info('Loading labels...')
        return tuple(
            map(Label.from_json,
                self._connection.paginate_get(
                    f'{self._repository.api_url}/labels'
                ))
        )

    def load_pull_request_files(self, pull_request):
        self._logger.info(f'Loading files for {pull_request.number}')
        return map(
            Change.from_json,
            self._connection.paginate_get(
                f'{self._repository.api_url}/pulls/{pull_request.number}/files')
        )
