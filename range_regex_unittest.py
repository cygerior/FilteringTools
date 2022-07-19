import unittest

from range_regex import RangeRegex


class MyTestCase(unittest.TestCase):

    @unittest.skip("Not working yet: will perhaps be abandoned")
    def test_range_split(self):
        self.assertEqual(
            [(1, 9)],
            RangeRegex.split_range(1, 9)
        )
        self.assertEqual(
            [(9, 9)],
            RangeRegex.split_range(9, 9)
        )
        self.assertEqual(
            [(1, 9), (10, 10)],
            RangeRegex.split_range(1, 10)
        )
        self.assertEqual(
            [(1, 9), (10, 99)],
            RangeRegex.split_range(1, 99)
        )
        self.assertEqual(
            [(8, 9), (10, 59), (60, 65)],
            RangeRegex.split_range(8, 65)
        )
        self.assertEqual(
            [(54, 59), (60, 99), (100, 999), (1000, 1199), (1200, 1229), (1230, 1234)],
            RangeRegex.split_range(54, 1234)
        )


if __name__ == '__main__':
    unittest.main()
