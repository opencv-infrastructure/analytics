from enum import Enum

from utils.serialization import Serializable


class OwnerType(Enum):
    User = 0
    Organization = 1


class Owner(Serializable):
    def __init__(self, login, uid, url, api_url, otype):
        self.login = login
        self.uid = uid
        self.url = url
        self.api_url = api_url
        self._type = otype

    @property
    def otype(self):
        return self._type

    def to_json(self):
        return {
            'login': self.login,
            'id': self.uid,
            'html_url': self.url,
            'url': self.api_url,
            'type': self._type
        }

    @classmethod
    def from_json(cls, json_dict):
        return cls(
            json_dict['login'],
            json_dict['id'],
            json_dict['html_url'],
            json_dict['url'],
            json_dict['type']
        )
