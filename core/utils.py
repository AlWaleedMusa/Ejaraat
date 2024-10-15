from datetime import date
import calendar
import requests
from datetime import timedelta
from .models import Notifications, RecentActivity


def get_expiring_contracts(properties):
    """
    """
    return [
        rental
        for property in properties
        for rental in property.property_rentals.all()
        if rental.expiring_contracts()
    ]

def get_upcoming_payments(properties):
    """
    """
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
                    if today > due_date and rental.status != "paid":
                        if rental.status != "overdue":
                            rental.status = "overdue"
                            rental.save()
                        upcoming_payments.append(rental)
                    
                    # Handle pending payments due within 7 days
                    elif rental.status != "pending" and rental.status != "paid":
                        rental.status = "pending"
                        rental.save()
                        upcoming_payments.append(rental)

                    # Always append rentals due within 7 days, regardless of status
                    if rental not in upcoming_payments and rental.status != "paid":
                        upcoming_payments.append(rental)
            else:
                # Handle rentals with no more payments and unpaid/overdue status
                if rental.status != "paid" and rental.status != "overdue":
                    rental.status = "overdue"
                    rental.save()
                    upcoming_payments.append(rental)

    return upcoming_payments


def get_recent_activity(user):
    """
    """
    return RecentActivity.objects.filter(user=user).order_by("-timestamp")[:10]

def get_notifications(user):
    """
    """
    return Notifications.objects.filter(user=user, is_read=False)



# def convert_currency(amount, from_currency, to_currency="USD"):
#     """
#     """
#     url = f"https://v6.exchangerate-api.com/v6/5ea2b1bcbecc8661d649b429/latest/{from_currency}"
#     response = requests.get(url)
#     data = response.json()

#     if response.status_code == 200:
#         if to_currency in data["conversion_rates"]:
#             data = response.json()
#             rate = data["conversion_rates"][to_currency]
#             return amount * rate
#         else:
#             raise ValueError(f"conversion rate for {to_currency} not found")


# def get_monthly_earning(properties):
#     """
#     """
#     today = date.today()
#     month = today.month
#     year = today.year
#     monthly_earning = 0

#     for property in properties:
#         for rental in property.property_rentals.all():
#             if rental.start_date.month == month and rental.start_date.year == year:
#                 print(rental.price, rental.property.currency)
#                 converted_price = convert_currency(rental.price, rental.property.currency)
#                 print(converted_price)
#                 monthly_earning += converted_price

#     return monthly_earning