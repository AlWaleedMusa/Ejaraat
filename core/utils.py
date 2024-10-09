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

def get_days_overdued(rental, next_payment):
    """
    """
    year = rental.start_date.year
    month = rental.start_date.month
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month - next_payment

def get_upcoming_payments(properties):
    """
    """
    upcoming_payments = []

    for property in properties:
        for rental in property.property_rentals.all():
            next_payment = rental.get_next_payment()
            # if there is an expected payment
            if next_payment is not None:
                days_overdued = get_days_overdued(rental, next_payment)
                if next_payment <= 7 :
                    upcoming_payments.append(rental)
                elif (days_overdued >= 0 and not date.today().day == rental.start_date.day) and not rental.status == "paid":
                    rental.status = "overdue"
                    rental.save()
                    upcoming_payments.append(rental)
            # check if the last month is paid or not
            elif not rental.status == "paid":
                rental.status = "overdue"
                rental.save()
                upcoming_payments.append(rental)

    return upcoming_payments
