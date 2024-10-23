from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import os
import requests

from django.template.loader import get_template
from django.db.models import Count


def get_expiring_contracts(properties):
    """
    Retrieve a list of rentals with expiring contracts from a given list of properties.

    This function iterates over a list of properties and their associated rentals to find
    rentals with expiring contracts.

    Args:
        properties (QuerySet): A QuerySet of Property instances.

    Returns:
        list: A list of Rental instances with expiring contracts.
    """
    return [
        rental
        for property in properties
        for rental in property.property_rentals.all()
        if rental.expiring_contracts()
    ]


def get_upcoming_payments(properties):
    """
    Retrieve a list of rentals with upcoming payments from a given list of properties.

    This function iterates over a list of properties and their associated rentals to find
    rentals with payments due within the next 7 days or overdue payments.

    Args:
        properties (QuerySet): A QuerySet of Property instances.

    Returns:
        list: A list of Rental instances with upcoming payments.
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


def convert_currency(amount, from_currency, to_currency="USD"):
    """
    Convert an amount from one currency to another using the exchange rate API.

    This function fetches the latest exchange rates from the API and converts the given amount
    from the source currency to the target currency.

    Args:
        amount (float): The amount to be converted.
        from_currency (str): The source currency code.
        to_currency (str, optional): The target currency code. Defaults to "USD".

    Returns:
        float: The converted amount in the target currency.

    Raises:
        ValueError: If the conversion rate for the target currency is not found.
    """

    url = f"https://v6.exchangerate-api.com/v6/{os.getenv('CURRENCY_CONVERTER_API')}/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if to_currency in data["conversion_rates"]:
            rate = data["conversion_rates"][to_currency]
            return amount * rate
        else:
            raise ValueError(f"conversion rate for {to_currency} not found")


def get_monthly_revenue(properties):
    """
    Calculate the total monthly revenue for a given list of properties.

    This function iterates over a list of properties and their associated rentals to calculate
    the total revenue generated for the current month. It sums up the rental prices for rentals
    that are active during the current date.

    Args:
        properties (QuerySet): A QuerySet of Property instances.

    Returns:
        float: The total monthly revenue for the given properties.
    """
    today = date.today()
    temp = 0
    monthly_revenue = 0

    for property in properties:
        for rental in property.property_rentals.all():
            if rental.start_date <= today and rental.end_date >= today:

                rental_payment = int(rental.payment)
                if rental_payment == 1:
                    temp = rental.price * 30
                elif rental_payment == 7:
                    temp = rental.price * 4
                elif rental_payment == 30:
                    temp = rental.price
                elif rental_payment == 365:
                    temp = rental.price / 12

                # converted_price = convert_currency(
                #     temp, rental.property.currency
                # )
                monthly_revenue += 1 #converted_price

    return monthly_revenue


def clear_notification_service(user):
    """
    Clear the notifications for a given user.

    This function marks all unread notifications for a given user as read and returns the updated
    notifications HTML.

    Args:
        user (User): The user whose notifications are to be cleared.

    Returns:
        str: The updated notifications HTML.
    """

    from .models import Notifications

    Notifications.objects.filter(user=user).update(is_read=True)
    notifications = Notifications.objects.filter(user=user, is_read=False)
    notifications_html = get_template("includes/notifications.html").render(
        context={"notifications": notifications}
    )

    return notifications_html


def get_next_payment(payment, start_date, end_date):
    """
    Calculate the next payment date based on the payment interval.

    This function calculates the next payment date based on the payment interval (daily, weekly,
    monthly, or yearly) and the start date of the rental contract. It returns the next payment date
    and the number of days until the next payment is due.

    Args:
        payment (int): The payment interval in days.
        start_date (date): The start date of the rental contract.
        end_date (date): The end date of the rental contract.

    Returns:
        tuple: A tuple containing the next payment date and the number of days until the next payment.
    """

    interval_days = int(payment)
    today = date.today()
    current_payment_date = start_date

    while current_payment_date <= today and current_payment_date < end_date:
        if interval_days == 365:
            current_payment_date += relativedelta(years=1)
        elif interval_days == 30:
            current_payment_date += relativedelta(months=1)
        else:
            current_payment_date += timedelta(days=interval_days)

    if current_payment_date >= end_date:
        return None

    days_until_next_payment = (current_payment_date - today).days

    return current_payment_date, days_until_next_payment


def get_payment_status_chart(user):
    """
    Retrieve the payment status counts for a given user's properties.

    This function queries the database to get the count of payments with different statuses
    (paid, pending, overdue) for a given user's properties.

    Args:
        user (User): The user whose payment status counts are to be retrieved.

    Returns:
        dict: A dictionary containing the counts of payments with different statuses.
    """
    from .models import RentProperty

    payment_status_counts = (
        RentProperty.objects.filter(property__user=user)
        .values("status")
        .annotate(count=Count("status"))
    )

    # Prepare the data for the chart
    data = {
        "paid": 0,
        "pending": 0,
        "overdue": 0,
    }

    # Populate the data dictionary based on query results
    for entry in payment_status_counts:
        if entry["status"] == "paid":
            data["paid"] = entry["count"]
        elif entry["status"] == "pending":
            data["pending"] = entry["count"]
        elif entry["status"] == "overdue":
            data["overdue"] = entry["count"]

    # Pass the data to the frontend
    return {
        "paid": data["paid"],
        "pending": data["pending"],
        "overdue": data["overdue"],
    }
