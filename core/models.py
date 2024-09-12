from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from babel.numbers import format_number


class Property(models.Model):
    """
    A property model
    """

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    TYPE_CHOICES = (
        ("R", "Room"),
        ("A", "Apartment"),
        ("H", "House"),
        ("V", "Villa"),
        ("O", "Office"),
        ("S", "Store"),
    )

    # property data
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Landlord",
        related_name="properties",
    )
    name = models.CharField(max_length=250)
    property_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    address = models.CharField(max_length=200)
    price = models.IntegerField()
    is_rented = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.property_type}"


class RentProperty(models.Model):
    """
    A model to represent the rental details of a property
    """

    class Meta:
        verbose_name = "Rent Property"
        verbose_name_plural = "Rent Properties"

    PAYMENT_OPTIONS = (
        ("1", "Daily"),
        ("7", "Weekly"),
        ("30", "Monthly"),
        ("365", "Yearly"),
    )

    # tenant data
    t_name = models.CharField("Tenant's Name", max_length=150)
    t_phone_number = models.CharField(
        "Tenant's phone number",
        max_length=14,
        help_text="Phone number must be in this format +249912345678",
    )
    t_id = models.ImageField(
        "Tenant's ID Image [Passport, National ID]",
        upload_to="tenants_ID",
        null=True,
        blank=True,
    )

    # property data
    property = models.ForeignKey(
        Property,
        verbose_name="Property to Rent",
        on_delete=models.CASCADE,
        related_name="rentals",
    )
    # owner = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     verbose_name="Owner",
    #     null=True,
    #     related_name="owned_rentals",
    # )
    down_payment = models.DecimalField("Down Payment", max_digits=10, decimal_places=3)
    payment = models.CharField(
        "Payment Type", choices=PAYMENT_OPTIONS, max_length=10, null=True
    )
    start_date = models.DateField("Start Rent", default=date.today)
    end_date = models.DateField("End Rent", default=date.today() + timedelta(days=30))

    contract = models.ImageField(
        "Contract Image", upload_to="contracts", null=True, blank=True
    )

    def __str__(self):
        return f"{self.property.name} - Rented to {self.t_name}"

    def get_next_payment(self):
        interval_days = int(self.payment)
        today = date.today()
        current_payment_date = self.start_date
        end_date = self.end_date

        if today >= end_date - timedelta(days=3):
            return None  # rent ending in 3 days or less check with tenant

        while current_payment_date <= today and current_payment_date < end_date:
            if interval_days == 30:
                current_payment_date += relativedelta(months=1)  # Move by 1 month
            else:
                current_payment_date += timedelta(days=interval_days)  # For other intervals

        if current_payment_date >= end_date:
            return (
                None  # or return an appropriate message like "Rental period has ended"
            )

        return (current_payment_date - today).days

    def expected_income(self, obj):
        interval_days = int(self.payment)
        price = obj.price
        expected_income = 0
        end_date = self.end_date
        start_date = self.start_date
        today = date.today()

        current_date = start_date

        # Use relativedelta for better handling of monthly or yearly intervals
        while current_date <= end_date:
            expected_income += price

            # Check if it's a monthly interval, for example 30 days
            if interval_days == 30:
                current_date += relativedelta(months=1)  # Move by 1 month
            else:
                current_date += timedelta(days=interval_days)  # For other intervals

        return format_number(expected_income - price, locale='en_US')
