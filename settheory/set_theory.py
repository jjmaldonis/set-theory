import re
import copy
from itertools import combinations
from typing import Union, List, Tuple


class Set(object):
    set_pattern = re.compile('(\[|\()\s*(-*\w*\.*\w*)\s*,\s*(\w*\.*\w*)\s*(\)|\])')

    def __str__(self):
        if self.low == self.high:
            return "[{}]".format(self.low)
        else:
            return "{}{}, {}{}".format(
                self.lbound,
                self.low,
                self.high,
                self.hbound
            )
    __repr__ = __str__

    def __init__(self, single: Union[str, int, float]):
        if not isinstance(single, str):
            # singleton
            self.lclosed = True
            self.hclosed = True
            self.low = float(single)
            self.high = self.low
            self._fill_bounds()
        else:
            lower, lowbound, highbound, higher = self.set_pattern.findall(single)[0]
            self.low = float(lowbound)
            self.high = float(highbound)
            self._set_bounds(lower, higher)

    def _set_bounds(self, lower, higher):
        if lower == "[":
            self.lclosed = True
        elif lower == "(":
            self.lopen = True
        else:
            raise ValueError(lower)
        if higher == "]":
            self.hclosed = True
        elif higher == ")":
            self.hopen = True
        else:
            raise ValueError(higher)
        self._fill_bounds()

    def _fill_bounds(self):
        if hasattr(self, "lopen"):
            self.lclosed = not self.lopen
        if hasattr(self, "lclosed"):
            self.lopen = not self.lclosed
        if hasattr(self, "hopen"):
            self.hclosed = not self.hopen
        if hasattr(self, "hclosed"):
            self.hopen = not self.hclosed

    @property
    def lbound(self):
        if self.lclosed:
            return "["
        elif self.lopen:
            return "("
        else:
            raise ValueError()

    @property
    def hbound(self):
        if self.hclosed:
            return "]"
        elif self.hopen:
            return ")"
        else:
            raise ValueError()

    def is_singleton(self) -> bool:
        return self.lclosed is True and self.hclosed is True and self.low == self.high

    def is_disjoint(self, aset: "Set") -> bool:
        if aset < self or aset > self:
            return True
        else:
            # Since Set can only be a single or a single continuous set, if the above check is False then the two
            #  sets are disjoint.
            return False

    def __contains__(self, num_or_set: Union["Set", int, float]) -> bool:
        if isinstance(num_or_set, (int, float)):
            num = num_or_set
            if num < self.low or num > self.high:
                return False
            if self.low < num < self.high:
                return True
            if self.low == num:
                return self.lclosed
            if self.high == num:
                return self.hclosed
            raise ValueError("Don't know how we got here", self, num)
        else:
            s = num_or_set
            if (self.low  < s.low  or (self.low  == s.low  and (self.lclosed or (self.lopen and s.lopen)))) and \
               (self.high > s.high or (self.high == s.high and (self.hclosed or (self.hopen and s.hopen)))):
                return True
            else:
                return False

    def __eq__(self, other: "Set") -> bool:
        return self.low == other.low and self.high == other.high and \
               self.lopen == other.lopen and self.hopen == other.hopen

    def __ne__(self, other: "Set") -> bool:
        return not self == other

    def __lt__(self, other: "Set") -> bool:
        # [0] < [1]
        # [0] > [-1]
        # ..., 1) < [1, ...
        # ..., 1) < (1, ...
        # ..., 1] < (1, ...
        # ..., 1] !< [1, ...
        if isinstance(other, (int, float)):
            return self.high < other or (self.high == other and self.hopen)
        if self.high < other.low:
            return True
        if self.high > other.low:
            return False
        if self.high == other.low:
            # Check bounds
            if self.hopen:
                return True
            if self.hclosed and other.lopen:
                return True
            if self.hclosed and other.lclosed:
                return False

    def __gt__(self, other: "Set") -> bool:
        return self != other and not self < other and other not in self and self not in other and \
               not (self.lclosed and other.hclosed and self.low == other.high) and \
               not (self.hclosed and other.lclosed and self.high == other.low)

    def __le__(self, other: "Set") -> bool:
        return self < other or self == other

    def __ge__(self, other: "Set") -> bool:
        return self > other or self == other

    def size(self) -> float:
        if self.is_singleton():
            return 0
        else:
            return self.high - self.low

    @staticmethod
    def union(s1: "Set", s2: "Set") -> Union["Set", Tuple["Set"]]:
        # Assume both are Set's
        s1, s2 = sorted([s1, s2], key=lambda s: s.low)
        s1, s2 = sorted([s1, s2])

        if s1 in s2:  # (0, 5) and (1, 2)
            return copy.deepcopy(s2)
        if s2 in s1:
            return copy.deepcopy(s1)
        # (0, 2) and (1, 3)
        # OR
        # (0, 1] and [1, 2)
        # OR
        # (0, 1) and [1]
        if s1.high > s2.low or \
           s1.high == s2.low and s1.hclosed and s2.lclosed:
            s3 = Set("{}{}, {}{}".format(s1.lbound, s1.low, s2.high, s2.hbound))
            return s3
        if s1.is_singleton():
            if s1.low == s2.low:
                return Set(f"[{s2.low}, {s2.high}{s2.hbound}")
            elif s1.high == s2.high:
                return Set(f"{s2.lbound}{s2.low}, {s2.high}]")
        if s2.is_singleton():
            if s1.low == s2.low:
                return Set(f"[{s1.low}, {s1.high}{s1.hbound}")
            elif s1.high == s2.high:
                return Set(f"{s1.lbound}{s1.low}, {s1.high}]")
        return s1, s2

    @staticmethod
    def merge(singles: List["Set"]) -> List["Set"]:
        # Merge sets
        if len(singles) > 1:
            all_merged = []
            dont_include = []
            for pair in combinations(singles, 2):
                merged = Set.union(*pair)
                if isinstance(merged, tuple):  # Then they are disjoint
                    all_merged.extend(merged)
                    assert len(merged) == 2
                    assert merged[0].is_disjoint(merged[1])
                else:
                    all_merged.append(merged)
                    dont_include.extend(pair)
            all_merged = [s for s in all_merged if not any(s is s_ for s_ in dont_include)]
            # Remove duplicates
            unique = []
            for s in all_merged:
                if not any(s == _s for _s in unique):
                    unique.append(s)
        else:
            unique = singles
        return unique

    @staticmethod
    def intersection(s1: "Set", s2: "Set") -> "Set":
        if s1 in s2:
            return copy.deepcopy(s1)
        if s2 in s1:
            return copy.deepcopy(s2)
        if Set.is_disjoint(s1, s2):
            return None  # TODO empty set. None?
        # [0, 3] and [2, 4]  OR  [0, 3] and [2, 3]
        if s2.low < s1.low:
            s2, s1 = s1, s2
        if s1.low > s2.low:  # low = max(s1.low, s2.low)
            low = s1.low
            lbound = s1.lbound
        else:
            low = s2.low
            lbound = s2.lbound
        if s1.high < s2.high:  # high = min(s1.high, s2.high)
            high = s1.high
            hbound = s1.hbound
        else:
            high = s2.high
            hbound = s2.hbound
        s = f"{lbound}{low}, {high}{hbound}"
        return Set(s)


class MultiSet(object):
    def __init__(self, *one_or_many: Union[str, int, float, Set, List]):
        if len(one_or_many) == 1:
            one_or_many = one_or_many[0]
        if isinstance(one_or_many, (str, int, float)):
            # one
            singles = [Set(one_or_many)]
        else:
            singles = one_or_many
        singles = [Set(one) if not isinstance(one, Set) else one for one in singles]
        self.singles = Set.merge(singles=singles)
        # Sort using Set order
        self.singles.sort(key=lambda s: s.low)
        self.singles.sort()

    def __str__(self):
        return "{{{}}}".format(", ".join(str(single) for single in self.singles))

    def __repr__(self):
        return str(self)

    def __contains__(self, other):
        if isinstance(other, Set) or isinstance(other, int) or isinstance(other, float):
            return any(other in single for single in self.singles)
        else:  # Assume `MultiSet`
            return all(
                any(other_single in single for single in self.singles) for other_single in other.singles
            )

    def __eq__(self, other):
        if isinstance(other, Set):
            return len(self.singles) == 1 and self.singles[0] == other
        else:  # Assume `MultiSet`
            return len(self.singles) == len(other.singles) and all(s == o for s, o in zip(self.singles, other.singles))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, Set):
            return all(s < other for s in self.singles)
        else:  # Assume `MultiSet`
            return all(
                all(single < other_single for other_single in other.singles) for single in self.singles
            )

    def __gt__(self, other):
        return self != other and not self < other

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def add(self, s: Union[Set, str, int, float]):
        """Add a set or single point to the MultiSet."""
        if isinstance(s, (str, int, float)):
            s = Set(s)
        self.singles = Set.merge([s] + self.singles)

    def remove(self, s):
        """Remove a set or single point from the MultiSet."""
        if isinstance(s, float) or isinstance(s, int):
            s = Set(s)
        raise NotImplemented

    def union(self, other: Union["MultiSet", Set]):
        if isinstance(other, MultiSet):
            new = MultiSet(*self.singles, *other.singles)
        else:
            new = MultiSet(*self.singles, other)
        return new

    def intersection(self, other: Union["MultiSet", Set]):
        raise NotImplementedError

    def is_disjoint(self, other: "MultiSet") -> bool:
        for aset in self.singles:
            for bset in other.singles:
                if not aset.is_disjoint(bset):
                    return False
        return True

    def __sub__(self, other):
        return self.remove(other)

    def __add__(self, other):
        return self.add(other)

    def __and__(self, other):
        """Returns a new intersection of the two sets."""
        return self.intersection(other)

    def __or__(self, other):
        """Returns a new union of the two sets."""
        return self.union(other)

    def __xor__(self, other):
        """The ^ symbol."""
        raise NotImplemented

    def __invert__(self):
        """The ~ symbol."""
        raise NotImplemented

    def size(self) -> float:
        """Returns the sum of the size of the single sets."""
        return sum(aset.size() for aset in self.singles)
