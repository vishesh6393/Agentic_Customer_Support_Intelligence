import random
from datasets import load_dataset
from sqlmodel import Session, select
from app.db import engine, create_tables
from app.support_api.models import Customer, Order, Ticket

NAMES = ["Aarav Shah", "Priya Nair", "Rohan Gupta", "Ananya Iyer", "Vikram Rao",
         "Sneha Patel", "Arjun Mehta", "Kavya Reddy", "Rahul Verma", "Isha Kapoor"]
PRODUCTS = [("Wireless Earbuds", 2499), ("Smart Watch", 5999), ("Laptop Stand", 1299),
            ("USB-C Hub", 1899), ("Mechanical Keyboard", 4499), ("Bluetooth Speaker", 3299)]
STATUSES = ["placed", "shipped", "delivered"]
DATASET = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"


def add_customers_and_orders(db):
    for name in NAMES:
        email = name.lower().replace(" ", ".") + "@example.com"
        customer = Customer(name=name, email=email)
        db.add(customer)
        db.flush()
        for product, price in random.sample(PRODUCTS, k=2):
            db.add(Order(customer_id=customer.id, product=product,
                         amount=price, status=random.choice(STATUSES)))


def add_real_tickets(db, limit=300):
    emails = [c.email for c in db.exec(select(Customer)).all()]
    rows = load_dataset(DATASET, split="train").shuffle(seed=42).select(range(limit))
    for row in rows:
        db.add(Ticket(customer_email=random.choice(emails),
                      category=row["category"].lower(),
                      message=row["instruction"]))


def seed():
    create_tables()
    random.seed(42)
    with Session(engine) as db:
        if db.exec(select(Customer)).first():
            print("already seeded")
            return
        add_customers_and_orders(db)
        add_real_tickets(db)
        db.commit()
        print("done: 10 customers, 20 orders, 300 real tickets")


if __name__ == "__main__":
    seed()