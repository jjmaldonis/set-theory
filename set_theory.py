import re
import copy
from itertools import combinations


class SingleTSet(object):
    set_pattern = re.compile("(\[|\()\s*(\d*\.*\d*)\s*,\s*(\d*\.*\d*)\s*(\)|\])")

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

    def __init__(self, single):
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
            raise ValueError(lower)

    @property
    def hbound(self):
        if self.hclosed:
            return "]"
        elif self.hopen:
            return ")"
        else:
            raise ValueError(higher)

    def __contains__(self, num_or_set):
        if isinstance(num_or_set, int) or isinstance(num_or_set, float):
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

    def __eq__(self, other):
        return self.low == other.low and self.high == other.high and self.lopen == other.lopen and self.hopen == other.hopen

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        # [0] < [1]
        # [0] > [-1]
        # ..., 1) < [1, ...
        # ..., 1) < (1, ...
        # ..., 1] < (1, ...
        # ..., 1] !< [1, ...
        if isinstance(other, int) or isinstance(other, float):
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

    def __gt__(self, other):
        return self != other and not self < other

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other



class TSet(object):
    def __init__(self, *one_or_many):
        if len(one_or_many) == 1:
            one_or_many = one_or_many[0]
        if isinstance(one_or_many, str) or isinstance(one_or_many, int) or isinstance(one_or_many, float):
            # one
            singles = [SingleTSet(one_or_many)]
        else:
            # many
            singles = [SingleTSet(one) for one in one_or_many]
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
        # Sort, using SingleTSet order
        unique.sort(key=lambda s: s.low)
        unique.sort()
        self.singles = unique

    def __str__(self):
        return "{{{}}}".format(", ".join(str(single) for single in self.singles))

    def __contains__(self, other):
        if isinstance(other, SingleTSet) or isinstance(other, int) or isinstance(other, float):
            return any(other in single for single in self.singles)
        else:  # Assume `TSet`
            return all(
                any(other_single in single for single in self.singles)
                    for other_single in other.singles
            )

    def __eq__(self, other):
        if isinstance(other, SingleTSet):
            return len(self.singles) == 1 and self.singles[0] == other
        else:  # Assume `TSet`
            return len(self.singles) == len(other.singles) and all(s == o for s, o in zip(self.singles, other.singles))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, SingleTSet):
            return all(s < other for s in self.singles)
        else:  # Assume `TSet`
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
    def merge_two(s1, s2):
        # Assume both are SingleTSet's
        s1, s2 = sorted([s1, s2], key=lambda s: s.low)
        s1, s2 = sorted([s1, s2])

        if s1 in s2:  # (0, 5) and (1, 2)
            return copy.deepcopy(s2)
        if s2 in s1:
            return copy.deepcopy(s1)
        # (0, 2) and (1, 3)
        # OR
        # (0, 1] and [1, 2)
        if s1.high > s2.low or \
           s1.high == s2.low and s1.hclosed and s2.lclosed:
            s3 = SingleTSet("{}{}, {}{}".format(s1.lbound, s1.low, s2.high, s2.hbound))
            return s3
        return s1, s2



def test():
    # Use hypothesis for testing instead if I can.
    # All the below should be True

    s1 = SingleTSet("[2,5]")
    s2 = SingleTSet(5)
    print(s2 in s1)

    s = TSet("[0, 1)", "(1, 3]", "(1, 4)", "[2, 5]", 5, 6)
    print(not (1 in s))
    print(0 in s)
    print(0.5 in s)
    print(5 in s)
    print(6 in s)
    print(not (6+1e-12 in s))
    print(not (6-1e-12 in s))

    s1 = TSet("(0, 5)") == TSet("[3, 5)", "(0, 3]")
    print(s1)

    s1 = TSet(0)
    print(s1 == s1)
    print(not (s1 != s1))
    print(not (s1 < 0))
    print(not (s1 < s1))
    print(not (s1 > s1))
    print(s1 <= s1)
    print(s1 >= s1)
    print(s1 < 1e-12)
    print(0 in s1 and 1e-12 not in s1)
    s2 = TSet("[0,1]")
    print(0 in s2 and 1 in s2)
    s3 = TSet("(0,1]")
    print(0 not in s3 and 1 in s3)
    s4 = TSet("[0,1)")
    print(0 in s4 and 1 not in s4)
    s5 = TSet("(0,1)")
    print(0 not in s5 and 1 not in s5)
    s6 = TSet("[0, 1]")
    print(0 in s6 and 1 in s6)
    print(s2 == s6)

    print(s1 < s3)
    print(s1 in s2 and s1 not in s3 and s1 in s4 and s1 not in s5 and s1 in s6)
    print(s2 not in s1 and s2 in s2 and s2 not in s3 and s2 not in s4 and s2 not in s5 and s2 in s6)
    print(s3 not in s1 and s3 in s2 and s3 in s3 and s3 not in s4 and s3 not in s5 and s3 in s6)
    print(s4 not in s1 and s4 in s2 and s4 not in s3 and s4 in s4 and s4 not in s5 and s4 in s6)
    print(s5 not in s1 and s5 in s2 and s5 in s3 and s5 in s4 and s5 in s5 and s5 in s6)



if __name__ == "__main__":
    test()

