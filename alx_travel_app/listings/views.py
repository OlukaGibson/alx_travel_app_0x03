import os
import requests
from django.http import JsonResponse
from .models import Payment
from rest_framework import viewsets
from .models import Booking
from .serializers import BookingSerializer
from .tasks import send_booking_confirmation_email

CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')
CHAPA_BASE_URL = 'https://api.chapa.co/v1'

def initiate_payment(request):
    # Example: booking_reference and amount should come from request.POST or JSON
    booking_reference = request.POST.get('booking_reference')
    amount = request.POST.get('amount')
    email = request.POST.get('email')

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "first_name": "John",
        "last_name": "Doe",
        "tx_ref": booking_reference,
        "callback_url": "http://yourdomain.com/payment/callback/",
        "return_url": "http://yourdomain.com/payment/success/",
        "customization[title]": "Travel Booking Payment",
        "customization[description]": "Payment for booking"
    }

    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}"
    }

    response = requests.post(f"{CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if data.get('status') == 'success':
        Payment.objects.create(
            booking_reference=booking_reference,
            transaction_id=data['data']['tx_ref'],
            amount=amount,
            status='Pending'
        )
        return JsonResponse({"checkout_url": data['data']['checkout_url']})
    else:
        return JsonResponse({"error": "Failed to initiate payment"}, status=400)


def verify_payment(request, tx_ref):
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}"
    }

    response = requests.get(f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}", headers=headers)
    data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

    if data.get('status') == 'success' and data['data']['status'] == 'success':
        payment.status = 'Completed'
        # You could trigger Celery to send confirmation email here
    else:
        payment.status = 'Failed'

    payment.save()
    return JsonResponse({"payment_status": payment.status})

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        user_email = booking.user.email
        listing_name = booking.listing.name

        # Call the Celery task asynchronously
        send_booking_confirmation_email.delay(user_email, listing_name)