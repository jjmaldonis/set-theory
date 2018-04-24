from settheory import Set, MultiSet

EPS = 1e-12


def test():
    # Use hypothesis for testing instead if I can.
    # All the below should be True

    s1 = MultiSet(0)
    s2 = MultiSet(0)
    s3 = s1 | s2
    assert s3 == s1

    s1 = MultiSet('(2,5)')
    s2 = MultiSet(5)
    s3 = s1 | s2
    assert len(s3.singles) == 1

    s1 = Set('[2,5]')
    s2 = Set(5)
    assert s2 in s1

    s = MultiSet('[0, 1)', '(1, 3]', '(1, 4)', '[2, 5]', 5, 6)
    assert not (1 in s)
    assert 0 in s
    assert 0.5 in s
    assert 5 in s
    assert 6 in s
    assert not (6+EPS in s)
    assert not (6-EPS in s)

    s1 = MultiSet('(0, 5)') == MultiSet('[3, 5)', '(0, 3]')
    assert s1

    s1 = MultiSet(0)
    assert s1 == s1
    assert not (s1 != s1)
    assert not (s1 < 0)
    assert not (s1 < s1)
    assert not (s1 > s1)
    assert s1 <= s1
    assert s1 >= s1
    assert s1 < EPS
    assert 0 in s1 and EPS not in s1
    s2 = MultiSet('[0,1]')
    assert 0 in s2 and 1 in s2
    s3 = MultiSet('(0,1]')
    assert 0 not in s3 and 1 in s3
    s4 = MultiSet('[0,1)')
    assert 0 in s4 and 1 not in s4
    s5 = MultiSet('(0,1)')
    assert 0 not in s5 and 1 not in s5
    s6 = MultiSet('[0, 1]')
    assert 0 in s6 and 1 in s6
    assert s2 == s6

    assert s1 < s3
    assert s1 in s2 and s1 not in s3 and s1 in s4 and s1 not in s5 and s1 in s6
    assert s2 not in s1 and s2 in s2 and s2 not in s3 and s2 not in s4 and s2 not in s5 and s2 in s6
    assert s3 not in s1 and s3 in s2 and s3 in s3 and s3 not in s4 and s3 not in s5 and s3 in s6
    assert s4 not in s1 and s4 in s2 and s4 not in s3 and s4 in s4 and s4 not in s5 and s4 in s6
    assert s5 not in s1 and s5 in s2 and s5 in s3 and s5 in s4 and s5 in s5 and s5 in s6


def test_disjointness():
    s1 = MultiSet(0)
    s2 = MultiSet('(0, 1)')
    assert s1.is_disjoint(s2) and s2.is_disjoint(s1)
    s1 = MultiSet(0)
    s2 = MultiSet('[0, 1)')
    assert not s1.is_disjoint(s2) and not s2.is_disjoint(s1)
    s1 = MultiSet('[0, 1)')
    s2 = MultiSet('[1, 2)')
    assert s1.is_disjoint(s2) and s2.is_disjoint(s1)
    s1 = MultiSet('[0, 1]')
    s2 = MultiSet('[1, 2)')
    assert not s1.is_disjoint(s2) and not s2.is_disjoint(s1)


def test_size():
    s1 = MultiSet(0)
    assert s1.size() == 0
    s2 = MultiSet('(0, 1)')
    assert s2.size() == 1
    s3 = MultiSet('[0, 1]', '[1, 2]', '[3, 10]')
    assert s3.size() == 9


def test_infinity():
    s1 = Set('(-inf, inf)')
    assert s1.size() == float('inf')
    s2 = Set("(-1, 1)")
    assert s1.intersection(s1, s2) == s2


    # TODO
    # test Set.merge on only two sets (see two use cases in Set._merge_two)
