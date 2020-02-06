import enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID


db = SQLAlchemy()
BaseModel = db.make_declarative_base(db.Model)


class ItemType(enum.Enum):
    computers = "computers"
    electronics = "electronics"
    furniture = "furniture"
    jewelry = "jewelry"


class Item(BaseModel):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    item_uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    item_type = db.Column(db.Enum(ItemType))
    item_cost = db.Column(db.Numeric(precision=12, scale=2), index=True)
    item_sku = db.Column(db.String(32), nullable=False, index=True)
    item_title = db.Column(db.String(64))
    warranties = db.relationship("Warranty", backref="item", lazy=True)

    def __repr__(self):
        return '<Item {} "{}">'.format(self.item_uuid, self.item_title)


class Store(BaseModel):
    __tablename__ = 'stores'
    store_id = db.Column(db.Integer, primary_key=True)
    store_uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    store_name = db.Column(db.String(32), nullable=False, index=True)
    warranties = db.relationship("Warranty", backref="item", lazy=True)

    def __repr__(self):
        return '<Store {} "{}">'.format(self.store_uuid, self.store_name)


class Constraint(BaseModel):
    """Constraints defined here govern what Warranties are available for a
    given item_type and item_cost

    given the following:

    item_type | min_cost | max_cost | warranty_price | warranty_duration_months
    ----------+----------+----------+----------------+-------------------------
    furniture | 0.00     | 100.00   | 5.00           | 12
    ----------+----------+----------+----------------+-------------------------
    furniture | 0.00     | 100.00   | 10.00          | 36
    ----------+----------+----------+----------------+-------------------------
    furniture | 0.00     | 100.00   | 50.00          | 0 (lifetime)
    ----------+----------+----------+----------------+-------------------------
    furniture | 100.01   | 500.00   | 15.00          | 12
    ----------+----------+----------+----------------+-------------------------
    furniture | 100.01   | 500.00   | 20.00          | 24
    ----------+----------+----------+----------------+-------------------------

    a search for warranty terms for (item_type=furniture, item_cost=75.00) will
    return the first 3 rows
    """
    __tablename__ = 'constraints'
    __table_args__ = (
        db.UniqueConstraint('item_type', 'min_cost', 'max_cost',
                            'warranty_price', 'warranty_duration_months'),
    )

    constraint_id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.Enum(ItemType))
    min_cost = db.Column(db.Numeric(precision=6, scale=2), index=True, nullable=False)
    max_cost = db.Column(db.Numeric(precision=6, scale=2), index=True, nullable=False)
    warranty_price = db.Column(db.Numeric(precision=6, scale=2), index=True, nullable=False)
    warranty_duration_months = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Constraint {}:{}-{}-{}-{}-{}>'.format(self.constraint_id,
                                                       self.item_type,
                                                       self.min_cost,
                                                       self.max_cost,
                                                       self.warranty_price,
                                                       self.warranty_duration_months)


class Warranty(BaseModel):
    __tablename__ = 'warranties'

    warranty_id = db.Column(db.Integer, primary_key=True)
    warranty_uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
    warranty_price = db.Column(db.Numeric(precision=6, scale=2), index=True, nullable=False)
    warranty_duration_months = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Warranty {}>'.format(self.warranty_uuid)

