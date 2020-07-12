"""
This file is intended to test some code replacements I'm making to the old v2.7 version of OpenOPC (and actually, to the
more recent OpenOPC-Python3x that appears to have understandably missed some code that works different under v3).

The tests are less to convince myself, and more to provide evidence in case I wind up issuing a PR to OpenOPC-Python3x.
"""
import logging
from sys import version_info
import unittest


class ZipTests(unittest.TestCase):
    """
    The problem solved by this code replacement is that in v2.7, `map(None, some_list, other_list)` would apply the
    identity function to each element it touched; in v3.8, it sets everything to None.

    Important criteria:
    1. Must return a list (not a generator/iterable)
    2. Must correctly fill missing values from shorter list with `None`, which implies len(result) == len(longest_list)
    3. Must preserve order
    4. Must produce elements which are tuples of the n-th item of each list
    """

    @classmethod
    def code_under_test_v2(cls, list_one, list_two):
        """Original code from module; demonstrates original behavior when run under v2.7"""
        return map(None, list_one, list_two)

    @classmethod
    def code_under_test_v3(cls, list_one, list_two):
        """New proposed code to replace problem code; demonstrates equivalent behavior when run under v3.8"""
        from itertools import zip_longest
        return list(zip_longest(list_one, list_two))

    @classmethod
    def setUpClass(cls):
        cls.alphas = ['a', 'b', 'c', 'd']
        cls.nums = [1, 2, 3, 4]

        logging.basicConfig(level=logging.DEBUG)
        if version_info.major == 3:
            logging.debug("Detected v3.x interpreter - setting code-under-test appropriately")
            cls.code_under_test = cls.code_under_test_v3
        elif version_info.major == 2:
            logging.debug("Detected v2.x interpreter - setting code-under-test appropriately")
            cls.code_under_test = cls.code_under_test_v2

    def test_return_type(self):
        self.assertIsInstance(self.code_under_test(self.alphas, self.nums), list)

    def test_matched_lengths_case_one(self):
        """Case 1: Input lists have equal length"""
        alphas, nums = self.alphas, self.nums
        self.assertEqual(len(self.code_under_test(alphas, nums)), len(alphas))
        self.assertEqual(len(self.code_under_test(alphas, nums)), len(nums))

    def test_mismatched_lengths_case_two(self):
        """Case 2: First list shorter"""
        alphas, nums = self.alphas[:2], self.nums
        result = self.code_under_test(alphas, nums)
        self.assertEqual(len(result), len(nums))
        self.assertIsNone(result[3][0])

    def test_mismatched_lengths_case_three(self):
        """Case 3: First list longer"""
        alphas, nums = self.alphas, self.nums[:2]
        result = self.code_under_test(alphas, nums)
        self.assertEqual(len(result), len(alphas))
        self.assertIsNone(result[3][1])

    def test_order(self):
        """Ensure order is preserved"""
        result = self.code_under_test(self.alphas, self.nums)
        for i, item in enumerate(result):
            self.assertEqual(result[i][0], self.alphas[i])
            self.assertEqual(result[i][1], self.nums[i])

    def test_elems_are_tuples(self):
        """Make sure elements of list are tuples"""
        result = self.code_under_test(self.alphas, self.nums)
        for item in result:
            self.assertIsInstance(item, tuple)


if __name__ == '__main__':
    unittest.main()
