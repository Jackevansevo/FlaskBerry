from flask_mail import Message

from .models import Customer
from celery.schedules import crontab
from pony.orm import db_session

from . import app, mail, celery


@celery.task
def send_async_email(title, recipients, body, html=None):
    """Background task to send an email with Flask-Mail"""
    print('sending email')
    with app.app_context():
        msg = Message(title, recipients=recipients, body=body, html=html)
        mail.send(msg)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(
        5.0, send_reminder_emails.s(), name='Send reminder emails'
    )

    # Executes every morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30),
        send_reminder_emails.s(),
        'Daily book return reminder'
    )


@celery.task
@db_session
def send_reminder_emails():
    # Find all the Customers with unreturned loans
    customers = Customer.select()
    for customer in customers:
        outstanding_loans = customer.unreturned_loans
        if outstanding_loans:
            for loan in outstanding_loans:
                send_async_email.delay(
                    "return your books jackass",
                    [customer.email],
                    "please return your books"
                )
