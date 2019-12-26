from utils.serialization import Serializable
from utils.date_utils import parse_iso_date

from github_api.models.owner import Owner


class Milestone(Serializable):
    def __init__(self, json_dict):
        self.api_url = json_dict['url']
        self.url = json_dict['html_url']
        self.labels_url = json_dict['labels_url']
        self.uid = json_dict['id']
        self.node_id = json_dict['node_id']
        self.state = json_dict['state']
        self.number = json_dict['number']
        self.title = json_dict['title']
        self.description = json_dict['description']
        self.creator = Owner.from_json(json_dict['creator'])
        self.open_issues = json_dict['open_issues']
        self.closed_issues = json_dict['closed_issues']
        self.created_at = parse_iso_date(json_dict['created_at'])
        self.updated_at = parse_iso_date(json_dict['updated_at'])
        self.closed_at = parse_iso_date(json_dict['closed_at'])
        self.due_on = parse_iso_date(json_dict['due_on'])

    def to_json(self):
        return {
            'url': self.api_url,
            'html_url': self.url,
            'labels_url': self.labels_url,
            'id': self.uid,
            'node_id': self.node_id,
            'number': self.number,
            'state': self.state,
            'title': self.title,
            'description': self.description,
            'creator': self.creator,
            'open_issues': self.open_issues,
            'closed_issues': self.closed_issues,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'closed_at': self.closed_at.isoformat(),
            'due_on': self.due_on.isoformat()
        }

    @classmethod
    def from_json(cls, json_dict):
        pass
