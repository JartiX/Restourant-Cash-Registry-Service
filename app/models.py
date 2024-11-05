from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Boolean,
    Enum,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship
from app import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    passhash = db.Column(db.String(120), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_employee = db.Column(db.Boolean, default=False, nullable=False)
    is_manager = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    locations = relationship(
        "Location",
        secondary="user_location",
        back_populates="users",
        foreign_keys="[UserLocation.user_id, UserLocation.location_id]",
        cascade="all, delete-orphan",
    )
    purchases = relationship("Purchase", back_populates="user")
    stop_list = relationship("StopList", back_populates="user")
    stop_list_history = relationship("StopListHistory", back_populates="user")


class Location(db.Model):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    tax_id = Column(String, nullable=False)
    address = Column(String, nullable=False)

    users = relationship(
        "User",
        secondary="user_location",
        back_populates="locations",
        foreign_keys="[UserLocation.user_id, UserLocation.location_id]",
    )
    stop_list = relationship(
        "StopList", back_populates="location", cascade="all, delete-orphan"
    )
    stop_list_history = relationship(
        "StopListHistory", back_populates="location", cascade="all, delete-orphan"
    )


class UserLocation(db.Model):
    __tablename__ = "user_location"

    user_id = db.Column(db.Integer, ForeignKey("user.id"), primary_key=True)
    location_id = db.Column(db.Integer, ForeignKey("location.id"), primary_key=True)


class Product(db.Model):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float(asdecimal=True), nullable=False)

    stop_list = relationship("StopList", cascade="all, delete-orphan")
    purchase_items = relationship("PurchaseItem")


class StopList(db.Model):
    __tablename__ = "stop_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    remaining_quantity = Column(Integer, nullable=True)
    date_added = Column(DateTime, default=datetime.now(timezone.utc))

    product = relationship("Product", back_populates="stop_list")
    location = relationship("Location", back_populates="stop_lists")
    employee = relationship("User", back_populates="stop_list")


class StopListHistory(db.Model):
    __tablename__ = "stop_list_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    employee = Column(Integer, ForeignKey("user.id"), nullable=False)
    action = Column(Enum("added", "removed"), nullable=False)
    remaining_quantity = Column(Integer, nullable=False)
    datetime = Column(DateTime, default=datetime.now(timezone.utc))

    product = relationship("Product")
    location = relationship("Location")
    employee = relationship("User")


class Customer(db.Model):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    delivery_address = Column(String, nullable=True)
    birthday = Column(Date, nullable=True)
    block_status = Column(Boolean, default=False, nullable=False)
    discount = Column(Float(asdecimal=True), default=0)
    note = Column(String, nullable=True)

    purchases = relationship(
        "Purchase", back_populates="customer", cascade="all, delete-orphan"
    )


class Purchase(db.Model):
    __tablename__: str = "purchase"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=True)
    employee = Column(Integer, ForeignKey("user.id"), nullable=False)
    location_id = Column(String, ForeignKey("location.id"), nullable=False)
    total_before_tax = Column(Float(asdecimal=True), nullable=False)
    tax_amount = Column(Float(asdecimal=True), nullable=False)
    total = Column(Float(asdecimal=True), nullable=False)
    datetime = Column(DateTime, default=datetime.now(timezone.utc))
    table_number = Column(Integer, nullable=True)
    delivery_address = Column(String, nullable=True)
    promotion_id = Column(Integer, ForeignKey("promotion.id"), nullable=True)
    status = Column(
        Enum("accepted", "cancelled", "preparing", "prepared", "closed", "refunded"),
        nullable=False,
    )
    type = Column(Enum("dine-in", "delivery"), nullable=False)

    customer = relationship("Customer", cascade="save-update")
    purchase_items = relationship("PurchaseItem", cascade="save-update, delete-orphan")
    employee = relationship("user", cascade="none")
    promotion = relationship("Promotion", cascade="none")


class PurchaseItem(db.Model):
    __tablename__: str = "purchase_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("purchase.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    sale_price = Column(Float(asdecimal=True), nullable=False)

    purchase = relationship("Purchase", back_populates="purchase_items")
    product = relationship("Product")


class Promotion(db.Model):
    __tablename__: str = "promotion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    discount_percentage = Column(Float(asdecimal=True), nullable=True)
    discount_value = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)


models = [
    User,
    Location,
    UserLocation,
    Product,
    StopList,
    StopListHistory,
    Customer,
    Purchase,
    PurchaseItem,
    Promotion,
]
