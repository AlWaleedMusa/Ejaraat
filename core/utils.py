from datetime import date
import calendar
import requests
from datetime import timedelta
from .models import RecentActivity


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
