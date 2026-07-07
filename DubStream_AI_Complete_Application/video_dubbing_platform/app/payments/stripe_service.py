import stripe
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models import User, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    async def create_customer(user_id: str, email: str, name: str):
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"user_id": user_id}
        )
        return customer.id
    
    @staticmethod
    async def create_subscription(customer_id: str, price_id: str, db: Session, user_id: str):
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )
        
        db_sub = Subscription(
            user_id=user_id,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer_id,
            status=subscription.status,
            current_period_end=subscription.current_period_end
        )
        db.add(db_sub)
        db.commit()
        return subscription
    
    @staticmethod
    async def cancel_subscription(subscription_id: str):
        return stripe.Subscription.delete(subscription_id)
    
    @staticmethod
    async def handle_webhook(event: dict, db: Session):
        if event["type"] == "customer.subscription.updated":
            stripe_sub_id = event["data"]["object"]["id"]
            status = event["data"]["object"]["status"]
            
            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_sub_id
            ).first()
            if sub:
                sub.status = status
                db.commit()
        
        elif event["type"] == "customer.subscription.deleted":
            stripe_sub_id = event["data"]["object"]["id"]
            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_sub_id
            ).first()
            if sub:
                sub.status = "canceled"
                db.commit()
