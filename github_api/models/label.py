from enum import Enum
from utils.serialization import Serializable


class LabelType(Enum):
    Other = 0,
    Category = 1
    Platform = 2
    EffortsEstimation = 3
    Priority = 4
    ChangesType = 5
    Problem = 6
    Reproducer = 7


class Label(Serializable):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self._type = self._determinate_type()

    def __repr__(self):
        return f'Label(name={self.name}, description={self.description},' \
               f' type={self._type})'

    @property
    def ltype(self):
        return self._type

    def to_json(self):
        return dict(name=self.name, description=self.description)

    @classmethod
    def from_json(cls, label_json):
        return cls(label_json['name'], label_json['description'])

    def _determinate_type(self):
        if self.name.startswith('category'):
            return LabelType.Category
        elif self.name.startswith('platform'):
            return LabelType.Platform
        elif self.name.startswith('effort'):
            return LabelType.EffortsEstimation
        elif self.name.startswith('priority'):
            return LabelType.Priority
        elif self.name in ('evolution', 'feature', 'bug', 'optimization',
                           'test', 'confirmed', 'future'):
            return LabelType.ChangesType
        elif self.name.startswith('pr'):
            if 'reproducer' in self.name:
                return LabelType.Reproducer
            else:
                return LabelType.Problem
        elif self.name in ('community help requested', 'incomplete',):
            return LabelType.Problem
        else:
            return LabelType.Other
