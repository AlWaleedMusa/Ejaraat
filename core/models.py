from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import get_next_payment


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
    name = models.CharField(max_length=20)
    property_type = models.CharField(
        max_length=25, choices=TYPE_CHOICES, default=TYPE_CHOICES[1]
    )
    country = CountryField(blank_label=_("Select Country"))
    city = models.CharField(max_length=25)
    address = models.CharField(max_length=100)
    currency = models.CharField(
        max_length=3, null=True, blank=True, choices=CURRENCY_CHOICES
    )
    is_rented = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - belong to {self.user} / {self.property_type}"

    def get_translated_currency(self):
        """
        Get the translated currency based on the selected currency
        """

        currency_map = {
            "USD": _("USD"),
            "EUR": _("EUR"),
            "SDG": _("SDG"),
            "EGP": _("EGP"),
        }
        return currency_map.get(self.currency, self.currency)

    def save(self, *args, **kwargs):
        """
        Set the currency based on the country
        """

        country_currency_map = {
            "US": "USD",
            "EU": "EUR",
            "SD": "SDG",
            "EG": "EGP",
        }
        if not self.currency:
            self.currency = country_currency_map.get(self.country, "USD")
        super().save(*args, **kwargs)


class Tenant(models.Model):
    """
    A tenant model
    """

    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=14)
    id_image = models.ImageField(
        upload_to="tenants_ID",
        null=True,
        blank=True,
        help_text="[Passport, National ID]",
    )

    def __str__(self):
        return f"{self.name} / {self.landlord}'s Tenant" 


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

    STATUS_OPTIONS = (
        ("paid", _("Paid")),
        ("unpaid", _("Unpaid")),
        ("pending", _("Pending")),
        ("overdue", _("Overdue")),
    )

    # tenant data
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="tenant_rentals"
    )

    # property data
    property = models.ForeignKey(
        Property,
        verbose_name="Property to Rent",
        on_delete=models.CASCADE,
        related_name="property_rentals",
    )
    payment = models.CharField(
        choices=PAYMENT_OPTIONS, max_length=10, default=PAYMENT_OPTIONS[2]
    )
    price = models.IntegerField(help_text=_("Format: 12500"))
    damage_deposit = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today() + timedelta(days=30))
    status = models.CharField(max_length=10, choices=STATUS_OPTIONS, default="paid")
    contract = models.ImageField(upload_to="contracts", null=True, blank=True)

    def __str__(self):
        return f"{self.property.name} - Rented to {self.tenant.name} by {self.property.user}"

    def get_payment_period(self):
        """
        Get the payment period based on the payment interval
        """

        payment = int(self.payment)
        if payment == 7:
            return _("week")
        elif payment == 30:
            return _("month")
        elif payment == 365:
            return _("year")
        else:
            return _("day")

    def expiring_contracts(self):
        """
        Check if the contract is expiring in the next 30 days
        """

        end_date = self.end_date
        today = date.today()

        if today >= end_date - timedelta(days=30):
            return True, (end_date - today).days

    def get_next_payment(self):
        """
        Calculate the next payment date based on the payment interval
        """

        return get_next_payment(self.payment, self.start_date, self.end_date)

    # def reset_payment_status(self):
    #     """
    #     Resets the payment status based on the payment frequency (daily, weekly, monthly, or yearly).
    #     This should reset on the next payment date based on the interval.
    #     """
    #     today = date.today()
    #     interval_days = int(self.payment)

    #     if self.status == "paid":
    #         # Reset logic for different payment intervals
    #         if interval_days == 1:
    #             # Reset every day
    #             self.status == "pending"
    #             self.save()

    #         elif interval_days == 7:
    #             # Reset every 7 days from start_date
    #             next_payment_day = self.start_date + timedelta(weeks=(today - self.start_date).days // 7 + 1)
    #             if today == next_payment_day:
    #                 self.status == "pending"
    #                 self.save()

    #         elif interval_days == 30:
    #             # Reset every month on the same day as start_date
    #             next_payment_month = self.start_date + relativedelta(months=(today.year - self.start_date.year) * 12 + today.month - self.start_date.month + 1)
    #             if today == next_payment_month:
    #                 self.status == "pending"
    #                 self.save()

    #         elif self.payment == 365:
    #             # Reset every year on the same day as start_date
    #             next_payment_year = self.start_date + relativedelta(years=(today.year - self.start_date.year + 1))
    #             if today == next_payment_year:
    #                 self.status == "pending"
    #                 self.save()

    # def expected_income(self):
    #     """
    #     Calculate the expected income from the property based on the payment interval
    #     """

    #     interval_days = int(self.payment)
    #     price = self.price
    #     expected_income = 0
    #     end_date = self.end_date
    #     start_date = self.start_date

    #     current_date = start_date

    #     # Use relativedelta for better handling of monthly or yearly intervals
    #     while current_date <= end_date:
    #         expected_income += price

    #         # Check if it's a monthly interval, for example 30 days
    #         if interval_days == 30:
    #             current_date += relativedelta(months=1)  # Move by 1 month
    #         else:
    #             current_date += timedelta(days=interval_days)  # For other intervals

    #     return (
    #         format_number(expected_income, locale="en_US")
    #         if expected_income == price
    #         else format_number(expected_income - price, locale="en_US")
    #     )


class RentHistory(models.Model):
    """
    A model to represent the rent history of a property
    """

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.IntegerField()
    damage_deposit = models.IntegerField(null=True, blank=True)
    payment_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    contract = models.ImageField(
        upload_to="rent_history_contracts", null=True, blank=True
    )

    class Meta:
        verbose_name = "Rent History"
        verbose_name_plural = "Rent Histories"
        ordering = ["-end_date"]

    def __str__(self):
        property_name = self.property.name
        tenant_name = self.tenant.name if self.tenant else "Unknown Tenant"
        return f"RentHistory for {property_name} rented by {tenant_name}"


class RecentActivity(models.Model):
    """
    A model to represent recent activities for a user
    """

    ACTIVITIES_OPTIONS = (
        ("rent", _("You've rented this property.")),
        ("payment", _("You've received a payment for the property.")),
        ("contract", _("You've successfully renewed the contract for the property.")),
        ("overdue", _("Payment overdue for the property.")),
        ("add", _("You've added a new property.")),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=ACTIVITIES_OPTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recent Activity"
        verbose_name_plural = "Recent Activities"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} {self.activity_type} for {self.property.name} on {self.timestamp}"


class Notifications(models.Model):
    """
    A model to represent notifications for a user
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Notification for {self.user}"
