import json


class NestedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Serializable):
            return obj.to_json()
        else:
            return json.JSONEncoder.default(self, obj)


class Serializable:
    def to_json_str(self):
        return json.dumps(self.to_json(), cls=NestedEncoder)

    def to_json(self):
        raise NotImplementedError('functionality is not implemented')

    @classmethod
    def from_json(cls, json_dict):
        raise NotImplementedError('functionality is not implemented')


def dump(obj, file):
    json.dump(obj, file, cls=NestedEncoder)


def dumps(obj):
    json.dumps(obj, cls=NestedEncoder)


def load(file):
    return json.load(file)
