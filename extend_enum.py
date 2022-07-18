from enum import EnumMeta, Enum
from unittest import TestCase


class ExtEnumMeta(EnumMeta):
    pass


class ExtEnum(metaclass=EnumMeta):
    pass


class EnBase(ExtEnum):
    VAL1 = 10
    VAL2 = 33


en = Enum()


class ExtEnumTestCase(TestCase):
    def test_base_iter(self):
        self.assertEqual([EnBase.VAL1, EnBase.VAL2], [item for item in EnBase])

    def test_ext_iter(self):
        class En1(Enum):
            VAL4 = 43

