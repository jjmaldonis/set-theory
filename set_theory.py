import copy
from itertools import combinations
from typing import List, Tuple, Union


class Singleton(float):
    pass


class Interval(object):
    def __init__(self, interval: Union[List, Tuple], singleton: Singleton = None):
        """
        Examples:
            Interval((0, 1))  # The open interval from 0 to 1
            Interval([0, 1]  # The closed interval from 0 to 1
            Interval((0, 1), Singleton(0))  # The half-open interval [0, 1)
            Interval((0, 1), Singleton(1))  # The half-open interval (0, 1]
        """
        if singleton and singleton not in interval:
            raise ValueError("`singleton` must be on a boundary")
        if singleton and isinstance(interval, list):
            raise TypeError("`interval` cannot be a list if a `singleton` is provided")
        if isinstance(singleton, (int, float)):
            singleton = Singleton(singleton)
        self._interval = interval
        self._singleton = singleton

    @property
    def lower(self):
        return self._interval[0]

    @property
    def upper(self):
        return self._interval[1]

    @property
    def lopen(self):
        return isinstance(self._interval, tuple) and self.lower != self._singleton

    @property
    def ropen(self):
        return isinstance(self._interval, tuple) and self.upper != self._singleton

    @property
    def lclosed(self):
        return not self.lopen

    @property
    def rclosed(self):
        return not self.ropen

    def __str__(self):
        if not self._singleton:
            return str(self._interval)
        else:
            if self._singleton == self.lower:
                return f"[{self.lower}, {self.upper})"
            else:
                return f"({self.lower}, {self.upper}]"
    __repr__ = __str__

    def __contains__(self, num_or_set: Union['Interval', Singleton, float, int]):
        if isinstance(num_or_set, (Singleton, int, float)):
            num = num_or_set
            if isinstance(self._interval, tuple):
                return num == self._singleton or self.lower < num < self.upper
            else:
                return self.lower <= num <= self.upper
        else:
            other: Interval = num_or_set
            if (self.lower < other.lower or (self.lower == other.lower and (self.lclosed or self.lopen == other.lopen))) and \
               (self.upper > other.upper or (self.upper == other.upper and (self.rclosed or self.ropen == other.ropen))):
                return True
            else:
                return False

    def __eq__(self, other: Union["Interval", Singleton]):
        if isinstance(other, Singleton):
            return False
        return self._interval == other._interval and self._singleton == other._singleton

    def __ne__(self, other: Union["Interval", Singleton]):
        return not self == other

    def __lt__(self, other: Union["Interval", Singleton, float, int]):
        # ..., 1) < [1, ...
        # ..., 1) < (1, ...
        # ..., 1] < (1, ...
        # ..., 1] !< [1, ...
        if isinstance(other, (Singleton, float, int)):
            return self.upper < other
        low, high = self._interval
        olow, ohigh = other._interval
        if high < olow:
            return True
        if high > olow:
            return False
        if high == olow:
            # Check bounds
            if isinstance(self._interval, tuple):
                return True
            if isinstance(self._interval, list) and isinstance(other._interval, tuple):
                return True
            if isinstance(self._interval, list) and isinstance(other._interval, list):
                return False

    def __gt__(self, other: "Interval"):
        return self != other and not self < other

    def __le__(self, other: "Interval"):
        return self < other or self == other

    def __ge__(self, other: "Interval"):
        return self > other or self == other


class Set(object):
    def __init__(self, *intervals: Union[Interval, Singleton, tuple, list, float, int]):
        singles = []
        for interval in intervals:
            if not isinstance(interval, (Interval, Singleton)):
                if isinstance(interval, (float, int)):
                    interval = Singleton(interval)
                else:
                    interval = Interval(interval)
            singles.append(interval)

        # Merge sets
        if len(singles) > 1:
            all_merged = []
            dont_include = []
            for pair in combinations(singles, 2):
                merged = self.merge_two(*pair)
                if isinstance(merged, tuple):
                    all_merged.extend(merged)
                else:
                    all_merged.append(merged)
                    dont_include.extend(pair)
            all_merged = [s for s in all_merged if s not in dont_include]
            # Remove duplicates
            unique = []
            for s in all_merged:
                if not any(s == _s for _s in unique):
                    unique.append(s)
        else:
            unique = singles
        # Sort, using Interval order
        unique.sort(key=lambda s: s.lower if isinstance(s, Interval) else s)
        unique.sort()
        self.singles = unique

    def __str__(self):
        return "{{{}}}".format(", ".join(str(single) for single in self.singles))
    __repr__ = __str__

    def __contains__(self, other: Union["Set", Interval, Singleton, int, float]):
        if isinstance(other, (Interval, Singleton, int, float)):
            return any(other in single if isinstance(single, Interval) else other == single for single in self.singles)
        else:  # Assume `Set`
            return all(
                any(other_single in single if isinstance(single, Interval) else other_single == single for single in self.singles)
                for other_single in other.singles
            )

    def __eq__(self, other):
        if isinstance(other, Interval):
            return len(self.singles) == 1 and self.singles[0] == other
        else:  # Assume `Set`
            return len(self.singles) == len(other.singles) and all(s == o for s, o in zip(self.singles, other.singles))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, Interval):
            return all(s < other for s in self.singles)
        else:  # Assume `Set`
            return all(
                all(single < other_single for other_single in other.singles)
                for single in self.singles
            )

    def __gt__(self, other):
        return self != other and not self < other

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    @staticmethod
    def merge_two(s1: Union[Interval, Singleton], s2: Union[Interval, Singleton]):
        if isinstance(s1, Singleton):
            if isinstance(s2, Singleton):
                if s1 == s2:
                    return s1
                else:
                    return s1, s2

            # s2 is an Interval
            # 1 & (0, 2)  -  in interval
            # 0 & (1, 2)  -  too low
            # 3 & (1, 2)  -  too high
            # 0 & [0, 1]
            # 0 & (0, 1]
            # 1 & [0, 1]
            # 1 & (0, 1)
            if s1 in s2:
                return s2
            elif s1 < s2.lower or s1 > s2.upper:
                return s1, s2
            elif s1 == s2.lower:
                if s2.lclosed:
                    return s2
                elif s2.rclosed:  # and s2.lopen
                    return Interval([s2.lower, s2.upper])
                else:  # s2.ropen and s2.lopen
                    return Interval((s2.lower, s2.upper), s1)  # [s1, s2.upper)
            elif s1 == s2.upper:
                if s2.rclosed:
                    return s2
                elif s2.lclosed:  # and s2.ropen
                    return Interval([s2.lower, s1])
                else:  # s2.ropen and s2.lopen
                    return Interval((s2.lower, s2.upper), s1)  # (s2.lower, s1]

        if isinstance(s2, Singleton):
            if s2 in s1:
                return s1
            elif s2 < s1.lower or s2 > s1.upper:
                return s2, s1
            elif s2 == s1.lower:
                if s1.lclosed:
                    return s1
                elif s1.rclosed:  # and s1.lopen
                    return Interval([s1.lower, s1.upper])
                else:  # s1.ropen and s1.lopen
                    return Interval((s1.lower, s1.upper), s2)  # [s2, s1.upper)
            elif s2 == s1.upper:
                if s1.rclosed:
                    return s1
                elif s1.lclosed:  # and s1.ropen
                    return Interval([s1.lower, s2])
                else:  # s1.ropen and s1.lopen
                    return Interval((s1.lower, s1.upper), s2)  # (s1.lower, s2]

        # Swap order if necessary so that s1 < s2 if applicable
        #s1, s2 = sorted([s1, s2], key=lambda s: s._interval)
        s1, s2 = sorted([s1, s2])

        if s1 in s2:  # (0, 5) and (1, 2)
            return copy.deepcopy(s2)
        if s2 in s1:
            return copy.deepcopy(s1)
        # (0, 2) and (1, 3)
        # OR
        # (0, 1] and [1, 2)
        low1, high1 = s1._interval
        low2, high2 = s2._interval
        if (high1 > low2) or (high1 == low2 and s1.rclosed and s2.lclosed):
            if low1 in s1 and high2 in s2:
                s3 = Interval([low1, high2])
            elif low1 not in s1 and high2 not in s2:
                s3 = Interval((low1, high2))
            elif low1 in s1 and high2 not in s2:
                s3 = Interval((low1, high2), Singleton(low1))
            elif low1 not in s1 and high2 in s2:
                s3 = Interval((low1, high2), Singleton(high2))
            else:
                raise RuntimeError("impossible!")
            return s3
        return s1, s2
