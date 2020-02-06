"""
This is the library functions layer of the warranties_api applications.

This is the only layer that should be instantiating models and interacting
with the database.

Functions here should be entirely agnostic to and ignorant of any app context.
"""
import collections
import logging
import random

from pplans.models import db, Item, Store, Warranty, Constraint


log = logging.getLogger(__name__)


def create_store_name():
    """A silly function to illustrate unit testing libs witin a service package"""
    W1 = ["ACME", "Apu's", "Corner", "Dollar", "Harlem", "Moe's"]
    W2 = ["Markt", "Store", "Stuff", "Warehouse"]
    return " ".join([random.choice(W1), random.choice(W2)])

def gen_warranty(item_type, item_cost, store_uuid, item_sku):
    pass

def get_warranties(item_type="", item_sku="", item_uuid="", store_uuid=""):
    log.debug("get_warranties: {}".format(locals()))
    crit = {
        "item_type": item_type,
        "item_uuid": item_uuid,
        "item_sku": item_sku,
        "store_uuid": store_uuid,
    }
    res = Warranty.query(
        Item.item_uuid,
        Item.item_type,
        Item.item_cost,
        Item.item_sku,
        Item.item_title,
        Store.store_uuid,
        Store.store_name,
        Warranty.warranty_price,
        Warranty.warranty_duration_month
    ).filter_by(**crit).all()
    log.debug("get_warranties: {}".format(res))
    ret = []
    for rec in res:
        ret.append({
            "item_sku": rec.item_sku,
            "item_type": rec.item_type,
            "item_uuid": rec.item_uuid,
            "store_uuid": rec.store_uuid,
            "warranty_price": rec.warranty_price,
            "warranty_duration_month": rec.warranty_duration_month,
        })
    return ret


def create_demo_data():
    created = collections.defaultdict(list)

    s = Store(store_name=create_store_name())
    db.session.add(s)
    created["stores"].append(s)

    for row in [
        ("furniture", "FURN-123", "80.00", "Amy's Sectional Sofa"),
        ("furniture", "FURN-1234", "120.00", "Ken's Vintage Sofa"),
    ]:
        i = Item(item_type=row[0], item_sku=row[1], item_cost=row[2], item_title=row[3])
        db.session.add(i)
        created["items"].append(i)

    for row in [
        ("furniture", "0.00", "100.00", "5.00", "12"),
        ("furniture", "0.00", "100.00", "10.00", "36"),
        ("furniture", "0.00", "100.00", "50.00", "0"),
        ("furniture", "100.01", "500.00", "15.00", "12"),
        ("furniture", "100.01", "500.00", "20.00", "24"),
    ]:
        c = Constraint(item_type=row[0], min_cost=row[1], max_cost=row[2],
                       warranty_price=row[3], warranty_duration_months=row[4])
        db.session.add(c)
        created["constraints"].append(c)

    # commit to generate ids
    db.session.commit()

    store_id = created["stores"][0].store_id
    item_one_id = created["items"][0].item_id
    item_two_id = created["items"][1].item_id

    for row in [
        # item_cost=80.00 elig. for (5.00, 12), (10.00, 36), (50.00, 0)
        (store_id, item_one_id, 5.00, 12),
        (store_id, item_one_id, 10.00, 36),
        (store_id, item_one_id, 50.00, 0),
        # item_cost=120.00 elig. for (15.00, 12), (20.00, 24)
        (store_id, item_two_id, 15.00, 12),
        (store_id, item_two_id, 20.00, 24),
    ]:
        w = Warranty(store_id=row[0], item_id=row[1], warranty_price=row[2],
                     warranty_duration_months=row[3])
        db.session.add(w)
        created["warranties"].append(w)

    db.session.commit()
    return created

