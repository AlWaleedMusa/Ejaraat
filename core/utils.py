from datetime import date
import requests
import os
from .models import Notifications, RecentActivity


def get_expiring_contracts(properties):
    """ """
    return [
        rental
        for property in properties
        for rental in property.property_rentals.all()
        if rental.expiring_contracts()
    ]


def get_upcoming_payments(properties):
    """ """
    upcoming_payments = []
    today = date.today()

    for property in properties:
        for rental in property.property_rentals.all():
            next_payment = rental.get_next_payment()

            if next_payment:
                due_date, days_until_due = next_payment

                # Always show rentals with payments due within 7 days or overdue
                if days_until_due <= 7:
                    # Handle overdue payments
                    if today > due_date:
                        if rental.status != "overdue" and rental.status != "paid":
                            rental.status = "overdue"
                            rental.save()
                        upcoming_payments.append(rental)
                    else:
                        # Handle pending payments due within 7 days
                        if rental.status != "pending" and rental.status != "paid":
                            rental.status = "pending"
                            rental.save()
                            upcoming_payments.append(rental)

                        # Always append rentals due within 7 days, regardless of status
                        if rental not in upcoming_payments or rental.status != "paid":
                            upcoming_payments.append(rental)

                    if rental.status == "paid" and rental in upcoming_payments:
                        upcoming_payments.remove(rental)
            else:
                # Handle rentals with no more payments and unpaid/overdue status
                if rental.status != "paid" and rental.status != "overdue":
                    rental.status = "overdue"
                    rental.save()
                upcoming_payments.append(rental)

                if rental.status == "paid" and rental in upcoming_payments:
                    upcoming_payments.remove(rental)

    return upcoming_payments


def get_recent_activity(user):
    """ """
    return (
        RecentActivity.objects.filter(user=user)
        .exclude(activity_type="overdue")
        .order_by("-timestamp")[:10]
    )


def get_notifications(user):
    """ """
    return Notifications.objects.filter(user=user, is_read=False)


def convert_currency(amount, from_currency, to_currency="USD"):
    """ """
    url = f"https://v6.exchangerate-api.com/v6/{os.getenv('CURRENCY_CONVERTER_API')}/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if to_currency in data["conversion_rates"]:
            data = response.json()
            rate = data["conversion_rates"][to_currency]
            return amount * rate
        else:
            raise ValueError(f"conversion rate for {to_currency} not found")


def get_monthly_revenue(properties):
    """ """
    today = date.today()
    month = today.month
    year = today.year
    monthly_revenue = 0

    for property in properties:
        for rental in property.property_rentals.all():
            if rental.start_date.month == month and rental.start_date.year == year:
                # converted_price = convert_currency(rental.price, rental.property.currency)
                monthly_revenue += 1  # converted_price

    return monthly_revenue
