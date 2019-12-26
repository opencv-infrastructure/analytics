from github_api.models.owner import Owner
from utils.serialization import Serializable


class Repository(Serializable):
    def __init__(self, repo_dict):
        self.uid = repo_dict['id']
        self.node_id = repo_dict['node_id']
        self.name = repo_dict['name']
        self.full_name = repo_dict['full_name']
        self.is_private = repo_dict['private']
        self.owner = Owner.from_json(repo_dict['owner'])
        self.url = repo_dict['html_url']
        self.description = repo_dict['description']
        self.api_url = repo_dict['url']
        self.is_fork = repo_dict['fork']
        if self.is_fork:
            # The repository this repository was forked from
            if 'parent' in repo_dict:
                self._parent = Repository.from_json(repo_dict['parent'])
            else:
                self._parent = None
            # The ultimate source for the network
            if 'source' in repo_dict:
                self._source = Repository(repo_dict['source'])
            else:
                self._source = None

    @property
    def parent(self):
        if self.is_fork:
            return self._parent
        else:
            return None

    @property
    def source(self):
        if self.is_fork:
            return self._source
        else:
            return None

    def to_json(self):
        json_repr = {
            'id': self.uid,
            'node_id': self.node_id,
            'name': self.name,
            'full_name': self.full_name,
            'private': self.is_private,
            'owner': self.owner,
            'html_url': self.url,
            'description': self.description,
            'url': self.api_url,
            'fork': self.is_fork
        }
        if self.is_fork and self._parent and self._source:
            json_repr['parent'] = self._parent
            json_repr['source'] = self._source
        return json_repr

    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict)
