
from morus.testing.base import MorusTestCase

from pplans.warranty import create_store_name, gen_warranty


class WarrantyTestCase(MorusTestCase):

    def test_create_store_name(self):
        name = create_store_name()
        self.assertTrue(name)
        self.assertTrue(" " in name)


    def test_gen_warranty(self):
        pass

    def test_get_warranties(self):
        pass

