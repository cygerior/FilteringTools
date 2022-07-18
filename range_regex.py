import itertools
import re
import sre_parse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import log10, ceil, floor
from typing import Iterable


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


class SubMatcher(ABC):
    @classmethod
    def from_pattern(cls, pattern, default_base: int = 36):
        if pattern == '*':
            return AnySubMatcher()
        else:
            return RangeListSubMatcher(pattern, default_base=default_base)

    @abstractmethod
    def match(self, against: str) -> bool:
        pass

    @abstractmethod
    def generate(self) -> Iterable[str]:
        pass


class AnySubMatcher(SubMatcher):
    def match(self, against: str) -> bool:
        return True

    def generate(self):
        raise ValueError("Unable to generate from '*' pattern")


class RangeSubMatcher(SubMatcher):
    def __init__(self, rng: str, default_base: int = 36):
        super().__init__()
        rng = rng.strip('[] ')
        splt = rng.rsplit(':', maxsplit=1)
        rng = splt[0]
        self.base = default_base if len(splt) == 1 else int(splt[1])
        try:
            self.min, self.max = map(self._int, rng.split('-'))
        except ValueError:
            self.min = self.max = self._int(rng)

    def _int(self, str_value: str):
        return int(str_value, self.base)

    def match(self, against: str) -> bool:
        try:
            value = self._int(against)
        except ValueError:
            return False
        return self.min <= value <= self.max

    def _str(self, value: int):
        BS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        res = ""
        while value:
            res += BS[value % self.base]
            value //= self.base
        return res[::-1] or "0"

    def generate(self):
        return map(self._str, range(self.min, self.max + 1))


class RangeListSubMatcher(SubMatcher):
    def __init__(self, rng: str, default_base: int = 36):
        super().__init__()
        rng_list = re.split(r'[,| ]+', rng.strip('[]'))
        self.sub_matchers = [RangeSubMatcher(rng, default_base=default_base) for rng in rng_list]

    def match(self, against: str) -> bool:
        return any(sub_matcher.match(against) for sub_matcher in self.sub_matchers)

    def generate(self):
        return itertools.chain.from_iterable(sub_matcher.generate() for sub_matcher in self.sub_matchers)


class MatchSinglePattern:
    GROUP_RE = re.compile(r'(\[.*?\]|\*)', re.IGNORECASE)

    @staticmethod
    def escape(match: re.Match):
        return re.escape(match.group(0))

    def __init__(self, pattern: str, default_base: int = 36):
        self.default_base = default_base
        self.pattern = pattern
        self.__init_groups()

    def __init_groups(self):
        split_pattern = self.GROUP_RE.split(self.pattern)
        self.groups = split_pattern[1::2]
        self.parts = split_pattern[0::2]
        self.sub_matchers = [SubMatcher.from_pattern(pat, default_base=self.default_base) for pat in self.groups]
        escape_parts = map(re.escape, self.parts)
        self._regex_filter = re.compile(
            r'^' + '(.*?)'.join(escape_parts) + r'$',
            re.IGNORECASE
        )

    def match(self, against: str) -> bool:
        match = self._regex_filter.search(against)
        if not match:
            return False
        return all(sub_matcher.match(group) for group, sub_matcher in zip(match.groups(), self.sub_matchers))

    @staticmethod
    def _match_generate(matcher: SubMatcher):
        return matcher.generate()

    def _value_generate(self, values: Iterable[str]):
        return ''.join(itertools.chain.from_iterable(itertools.zip_longest(self.parts, values, fillvalue='')))

    def generate(self) -> Iterable[str]:
        values = itertools.product(*map(self._match_generate, self.sub_matchers))
        return map(self._value_generate, values)


class MatchPattern:
    def __init__(self, pattern, default_base: int = 36):
        self.matchers = [MatchSinglePattern(pat, default_base=default_base) for pat in re.split(r'(?!\[[^\]]*)[,| ]+(?![^\[]*\])', pattern)]

    def match(self, against: str):
        return any(matcher.match(against) for matcher in self.matchers)

    def generate(self) -> Iterable[str]:
        return itertools.chain.from_iterable(matcher.generate() for matcher in self.matchers)

