from .models import Property, RentProperty
from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput


class PropertyForm(forms.ModelForm):

    class Meta:
        model = Property
        exclude = ["user", "is_rented"]


class RentPropertyForm(forms.ModelForm):

    class Meta:
        model = RentProperty
        exclude = ["property", "owner"]
        widgets = {
            "start_date": DatePickerInput(options={"format": "DD/MM/YYYY"}),
            "end_date": DatePickerInput(options={"format": "DD/MM/YYYY"}),
        }
