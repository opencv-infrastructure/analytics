import logging
from contextlib import ExitStack
from functools import partial

from github_api.connection.connection import Connection
from github_api.connection.repository import RepositoryApi

DEFAULT_URL_BASE = 'https://api.github.com'


def configure_github_api_logger(severity_level=logging.INFO, filename=None):
    logger = logging.getLogger('github_api')
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(severity_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if filename:
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(severity_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


class GitHubApi:
    def __init__(self, auth_token=None, url_base=DEFAULT_URL_BASE):
        self._establish_connection = partial(Connection, url_base,
                                             auth_token=auth_token)
        self._connection = None
        self._exit_stack = ExitStack()

    def __enter__(self):
        self._connection = self._exit_stack.enter_context(
            self._establish_connection()
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection = None
        self._exit_stack.pop_all()
        self._exit_stack = None

    def get_repository_api(self, fullname):
        if not self._connection:
            raise RuntimeError(
                'GitHubApi should be used within context manager flow'
            )
        get_repo = self._connection.get(f'{self._connection.url_base}/repos/{fullname}')
        return RepositoryApi(self._connection, get_repo.json())
