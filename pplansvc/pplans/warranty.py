"""
This is the library functions layer of the warranties_api applications.

This is the only layer that should be instantiating models and interacting
with the database.

Functions here should be entirely agnostic to and ignorant of any app context.
"""
import collections
import logging
import random

from morus.logging import getLogger
from pplans.models import db, Item, Store, Warranty, Constraint


log = getLogger(__name__)

WARRANTY_ERRORS = {
    "no crit": "No suitable criteria",
    "filter req": "Filter criteria is required",
}

class WarrantyRuntimeError(RuntimeError):
    pass


def create_store_name():
    """A silly function to illustrate unit testing libs witin a service package"""
    W1 = ["ACME", "Apu's", "Corner", "Dollar", "Harlem", "Moe's"]
    W2 = ["Markt", "Store", "Stuff", "Warehouse"]
    return " ".join([random.choice(W1), random.choice(W2)])


def warranty(item_cost, item_sku, item_title, item_type, store_uuid):
    log.debug("warranty args: {}".format(locals()))

    # check for available warranties for (item_type, item_cost) combo
    constraints = get_constraints(item_type, item_cost)
    log.debug("found constraints: {}".format(constraints))
    if not constraints:
        raise WarrantyRuntimeError(WARRANTY_ERRORS["no crit"])

    # Item has a UNIQUE constraint on (item_type, item_sku)
    wheres = [
        Item.item_type == item_type,
        Item.item_sku == item_sku,
    ]
    item = Item.query.filter(*wheres).first()
    if not item:
        item = Item(item_sku=item_sku, item_type=item_type)
    item.item_cost = item_cost
    item.item_title = item_title
    db.session.add(item)

    store = Store.query.filter(Store.store_uuid==store_uuid).first()
    if not store:
        store = Store(store_uuid=store_uuid, store_name=create_store_name())
    db.session.add(store)

    # commit any changes to db, generate pk ids
    db.session.commit()

    # for each warranty available for item, ensure row exists
    warranties = []
    for avail_warranty in constraints:
        attrs = {
            "item_id": item.item_id,
            "store_id": store.store_id,
            "warranty_price": avail_warranty["warranty_price"],
            "warranty_duration_months": avail_warranty["warranty_duration_months"],
        }
        warranties.append(attrs)
        warranty = Warranty(**attrs)
        db.session.add(warranty)

    db.session.commit()
    return warranties


def get_warranties(item_type="", item_sku="", item_uuid="", store_uuid=""):
    log.debug("get_warranties: {}".format(locals()))
    if not any([item_type, item_sku, item_uuid, store_uuid]):
        raise WarrantyRuntimeError(WARRANTY_ERRORS["filter req"])

    wheres = []
    if item_type:
        wheres.append(Item.item_type == item_type)
    if item_uuid:
        wheres.append(Item.item_uuid == item_uuid)
    if item_sku:
        wheres.append(Item.item_sku == item_sku)
    if store_uuid:
        wheres.append(Store.store_uuid == store_uuid)

    rs = Warranty.query.join(Warranty.item).join(Warranty.store).filter(*wheres).all()
    log.debug("get_warranties: {}".format(rs))

    ret = []
    for rec in rs:
        ret.append({
            "item_sku": rec.item.item_sku,
            "item_type": rec.item.item_type.value,
            "item_uuid": rec.item.item_uuid,
            "store_uuid": rec.store.store_uuid,
            "warranty_price": str(rec.warranty_price),
            "warranty_duration_months": rec.warranty_duration_months,
        })
    return ret


def get_constraints(item_type="", item_cost=""):
    log.debug("get_constraints: {}".format(locals()))

    wheres = []
    if item_type:
        wheres.append(Constraint.item_type == item_type)
    if item_cost:
        wheres.extend([
            Constraint.min_cost < item_cost,
            Constraint.max_cost > item_cost,
        ])
    rs = Constraint.query.filter(*wheres).all()

    ret = []
    for rec in rs:
        ret.append({
            "constraint_id": rec.constraint_id,
            "item_type": rec.item_type.value,
            "min_cost": str(rec.min_cost),
            "max_cost": str(rec.max_cost),
            "warranty_price": str(rec.warranty_price),
            "warranty_duration_months": rec.warranty_duration_months,
        })
    return ret


def create_demo_data():
    created = collections.defaultdict(list)

    s = Store(store_name=create_store_name())
    db.session.add(s)
    created["stores"].append(s)

    for row in [
        ("furniture", "FURN-123", "80.00", "Retro Kitchen Table"),
        ("furniture", "FURN-1234", "120.00", "Ken's Vintage Sofa"),
        ("electronics", "ELEC-999", "1200.00", "ARP Modular Synth"),
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
        ("electronics", "0.00", "999.99", "100.00", "36"),
        ("electronics", "1000.00", "1999.99", "150.00", "36"),
    ]:
        c = Constraint(item_type=row[0], min_cost=row[1], max_cost=row[2],
                       warranty_price=row[3], warranty_duration_months=row[4])
        db.session.add(c)
        created["constraints"].append(c)

    # commit to generate ids
    db.session.commit()

    item_one_id = created["items"][0].item_id
    item_two_id = created["items"][1].item_id
    item_three_id = created["items"][2].item_id
    store_id = created["stores"][0].store_id

    for row in [
        # item_cost=80.00 elig. for (5.00, 12), (10.00, 36), (50.00, 0)
        (store_id, item_one_id, 5.00, 12),
        (store_id, item_one_id, 10.00, 36),
        (store_id, item_one_id, 50.00, 0),
        # item_cost=120.00 elig. for (15.00, 12), (20.00, 24)
        (store_id, item_two_id, 15.00, 12),
        (store_id, item_two_id, 20.00, 24),
        # item_cost=1200.00 elig. for (150.00, 36)
        (store_id, item_three_id, 150.00, 36),
    ]:
        w = Warranty(store_id=row[0], item_id=row[1], warranty_price=row[2],
                     warranty_duration_months=row[3])
        db.session.add(w)
        created["warranties"].append(w)

    db.session.commit()
    return created

