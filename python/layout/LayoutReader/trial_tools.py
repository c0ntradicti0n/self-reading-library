import numpy


def range_parameter(n_tuple, n=3):
    low = min(n_tuple)
    high = max(n_tuple)
    step = (high - low)/n
    yield from numpy.arange(low, high+step, step)


import unittest

class ListToolsTest(unittest.TestCase):
    def test_n_tuple(self):
        s_tuple = (10,40,70)
        print (list(range_parameter(s_tuple)))


if __name__ == '__main__':
    unittest.main()


