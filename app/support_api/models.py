from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    product: str
    amount: float
    status: str = "delivered"  # placed | shipped | delivered | refunded


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_email: str = Field(index=True)
    category: str
    message: str
    status: str = "open"
    created_at: datetime = Field(default_factory=utc_now)