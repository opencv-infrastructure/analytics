from enum import Enum
from utils.serialization import Serializable


class ChangeType(Enum):
    Addition = 0
    Deletion = 1

    def __str__(self):
        return self.name


class Change(Serializable):
    def __init__(self, filename, status, additions, deletions):
        self.filename = filename
        self.status = status
        self.additions = additions
        self.deletions = deletions

    def __repr__(self):
        return f'Change(filename={self.filename}, status={self.status},' \
               f' additions={self.additions}, deletions={self.deletions})'

    @property
    def changes(self):
        return self.additions + self.deletions

    def to_json(self):
        return dict(filename=self.filename, status=self.status,
                    additions=self.additions, deletions=self.deletions)

    @classmethod
    def from_json(cls, changes_json):
        return cls(changes_json['filename'], changes_json['status'],
                   changes_json['additions'], changes_json['deletions'])
