from .models import Property, RentProperty
from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.utils.translation import gettext_lazy as _


class PropertyForm(forms.ModelForm):

    class Meta:
        model = Property
        exclude = ["user", "is_rented"]
        labels = {
            'name': _("Property Name"),
            'property_type': _("Property Type"),
            'address': _("Property Address"),
            'price': _("Price/Month"),
        }


class RentPropertyForm(forms.ModelForm):

    class Meta:
        model = RentProperty
        exclude = ["property", "tenant"]
        widgets = {
            "start_date": DatePickerInput(options={"format": "DD/MM/YYYY"}),
            "end_date": DatePickerInput(options={"format": "DD/MM/YYYY"}),
        }
        labels = {
            'payment': _("Rent Payment Type"),
            'down_payment': _("Down Payment"),
            'start_date': _("Start Rent"),
            'end_date': _("End Rent"),
            'contract': _("Contract Image"),
            'damage_deposit': _("Damage Deposit"),
        }

    def __init__(self, *args, **kwargs):
        property = kwargs.pop("property", None)

        super().__init__(*args, **kwargs)

        if property:
            self.fields['damage_deposit'].initial = property.price
