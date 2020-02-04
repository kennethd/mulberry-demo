import random

def create_store_name():
    """A silly function for illustrating unit tests witin a service package"""
    W1 = ["ACME", "Apu's", "Corner", "Dollar", "General", "Harlem", "Moe's"]
    W2 = ["Markt", "Store", "Stuff", "Warehouse"]
    return " ".join([random.choice(W1), random.choice(W2)])

def gen_warranty(item_type, item_cost, store_uuid, item_sku):
    pass

def get_warranties(item_type=None, item_sku=None, store_uuid=None):
    pass

