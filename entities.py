from dataclasses import dataclass
from datetime import datetime


@dataclass
class Entry:
    url: str
    price: float
    last_check_dt: datetime

    def to_tuple(self):
        return (self.price, self.last_check_dt.isoformat(), self.url)

    @classmethod
    def from_tuple(cls, data):
        return cls(data[0], data[1], datetime.fromisoformat(data[2]) if data[2] else None)

@dataclass
class ComparisonPair:
    old: Entry
    new: Entry

    def priceDifference(self):
        return self.new.price - self.old.price


