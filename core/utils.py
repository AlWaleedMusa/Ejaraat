from datetime import date
import os
import requests


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
    monthly_revenue = 0

    for property in properties:
        for rental in property.property_rentals.all():
            if rental.start_date <= today and rental.end_date >= today:
                converted_price = convert_currency(
                    rental.price, rental.property.currency
                )
                monthly_revenue += converted_price

    return monthly_revenue
