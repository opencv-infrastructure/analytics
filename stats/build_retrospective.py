import logging
from datetime import timedelta

from utils.date_utils import build_date_sequence


class RetrospectivePullRequests:
    def __init__(self, begin, end, begin_pull_requests, end_pull_requests,
                 changes):
        self.begin = begin
        self.end = end
        self.begin_pull_requests = begin_pull_requests
        self.end_pull_requests = end_pull_requests
        self.changes = changes

    @property
    def created(self):
        return self.changes['created']

    @property
    def closed(self):
        return self.changes['closed']


def get_diff(dates, pull_requests_diff):
    date_from, date_to = dates
    created_prs = tuple(filter(
        lambda pr: date_from <= pr.created_at.date() < date_to,
        pull_requests_diff.created
    ))
    created_in_range = len(created_prs)
    logging.info(f'Created {created_in_range}')
    closed_prs = tuple(filter(
        lambda pr: date_from <= pr.closed_at.date() < date_to,
        pull_requests_diff.closed
    ))
    closed_in_range = len(closed_prs)
    logging.info(f'Closed {closed_in_range}')
    # Going to the past, so signs must be inverted
    return {
        'created': created_prs,
        'closed': closed_prs
    }


def build_retrospective(pull_requests, pull_requests_diff):
    now_open = len(pull_requests)
    dates = list(build_date_sequence(pull_requests_diff.date_range.start,
                                     pull_requests_diff.date_range.end))
    opened_pull_requests = [set(pull_requests), ]
    # This week change:
    today = dates[-1].date()
    start_of_the_week = dates[-2].date()
    logging.info(f'Analyzing range from {start_of_the_week} to {today}')
    diff = get_diff((start_of_the_week, today + timedelta(days=1)),
                    pull_requests_diff)
    opened_pull_requests.append(
        set(opened_pull_requests[-1]).union(diff['closed']) - set(
            diff['created'])
    )
    retrospective = [RetrospectivePullRequests(start_of_the_week, today,
                                               opened_pull_requests[-1],
                                               opened_pull_requests[-2],
                                               diff)]
    logging.info(f'At {start_of_the_week} there were '
                 f'{len(opened_pull_requests[-1])} open pull_requests')
    for date_to, date_from in zip(reversed(dates[:-1]), reversed(dates[:-2])):
        date_to = date_to.date()
        date_from = date_from.date()
        logging.info(f'Analyzing range from {date_from} to {date_to}')
        diff = get_diff((date_from, date_to), pull_requests_diff)
        opened_pull_requests.append(
            set(opened_pull_requests[-1]).union(diff['closed']) - set(
                diff['created'])
        )
        logging.info(f'At {date_from} there were '
                     f'{len(opened_pull_requests[-1])} open pull_requests')
        retrospective.append(
            RetrospectivePullRequests(date_from, date_to,
                                      opened_pull_requests[-1],
                                      opened_pull_requests[-2],
                                      diff)
        )
    return retrospective