import itertools
import re
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple


class SubMatcher(ABC):
    @classmethod
    def from_pattern(cls, pattern, default_base: int = 36):
        return (
            AnySubMatcher() if pattern == '*' else
            RangeListSubMatcher(pattern, default_base=default_base)
        )

    @abstractmethod
    def match(self, against: str) -> bool:
        pass

    @abstractmethod
    def __iter__(self) -> Iterable[str]:
        pass


class AnySubMatcher(SubMatcher):
    def match(self, against: str) -> bool:
        return True

    def __iter__(self):
        raise ValueError("Unable to generate from '*' pattern")


class RangeSubMatcher(SubMatcher):
    def __init__(self, rng: str, default_base: int = 36):
        super().__init__()
        rng = rng.strip('[] ')
        self.__init_flags(*rng.rsplit(':', maxsplit=1), default_base=default_base)

    def __init_flags(self, rng: str, base_str: Optional[str] = None, default_base: int = 36):
        self.base = default_base if base_str is None else int(base_str)
        self.__init_rng(*rng.split('-', maxsplit=1))

    def __init_rng(self, min_str: str, max_str: Optional[str] = None):
        self.min = self._int(min_str)
        self.max = self.min if max_str is None else self._int(max_str)

    def _int(self, str_value: str):
        return int(str_value, self.base)

    def match(self, against: str) -> bool:
        try:
            value = self._int(against)
        except ValueError:
            return False
        return self.min <= value <= self.max

    def _str(self, value: int):
        alpha = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        res = ""
        while value:
            res += alpha[value % self.base]
            value //= self.base
        return res[::-1] or "0"

    def __iter__(self):
        return map(self._str, range(self.min, self.max + 1))


class RangeListSubMatcher(SubMatcher):
    def __init__(self, rng: str, default_base: int = 36):
        super().__init__()
        rng_list = re.split(r'[,| ]+', rng.strip('[]'))
        self.sub_matchers = [RangeSubMatcher(rng, default_base=default_base) for rng in rng_list]

    def match(self, against: str) -> bool:
        return any(sub_matcher.match(against) for sub_matcher in self.sub_matchers)

    def __iter__(self):
        return itertools.chain.from_iterable(sub_matcher.__iter__() for sub_matcher in self.sub_matchers)


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

    def _generate_value(self, values: Tuple[str]):
        return ''.join(itertools.chain.from_iterable(itertools.zip_longest(self.parts, values, fillvalue='')))

    def __iter__(self) -> Iterable[str]:
        return map(self._generate_value, itertools.product(*self.sub_matchers))


class MatchPattern:
    def __init__(self, pattern, default_base: int = 36):
        self.matchers = [
            MatchSinglePattern(pat, default_base=default_base)
            for pat in re.split(r'(?!\[[^\]]*)[,| ]+(?![^\[]*\])', pattern)
        ]

    def match(self, against: str):
        return any(matcher.match(against) for matcher in self.matchers)

    def __iter__(self) -> Iterable[str]:
        return itertools.chain.from_iterable(self.matchers)
