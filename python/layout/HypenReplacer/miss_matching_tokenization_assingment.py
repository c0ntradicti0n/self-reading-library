import itertools
from collections import OrderedDict

from layouteagle.helpers.list_tools import partition_iterable


class MismatchingTokenisationManipulation:
    """ There are often things, that are divided differently. This class enables assigments to one kind of division
        resulting also in the devision of the other thing"""
    cuts1 = []
    cuts2 = []
    def __init__(self, version1) -> None:
        self.version1 = version1

    def join_with_next(self, fun_where):
        self.where = {}
        to_join = []
        it = self.version1.items()
        for (i_prev, w_prev), (i_follow, w) in pairwise(it):
            if not fun_where(w):
                self.where[i] = [i]
            else:
                self.where[i] = [i, i+1]
                to_join.append(i+1)
                next(it)

        for i in to_join ()

        print (self.where)



import unittest


class TestMismatchingTokenisationManipulation(unittest.TestCase):
    def test_hyphen(self):
        tokenisation = dict(enumerate(["This", "sentence", "has", "a", "hy-", "phen", "."]))
        is_hyphen = lambda string: string.endswith('-')
        mtm = MismatchingTokenisationManipulation(tokenisation)
        mtm.join_with_next(is_hyphen)
        print (mtm.version2)
        assert all(w1==w2 for w1, w2 in zip(mtm.version2, should_be))
        assert mtm.ids2_to_ids11[4] == [3,3]
        assert mtm.ids2_to_ids11[4] == [4,5]



if __name__ == '__main__':

    unittest.main()
