from datetime import date
from unittest import TestCase

from utils import get_date_index


class TestUtils(TestCase):

    def test_get_date_index(self):
        date_zero = date(2023, month=12, day=31)

        self.assertEqual(61, get_date_index("01-03-2024", date_zero),
                         "It needs to be index 31 for January + 29 for February + 1 for March. So 61")

