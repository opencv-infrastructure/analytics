import datetime

from utils.serialization import Serializable


class DateRange(Serializable):
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        assert (start is None and end is None) or start < end, \
            f'Invalid DateRange: start {start} should precede end {end} or ' \
            f' date_from and date_to should both be None - empty date range'
        self._start = start
        self._end = end

    def __str__(self):
        if self.is_empty:
            return 'DateRange()'
        return f'DateRange({self._start}, {self._end})'

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def is_empty(self):
        return self._start is None and self._end is None

    @classmethod
    def empty(cls):
        return cls(None, None)

    def to_json(self):
        if not self.is_empty:
            return {
                'start': self._start.isoformat().split('.')[0] + '+0000',
                'end': self._end.isoformat().split('.')[0] + '+0000'
            }
        else:
            return {'start': self._start, 'end': self._end}

    @classmethod
    def from_json(cls, json_dict):
        start = json_dict['start']
        if start:
            start = parse_iso_date(start)
        end = json_dict['end']
        if end:
            end = parse_iso_date(end)
        return cls(start, end)


def utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def parse_iso_date(iso_date: str):
    if iso_date.endswith('Z'):
        iso_date = iso_date.replace('Z', '+0000')
    elif '+' in iso_date[9:]:
        date, tz = iso_date.split('+')
        tz = tz.replace(':', '')
        iso_date = f'{date}+{tz}'
    return datetime.datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S%z')


def build_date_sequence(start: datetime.datetime,
                        end: datetime.datetime,
                        delta=datetime.timedelta(weeks=1)):
    current_date = start
    while current_date < end:
        yield current_date
        current_date += delta
    yield end
