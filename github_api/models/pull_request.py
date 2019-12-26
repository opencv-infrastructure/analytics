import datetime
from types import MappingProxyType

from github_api.models.repository import Repository
from github_api.models.milestone import Milestone
from github_api.models.user import User
from github_api.models.change import Change, ChangeType
from github_api.models.label import Label, LabelType
from utils.serialization import Serializable

from utils.date_utils import parse_iso_date, DateRange

from collections import defaultdict

DEFAULT_MODULES_TO_CONVERSION = MappingProxyType({
    'java': 'java bindings',
    'js': 'javascript (js)',
    'python': 'python bindings',
    'ts': 't-api',
    'gapi': 'g-api / gapi'
})

DEFAULT_CATEGORY_PREFIXES = MappingProxyType({
    'doc': 'documentation',
    'apps': 'apps',
    'samples': 'samples',
    'cmake': 'build/install',
    '3rdparty': '3rdparty'
})


def categorize_change(change,
                      module_to_category=DEFAULT_MODULES_TO_CONVERSION,
                      category_prefixes=DEFAULT_CATEGORY_PREFIXES):
    if change.filename.startswith('module'):
        module_name = change.filename.split('/')[1]
        return module_to_category.get(module_name, module_name)
    else:
        for prefix, category in category_prefixes.items():
            if change.filename.startswith(prefix):
                return category
        else:
            return 'infrastructure'


def categorize(pull_request):
    auto_assigned = False
    categories = tuple(
        label.name.split('category: ')[-1]
        for label in
        filter(lambda l: l.ltype is LabelType.Category, pull_request.labels)
    )
    if len(categories) == 0 and pull_request.changed_files:
        auto_assigned = True
        categories = tuple(set(
            categorize_change(change) for change in pull_request.changed_files))
    return categories, auto_assigned


class ChangeReference(Serializable):
    def __init__(self, label, ref, sha, user, repository):
        self.label = label
        self.ref = ref
        self.sha = sha
        self.user = user
        self.repository = repository

    def to_json(self):
        return {
            'label': self.label,
            'ref': self.ref,
            'sha': self.sha,
            'user': self.user,
            'repo': self.repository
        }

    @classmethod
    def from_json(cls, json_dict):
        return cls(
            json_dict['label'],
            json_dict['ref'],
            json_dict['sha'],
            User.from_json(json_dict['user']),
            Repository.from_json(json_dict['repo'])
        )


class PullRequest(Serializable):
    def __init__(self, pr_dict):
        self.title = pr_dict['title']
        self.url = pr_dict['html_url']
        self.uid = pr_dict['id']
        self.number = pr_dict['number']
        self.state = pr_dict['state']
        self.labels = tuple(map(Label.from_json, pr_dict['labels']))
        self.user = User.from_json(pr_dict['user'])
        self.body = pr_dict['body']
        if pr_dict.get('milestone'):
            self.milestone = Milestone.from_json(pr_dict.get('milestone'))
        else:
            self.milestone = None
        self.created_at = parse_iso_date(pr_dict['created_at'])
        self.updated_at = parse_iso_date(pr_dict['updated_at'])
        if pr_dict.get('closed_at'):
            self._closed_at = parse_iso_date(pr_dict['closed_at'])
        else:
            self._closed_at = None
        if pr_dict.get('merged_at'):
            self._merged_at = parse_iso_date(pr_dict['merged_at'])
        else:
            self._merged_at = None
        if pr_dict.get('assignee'):
            self._assignee = User.from_json(pr_dict['assignee'])
        else:
            self._assignee = None
        self.assignees = tuple(
            map(User.from_json, pr_dict.get('assignees', ()))
        )
        self.requested_reviewers = tuple(
            map(User.from_json, pr_dict.get('requested_reviewers', ()))
        )
        if pr_dict.get('head') is not None:
            self.head = ChangeReference.from_json(pr_dict['head'])
        else:
            self.head = None
        if pr_dict.get('base') is not None:
            self.base = ChangeReference.from_json(pr_dict['base'])
        else:
            self.base = None
        if pr_dict.get('changed_files') is not None:
            self.changed_files = tuple(
                map(Change.from_json, pr_dict['changed_files'])
            )
            self._categories, self._categories_assigned = categorize(self)
        else:
            self.changed_files = None
            self._categories, self._categories_assigned = None, None

    def __hash__(self):
        return hash(self.number)

    def __eq__(self, other):
        return self.number == other.number

    def get_age(self, since):
        """Age of the pull request in days"""
        if type(since) is datetime.date:
            created_at = self.created_at.date()
        else:
            created_at = self.created_at
        return max((since - created_at).days, 0)


    def get_last_update_age(self, since):
        """Estimated in days"""
        if not hasattr(self, '_update_age'):
            self._update_age = max((since - self.updated_at).days, 0)
        return self._update_age

    @property
    def categories(self):
        if self._categories is None:
            self._categories, self._categories_assigned = categorize(self)
        return self._categories

    @property
    def are_categories_auto_assigned(self):
        if self._categories_assigned is None:
            self._categories, self._categories_assigned = categorize(self)
        return self._categories_assigned

    @property
    def changes_type(self):
        return filter(lambda l: l.ltype is LabelType.ChangesType, self.labels)

    @property
    def problems(self):
        return filter(lambda l: l.ltype is LabelType.Problem, self.labels)

    @property
    def efforts_estimation(self):
        return filter(lambda l: l.ltype is LabelType.EffortsEstimation,
                      self.labels)

    @property
    def platforms_info(self):
        return filter(lambda l: l.ltype is LabelType.Platform, self.labels)

    @property
    def other_labels(self):
        return filter(lambda l: l.ltype is LabelType.Other, self.labels)

    @property
    def is_wip(self):
        return 'wip' in self.title.lower() or 'wip' in self.body.lower()

    @property
    def is_reproducer(self):
        def notice_reproducer():
            return 'reproducer' in self.title.lower() \
                   or 'reproducer' in self.body.lower()

        def has_reproducer_label():
            return any(filter(
                lambda l: l.ltype is LabelType.Reproducer, self.labels
            ))

        return has_reproducer_label() or notice_reproducer()

    @property
    def total_changes(self):
        additions = 0
        deletions = 0
        for changed_file in self.changed_files:
            additions += changed_file.additions
            deletions += changed_file.deletions
        return {ChangeType.Addition: additions, ChangeType.Deletion: deletions}

    def get_changes_by_category(self, include_total=True):
        def empty_change():
            return dict.fromkeys(ChangeType, 0)

        changes_by_category = defaultdict(empty_change)
        additions = 0
        deletions = 0
        for changed_file in self.changed_files:
            category_changes = changes_by_category[
                categorize_change(changed_file)
            ]
            category_changes[ChangeType.Addition] += changed_file.additions
            category_changes[ChangeType.Deletion] += changed_file.deletions
            if include_total:
                additions += changed_file.additions
                deletions += changed_file.deletions
        if include_total:
            changes_by_category['Total'] = {
                ChangeType.Addition: additions,
                ChangeType.Deletion: deletions
            }
        return changes_by_category

    @property
    def target_branch(self):
        return self.base.ref

    @property
    def is_merged(self):
        return self._merged_at is not None

    @property
    def merged_at(self):
        return self._merged_at

    @property
    def is_closed(self):
        return self._closed_at is not None

    @property
    def closed_at(self):
        return self._closed_at

    @property
    def is_assigned(self):
        return self._assignee or len(self._assignee) > 0

    @property
    def are_reviewers_requested(self):
        return len(self.requested_reviewers) > 0

    def to_json(self):
        return {
            'title': self.title,
            'html_url': self.url,
            'id': self.uid,
            'number': self.number,
            'state': self.state,
            'body': self.body,
            'milestone': self.milestone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'merged_at': self._merged_at.isoformat() if self._merged_at else None,
            'closed_at': self._closed_at.isoformat() if self._closed_at else None,
            'labels': self.labels,
            'user': self.user,
            'assignee': self._assignee,
            'assignees': self.assignees,
            'requested_reviewers': self.requested_reviewers,
            'head': self.head,
            'base': self.base,
            'changed_files': self.changed_files
        }

    @classmethod
    def from_json(cls, pr_json):
        return cls(pr_json)


class PullRequestsDiff(Serializable):
    def __init__(self, date_range, created=(), closed=()):
        self._date_range = date_range
        self._created = created
        self._closed = closed

    @property
    def date_range(self):
        return self._date_range

    @property
    def created(self):
        return self._created

    @property
    def closed(self):
        return self._closed

    @property
    def merged(self):
        return tuple(filter(lambda pr: pr.is_merged, self._closed))

    def to_json(self):
        return {
            'date_range': self._date_range,
            'created': self._created,
            'closed': self._closed,
        }

    @classmethod
    def from_json(cls, json_dict):
        return cls(
            DateRange.from_json(json_dict['date_range']),
            tuple(map(PullRequest.from_json, json_dict['created'])),
            tuple(map(PullRequest.from_json, json_dict['closed'])))
