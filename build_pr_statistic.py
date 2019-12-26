import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import timedelta
from getpass import getpass

from github_api.connection import github
from stats.build_retrospective import build_retrospective

from utils.date_utils import DateRange, utc_now
from utils.pull_requests_cache import PullRequestsCache

import pages as ps


def build_pages(pages, pull_requests, retrospective, pages_path,
                resources_path):
    now = utc_now().isoformat().split('.')[0]
    logging.info(f'Building pages... Current UTC time: {now}')
    for page in pages.values():
        page.build(pull_requests, retrospective)
    logging.info('Writing pages....')
    for page_name, page in pages.items():
        page.save(f'{pages_path}/{page_name}.md', resources_path)
    logging.info('Building index.rst....')
    title_page = ps.TitlePage(now, pages.keys())
    title_page.build(pull_requests, retrospective)
    logging.info('Writing index.rst....')
    title_page.save(f'{pages_path}/index.rst', resources_path)
    logging.info('Done')


def download_pull_requests(token, diff_range=DateRange.empty()):
    github.configure_github_api_logger(logging.DEBUG)
    with github.GitHubApi(token) as api:
        opencv_repo = api.get_repository_api('opencv/opencv')
        return opencv_repo.load_open_pull_requests(), \
               opencv_repo.load_pull_requests_diff(diff_range)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Builds pull request statistic for OpenCV library'
    )
    parser.add_argument('--pages_path', type=Path,
                        default='./docs/source',
                        help='Path to pages directory. Will be created if does not exist')
    auth_token_group = parser.add_mutually_exclusive_group(required=False)
    auth_token_group.add_argument('--auth_token', type=str, default=None,
                                  help='Auth token to access Github API')
    auth_token_group.add_argument('--secure_auth', action='store_true',
                                  help='If specified, getpass prompt will be shown'
                                       ' to request auth token in secure way')
    cache_group = parser.add_mutually_exclusive_group(required=False)
    cache_group.add_argument('--cache', type=argparse.FileType('w'),
                             help='Save downloads into the cache file')
    cache_group.add_argument('--from_cache', type=argparse.FileType('r'),
                             help='Generates pages from the cache')

    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    if args.from_cache:
        cache = PullRequestsCache(args.from_cache)
        pull_requests, pull_requests_diff = cache.load()
    else:
        if args.auth_token:
            token = args.auth_token
        elif args.secure_auth:
            token = getpass('Enter public access token:')
        else:
            token = os.getenv('GITHUB_API_TOKEN')
            if not token:
                logging.warning(
                    'Neither "token" or "secure_auth" is specified '
                    'and "GITHUB_API_TOKEN" environment variable is not set.'
                    'Api calls are limited by 60 calls'
                )
        today = utc_now()
        start_of_the_week = today - timedelta(days=today.weekday())
        diff_range = DateRange(start_of_the_week - timedelta(weeks=12), today)
        pull_requests, pull_requests_diff = download_pull_requests(token,
                                                                   diff_range)
    if args.cache:
        cache = PullRequestsCache(args.cache)
        cache.save(pull_requests, pull_requests_diff)

    logging.info(f'{len(pull_requests)} pull requests for analysis')
    logging.info(f'Diff stats for {pull_requests_diff.date_range}')
    logging.info(f'{len(pull_requests_diff.merged)} merged pull requests')
    logging.info(f'{len(pull_requests_diff.closed)} closed pull requests')
    logging.info(f'{len(pull_requests_diff.created)} created pull requests')
    retrospective = build_retrospective(pull_requests, pull_requests_diff)
    pages = {
        'problems_distribution_page': ps.ProblematicPullRequestsPage(),
        'age_distribution_page': ps.AgeDistributionPage(),
        'changes_distribution_page': ps.ChangesDistributionPage(),
        'categories_distribution_page': ps.CategoriesDistributionPage()
    }
    # Path setup
    pages_path = args.pages_path
    resource_path = pages_path / '_static'
    resource_path.mkdir(parents=True, exist_ok=True)
    build_pages(pages, pull_requests, retrospective, pages_path, resource_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
