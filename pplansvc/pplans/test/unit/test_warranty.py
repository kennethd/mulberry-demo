"""
Unit tests are used to test discrete functionality -- single functions or
methods of library code
"""
from morus.testing.base import MorusTestCase

from pplans.warranty import create_store_name


class WarrantyTestCase(MorusTestCase):

    def test_create_store_name(self):
        name = create_store_name()
        self.assertTrue(name)
        self.assertTrue(" " in name)

