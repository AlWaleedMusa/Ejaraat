from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from babel.numbers import format_number
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _


class Property(models.Model):
    """
    A property model
    """

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    TYPE_CHOICES = (
        ("R", _("Room")),
        ("A", _("Apartment")),
        ("H", _("House")),
        ("V", _("Villa")),
        ("O", _("Office")),
        ("S", _("Store")),
    )

    CURRENCY_CHOICES = (
        ("", _("Select Currency")),
        ("USD", _("US Dollars")),
        ("EUR", _("European Euro")),
        ("SDG", _("Sudanese Pound")),
        ("EGP", _("Egyptian Pound")),
    )

    # property data
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Landlord",
    )
    name = models.CharField(max_length=250)
    property_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=TYPE_CHOICES[1])
    country = CountryField(blank_label="Select Country")
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    price = models.IntegerField()
    currency = models.CharField(max_length=3, null=True, blank=True, choices=CURRENCY_CHOICES)
    is_rented = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.property_type}"
    
    def save(self, *args, **kwargs):
        country_currency_map = {
            'US': 'USD',
            'EU': 'EUR',
            'SD': 'SDG',
            'EG': 'EGP',
        }
        if not self.currency:
            self.currency = country_currency_map.get(self.country, 'USD')
        super().save(*args, **kwargs)



class Tenant(models.Model):
    """
    A tenant model
    """

    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=14, help_text="Format: +249912345678")
    id_image = models.ImageField(
        upload_to="tenants_ID",
        null=True,
        blank=True,
        help_text="[Passport, National ID]"
    )

    def __str__(self):
        return self.name


class RentProperty(models.Model):
    """
    A model to represent the rental details of a property
    """

    class Meta:
        verbose_name = "Rent Property"
        verbose_name_plural = "Rent Properties"

    PAYMENT_OPTIONS = (
        ("1", _("Daily")),
        ("7", _("Weekly")),
        ("30", _("Monthly")),
        ("365", _("Yearly")),
    )

    # tenant data
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="tenant_rentals")

    # property data
    property = models.ForeignKey(
        Property,
        verbose_name="Property to Rent",
        on_delete=models.CASCADE,
        related_name="property_rentals",
    )
    payment = models.CharField(choices=PAYMENT_OPTIONS, max_length=10, default=PAYMENT_OPTIONS[2])
    damage_deposit = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today() + timedelta(days=30))

    contract = models.ImageField(
        upload_to="contracts", null=True, blank=True
    )

    def __str__(self):
        return f"{self.property.name} - Rented to {self.tenant.name}"

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
                current_payment_date += timedelta(
                    days=interval_days
                )  # For other intervals

        if current_payment_date >= end_date:
            return (
                None  # or return an appropriate message like "Rental period has ended"
            )

        return (current_payment_date - today).days

    def expected_income(self):
        interval_days = int(self.payment)
        price = self.property.price
        expected_income = 0
        end_date = self.end_date
        start_date = self.start_date

        current_date = start_date

        # Use relativedelta for better handling of monthly or yearly intervals
        while current_date <= end_date:
            expected_income += price

            # Check if it's a monthly interval, for example 30 days
            if interval_days == 30:
                current_date += relativedelta(months=1)  # Move by 1 month
            else:
                current_date += timedelta(days=interval_days)  # For other intervals

        return format_number(expected_income - price, locale="en_US")
