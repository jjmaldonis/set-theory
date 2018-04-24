from set_theory import Singleton, Interval, Set


# Use hypothesis for testing instead if I can.

def test_interval_1():
    s1 = Interval([2,5])
    assert s1.lclosed
    assert s1.rclosed
    assert not s1.lopen
    assert not s1.ropen
    assert 2 in s1
    assert 5 in s1
    assert 3 in s1
    assert 0 not in s1
    assert 6 not in s1


def test_1():
    s1 = Interval([2,5])
    s2 = Singleton(5)
    assert s2 in s1


def test_2():
    s = Set(
        Interval((0, 1), Singleton(0)),
        Interval((1, 3), Singleton(3)),
        Interval((1, 4)),
        Interval([2, 5]),
        Singleton(5),
        Singleton(6))
    assert not (1 in s)
    assert 0 in s
    assert 0.5 in s
    assert 5 in s
    assert 6 in s
    assert not (6+1e-12 in s)
    assert not (6-1e-12 in s)


def test_3():
    s1 = Set(Interval((0, 5)))
    s2 = Set(Interval((3, 5), Singleton(3)), Interval((0, 3), Singleton(3)))
    assert s1 == s2


def test_4():
    s1 = Set(Interval((0, 5)))
    s2 = Set(Interval((3, 5), Singleton(3)), Interval((0, 3)))
    assert s1 != s2

def test_5():
    s1 = Set(Singleton(0))
    assert s1 == s1
    assert not (s1 != s1)
    assert not (s1 < 0)
    assert not (s1 < s1)
    assert not (s1 > s1)
    assert s1 <= s1
    assert s1 >= s1
    assert s1 < 1e-12
    assert 0 in s1 and 1e-12 not in s1

    s2 = Set(Interval([0,1]))
    assert 0 in s2 and 1 in s2
    assert 0.5 in s2
    s3 = Set(Interval((0,1), Singleton(1)))
    assert 0 not in s3 and 1 in s3
    assert 0.5 in s3
    s4 = Set(Interval((0,1), Singleton(0)))
    assert 0 in s4 and 1 not in s4
    s5 = Set(Interval((0,1)))
    assert 0 not in s5 and 1 not in s5
    s6 = Set(Interval([0, 1]))
    assert 0 in s6 and 1 in s6
    assert s2 == s6

    i3 = Interval((0,1), Singleton(1))
    assert i3 in i3

    assert s1 < s3
    assert s1 in s2 and s1 not in s3 and s1 in s4 and s1 not in s5 and s1 in s6
    assert s2 not in s1 and s2 in s2 and s2 not in s3 and s2 not in s4 and s2 not in s5 and s2 in s6
    assert s3 not in s1 and s3 in s2 and s3 in s3 and s3 not in s4 and s3 not in s5 and s3 in s6
    assert s4 not in s1 and s4 in s2 and s4 not in s3 and s4 in s4 and s4 not in s5 and s4 in s6
    assert s5 not in s1 and s5 in s2 and s5 in s3 and s5 in s4 and s5 in s5 and s5 in s6