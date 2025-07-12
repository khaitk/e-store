import os
import stripe
from app.models.schemas import StripePaymentIntent

stripe.api_key = os.getenv("STRIPE_API_KEY")

class StripeService:
    @staticmethod
    def create_payment_intent(amount: float, currency: str = "vnd", metadata: dict = None) -> StripePaymentIntent:
        """
        Create a payment intent in Stripe
        """
        try:
            # Convert to smallest currency unit (e.g., cents for USD)
            amount_in_smallest_unit = int(amount)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_in_smallest_unit,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            
            return StripePaymentIntent(
                client_secret=intent.client_secret,
                payment_intent_id=intent.id
            )
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str):
        """
        Retrieve a payment intent from Stripe
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def refund_payment(payment_intent_id: str, amount: float = None):
        """
        Refund a payment
        """
        try:
            refund_params = {"payment_intent": payment_intent_id}
            
            # If amount is specified, add it to the refund parameters
            if amount is not None:
                refund_params["amount"] = int(amount)
            
            return stripe.Refund.create(**refund_params)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def construct_event(payload, sig_header, webhook_secret):
        """
        Construct a Stripe event from webhook payload
        """
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise Exception("Invalid signature")
