from dataclasses import dataclass
from math import log10, floor


@dataclass
class Range:
    min: int
    max: int


class RangeRegex:
    def __init__(self, range_pattern: str):
        self.range_pattern = range_pattern
        self.ranges = [Range(*range_pattern.split('-'))]

    def partial_decade_split(self):
        pass

    @staticmethod
    def split_range(start: int, end: int):
        start_dec = floor(log10(start))
        end_dec = floor(log10(end))

        return [(max(10**dec, start), min(10 ** (dec + 1) - 1, end)) for dec in range(start_dec, end_dec+1)]

    @property
    def regex(self):
        regex_list = []
        if min < 10:
            regex_list.append((self.min, min(9, self.max)))
        if max >= 10:
            regex_list.append((max(10, self.min), min(99, self.max)))


