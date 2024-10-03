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
    return [
        rental
        for property in properties
        for rental in property.property_rentals.all()
        if (next_payment := rental.get_next_payment()) and next_payment <= 7
    ]