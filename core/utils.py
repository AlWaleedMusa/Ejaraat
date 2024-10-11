from datetime import date
import calendar


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

    for property in properties:
        for rental in property.property_rentals.all():
            next_payment = rental.get_next_payment()
            if next_payment and (next_payment <= 3 and rental.status != "paid"):
                rental.status = "pending"
                rental.save()
                upcoming_payments.append(rental)

            elif rental.status != "paid":
                rental.status = "overdue"
                rental.save()
                upcoming_payments.append(rental)

    return upcoming_payments
