from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(user_email, listing_name):
    """Send a booking confirmation email to the user."""
    subject = f'Booking Confirmation for {listing_name}'
    message = f'Thank you for booking {listing_name} on ALX Travel!'
    send_mail(subject, message, None, [user_email])
