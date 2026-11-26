from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.support_api.models import Customer, Order, Ticket

app = FastAPI(title="Support API")


@app.get("/customers/{email}/orders")
def list_orders(email: str, db: Session = Depends(get_session)):
    customer = db.exec(select(Customer).where(Customer.email == email)).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    return db.exec(select(Order).where(Order.customer_id == customer.id)).all()


@app.post("/orders/{order_id}/refund")
def refund_order(order_id: int, db: Session = Depends(get_session)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    order.status = "refunded"
    db.add(order)
    db.commit()
    return {"order_id": order_id, "status": "refunded", "amount": order.amount}


@app.post("/tickets")
def create_ticket(ticket: Ticket, db: Session = Depends(get_session)):
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket