from django.urls import path
from . import views

urlpatterns = [
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/<str:tx_ref>/', views.verify_payment, name='verify_payment'),
]
