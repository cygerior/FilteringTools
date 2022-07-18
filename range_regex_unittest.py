import unittest

from range_regex import RangeRegex, MatchPattern, RangeSubMatcher, RangeListSubMatcher, MatchSinglePattern


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

    def test_multi_groups(self):
        matcher = MatchPattern('Test[1-45]item[0-zz]Any*suffix')
        self.assertTrue(matcher.match('Test22itemAAAny!!gh!!suffix'))
        self.assertTrue(matcher.match('Test1item0Any_xxx_suffix'))
        self.assertTrue(matcher.match('Test45itemzzAnysuffix'))
        self.assertFalse(matcher.match('Test46itemAAAny!!gh!!suffix'))
        self.assertFalse(matcher.match('Test22item100Any...suffix'))
        self.assertFalse(matcher.match('est46itemAAAny!!gh!!suffix'))
        self.assertFalse(matcher.match('Test46itemAAAny!!gh!!suffi'))
        self.assertFalse(matcher.match('Test46itemAAbny!!gh!!suffix'))
        self.assertTrue(matcher.match('Test00022item000Any!!gh!!suffix'))

    def test_multi_range(self):
        self.assertTrue(MatchPattern('Test_[1-3,12-15]').match('Test_1'))
        self.assertTrue(MatchPattern('Test_[1-3,12-15]').match('Test_3'))
        self.assertTrue(MatchPattern('Test_[1-3,12-15]').match('Test_12'))
        self.assertTrue(MatchPattern('Test_[1-3,12-15]').match('Test_15'))
        self.assertFalse(MatchPattern('Test_[1-3,12-15]').match('Test_4'))
        self.assertFalse(MatchPattern('Test_[1-3,12-15]').match('Test_11'))
        self.assertFalse(MatchPattern('Test_[1-3,12-15]').match('Test_0'))
        self.assertFalse(MatchPattern('Test_[1-3,12-15]').match('Test_16'))

    def test_multi_complex_range(self):
        self.assertTrue(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_1'))
        self.assertTrue(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_5'))
        self.assertTrue(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_15'))
        self.assertTrue(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_34'))
        self.assertTrue(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_001'))
        self.assertFalse(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_2'))
        self.assertFalse(MatchPattern('Test_[1, 5-7, 12 | 15-34]').match('Test_000'))

    def test_multi_pattern(self):
        self.assertTrue(MatchPattern('TestA, TestString').match('TEstA'))
        self.assertTrue(MatchPattern('TestA, TestString').match('TestStrIng'))
        self.assertTrue(MatchPattern('Test[a,c], TestString').match('TestC'))
        self.assertTrue(MatchPattern('Test[a,c], TestString').match('TestString'))

    def test_pattern_to_be_escaped(self):
        self.assertTrue(MatchPattern('Test.[1-5]').match('TEst.3'))
        self.assertFalse(MatchPattern('Test.A.[1-5]').match('TEstAA.3'))
        self.assertFalse(MatchPattern('Test.A.[1-5]k').match('TEstAA.3k3'))

    def test_range_matcher_generate(self):
        self.assertEqual(['1', '2', '3', '4', '5'], list(RangeSubMatcher('[1-5]').generate()))
        self.assertEqual(['1', '2', '3', '5'], list(RangeListSubMatcher('[1-3, 5]').generate()))

    def test_match_pattern_generate(self):
        self.assertEqual([
            'Toto1',
            'Toto2'
        ],
            list(MatchPattern('Toto[1-2]').generate())
        )
        self.assertEqual([
            'Toto1.5',
            'Toto1.6',
            'Toto2.5',
            'Toto2.6',
        ],
            list(MatchPattern('Toto[1-2].[5,6]').generate())
        )
        self.assertEqual([
            'Toto1.5',
            'Toto1.6',
            'Toto2.5',
            'Toto2.6',
            'Blabla3',
            'Blabla4',
            'Blabla5'
        ],
            list(MatchPattern('Toto[1-2].[5,6], Blabla[3-5]').generate())
        )

    def test_range_base10(self):
        self.assertEqual([
            'Toto9', 'Toto10'
            ],
            list(MatchPattern('Toto[9-10:10]').generate())
        )

    def test_range_default_base(self):
        self.assertEqual([
            'Toto9',
            'TotoA',
            'TotoB',
            'TotoZ',
            'Toto10'
            ],
            list(MatchPattern('Toto[9-b, z-10]').generate()))

        self.assertEqual([
            'Toto9', 'Toto10'
        ],
            list(MatchPattern('Toto[9-10]', default_base=10).generate())
        )

    def test_range_mixed_base(self):
        self.assertEqual([
            'TotoF.99',
            'TotoF.100',
            'Toto10.99',
            'Toto10.100',
        ],
            list(MatchPattern('Toto[f-10:16].[99-100:10]').generate()))


if __name__ == '__main__':
    unittest.main()
