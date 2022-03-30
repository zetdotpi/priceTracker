from dataclasses import dataclass
from datetime import datetime


@dataclass
class Entry:
    title: str
    url: str
    price: float
    last_check_dt: datetime

    def to_string(self, for_tg: bool = True) -> str:
        if for_tg:
            return f'{self.title} (*{self.url}*): {self.price}'
        else:
            return f'{self.title} ({self.url}): {self.price}'

    def to_tuple(self):
        return (self.title, self.price, self.last_check_dt.isoformat(), self.url)

    @classmethod
    def from_tuple(cls, data):
        return cls(data[0], data[1], data[2], datetime.fromisoformat(data[3]) if data[3] else None)

@dataclass
class ComparisonPair:
    old: Entry
    new: Entry

    def priceDifference(self):
        return self.new.price - self.old.price


