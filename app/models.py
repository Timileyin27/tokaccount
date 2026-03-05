from app.database import Base, engine,get_db
from sqlalchemy import Column, Integer, String, TIMESTAMP,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy import Enum as SqlEnum
from enum import Enum 

class User (Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
   
class Account (Base):
    __tablename__="account_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name= Column(String, nullable=False)
    price = Column(Float, nullable=False)
    amount_in_stock = Column(Integer, nullable=False)
    amount_sold = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Order (Base):
    __tablename__="orders"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    status= Column(SqlEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    total_amount = Column(Float, nullable=False)
    customer_email = Column(String, nullable=False)


class CartStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CHECKED_OUT = "CHECKED_OUT"
    EXPIRED = "EXPIRED"
class Cart (Base):
    __tablename__="cart"
    id = Column(Integer, primary_key=True, nullable=False)
    status= Column(SqlEnum(CartStatus), default=CartStatus.ACTIVE, nullable=False)
    cart_reference = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    expire_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now() + interval \'50 minutes\''))
class CartItem (Base):
    __tablename__="cart_item"
    id = Column(Integer, primary_key=True, nullable=False)
    cart_id = Column(Integer, ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(Integer, ForeignKey("account_type.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_at_addition = Column(Float, nullable=False)
    account = relationship("Account")
class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
class Payment (Base):
    __tablename__="payment"
    id = Column(Integer, primary_key=True, nullable=False)
    reference= Column(String, nullable=False, unique=True)
    provider = Column(String, nullable=False)
    provider_reference = Column(String, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    status= Column(SqlEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    paid_at = Column(TIMESTAMP(timezone=True), nullable=True)