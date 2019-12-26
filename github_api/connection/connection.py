import logging
from datetime import datetime
from contextlib import AbstractContextManager
import requests
from requests.exceptions import HTTPError


def log_api_call(api_call):
    def wrapped_api_call(*args, **kwargs):
        if logger.isEnabledFor(logging.DEBUG):
            if args and hasattr(args[0], '__module__'):
                method_name = f'{type(args[0]).__name__}.{api_call.__name__}'
                log_args = args[1:]
            else:
                method_name = api_call.__name__
                log_args = args
            logger.debug(f'{method_name} called: args={log_args}, kwargs={kwargs}')
        return api_call(*args, **kwargs)

    logger = logging.getLogger('github_api')
    return wrapped_api_call


class Connection(AbstractContextManager):
    def __init__(self, url_base, auth_token=None):
        self._auth_token = auth_token
        self._session = None
        self.url_base = url_base
        self._logger = logging.getLogger('github_api')

    def __enter__(self):
        self._session = requests.Session()
        if self._auth_token:
            self._session.headers.update(
                {'Authorization': f'token {self._auth_token}'}
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        self._session = None

    @log_api_call
    def paginate_get(self, url, params=None, **kwargs):
        if self._logger and self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                f'Paginate get "{url}". params={params}, kwargs={kwargs}'
            )
        return self._send_pagination(self.get, url, params, **kwargs)

    @log_api_call
    def paginate_post(self, url, params=None, payload=None, **kwargs):
        if self._logger and self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                f'Paginate'
            )
        return self._send_pagination(self.post, url, params, payload=payload,
                                     **kwargs)

    @log_api_call
    def search(self, url, params=None, **kwargs):
        page = self.get(url, params, **kwargs)
        if not params:
            params = dict(page=1)
        else:
            params['page'] = 1
        entries = list(page.json()['items'])
        while 'next' in page.links:
            params['page'] += 1
            page = self.get(url, params, **kwargs)
            entries.extend(page.json()['items'])
        return entries

    @log_api_call
    def get(self, url, params=None, **kwargs):
        return self._send(
            requests.Request('GET', url, params=params, **kwargs)
        )

    @log_api_call
    def post(self, url, params=None, payload=None, **kwargs):
        return self._send(
            requests.Request('POST', url, params=params, data=payload, **kwargs)
        )

    @staticmethod
    def _send_pagination(send_one, url, params=None, **kwargs):
        page = send_one(url, params, **kwargs)
        if not params:
            params = dict(page=1)
        else:
            params['page'] = 1
        entries = page.json()
        while 'next' in page.links:
            params['page'] += 1
            page = send_one(url, params, **kwargs)
            entries.extend(page.json())
        return entries

    def _send(self, request):
        prepared = self._session.prepare_request(request)
        prepared.url = requests.utils.unquote(prepared.url)
        try:
            response = self._session.send(prepared)
            response.raise_for_status()
            if 'X-RateLimit-Remaining' in response.headers:
                api_calls_remains = int(response.headers['X-RateLimit-Remaining'])
                reset_at = datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                if api_calls_remains < 10:
                    self._logger.warning(f'{api_calls_remains} api call remains.'
                                         f'Resets at {reset_at.isoformat()}')
            return response
        except HTTPError as http_error:
            self._logger.error(f'HTTP error occurred during {request.method}: {http_error}')
            raise
        except Exception as error:
            self._logger.error(f'Error occurred during {request.method}: {error}')
            raise
