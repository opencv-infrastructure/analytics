from utils.serialization import Serializable


class User(Serializable):
    def __init__(self, login, uid, url, api_url):
        self.login = login
        self.uid = uid
        self.url = url
        self.api_url = api_url

    def __repr__(self):
        return f'User(login={self.login}, id={self.uid}, url={self.url})'

    def to_json(self):
        return {
            'login': self.login,
            'id': self.uid,
            'html_url': self.url,
            'url': self.api_url
        }

    @classmethod
    def from_json(cls, user_json):
        return cls(user_json['login'],
                   user_json['id'],
                   user_json['html_url'],
                   user_json['url'])
