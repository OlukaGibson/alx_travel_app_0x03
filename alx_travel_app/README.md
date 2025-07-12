# ALX Travel App 0x03 — Background Tasks with Celery

This Django project demonstrates how to offload tasks using Celery and RabbitMQ, with a focus on sending asynchronous booking confirmation emails.

## ✅ Features
- Celery integration with RabbitMQ
- Background email task for new bookings
- Automatic email sending using Django's email backend
- BookingViewSet triggers task on create

## 🔧 Setup

### 1. Install RabbitMQ
```bash
sudo apt-get install rabbitmq-server
sudo service rabbitmq-server start

