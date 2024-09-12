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
        exclude = ["property", "owner"]
        widgets = {
            "start_date": DatePickerInput(options={"format": "DD/MM/YYYY"}),
            "end_date": DatePickerInput(options={"format": "DD/MM/YYYY"}),
        }
