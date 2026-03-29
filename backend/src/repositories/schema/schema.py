
    # # Relationships
    # customer = relationship("Customer", back_populates="orders")
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String)
    mail = Column(String)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, default="SYSTEM")

    modified_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    modified_by = Column(String, default="SYSTEM")

    # Relationships
    orders = relationship(
        "Order",
        back_populates="customer")


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    available_quantity = Column(Integer)

    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, default="SYSTEM")

    modified_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    modified_by = Column(String, default="SYSTEM")

    # Relationships
    order_items = relationship(
        "OrderItem",
        back_populates="item"
    )


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id")
    )

    status = Column(String)
    total_price = Column(Integer)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, default="SYSTEM")

    modified_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    modified_by = Column(String, default="SYSTEM")

    # Relationships
    customer = relationship(
        "Customer",
        back_populates="orders"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="order"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_items_id = Column(Integer, primary_key=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id")
    )

    item_id = Column(
        Integer,
        ForeignKey("items.item_id")
    )

    quantity = Column(Integer)
    price = Column(Integer)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, default="SYSTEM")

    modified_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    modified_by = Column(String, default="SYSTEM")

    # Relationships
    order = relationship(
        "Order",
        back_populates="order_items"
    )

    item = relationship(
        "Item",
        back_populates="order_items"
    )
    


class ErrorLog(Base):

    __tablename__ = "error_logs"

    error_log_id = Column(Integer, primary_key=True)

    function_name = Column(String)
    file_name = Column(String)
    error = Column(String)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, default="SYSTEM")

    modified_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    modified_by = Column(String, default="SYSTEM")