from .models import Property, RentProperty
from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from django.urls import reverse_lazy

class PropertyForm(forms.ModelForm):

    class Meta:
        model = Property
        exclude = ["user", "is_rented"]
        labels = {
            'name': _("Property Name"),
            'property_type': _("Property Type"),
            'address': _("Property Address"),
            'price': _("Price/Month"),
            'country': _("Country"),
            'city': _("City"),
            'currency': _("Currency"),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Enter property name')}),
            'address': forms.TextInput(attrs={'placeholder': _('Enter property address')}),
            'price': forms.NumberInput(attrs={'placeholder': _('Enter price per month')}),
            'city': forms.TextInput(attrs={'placeholder': _('Enter city')}),
        }

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'add')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse_lazy('edit_property', args=[self.instance.id]) if action == 'edit' else reverse_lazy('add_property'),
            'hx-target': '#main-content',
            'hx-swap': 'innerHTML',
        }
        self.helper.add_input(Submit('submit', 'Save'))

        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    'property_type',
                    'country',
                    'city',
                    'address',
                    css_class="col-lg-7"
                ),
                Column(
                    'price',
                    'currency',
                    css_class='col-lg-5'
                ),
                css_class="form-row"
            )
        )

        



class RentPropertyForm(forms.ModelForm):
    """
    """
    tenant_name = forms.CharField(max_length=100, label=_("Tenant Name"))
    tenant_phone_number = forms.CharField(max_length=14, label=_("Tenant Phone Number"),  help_text="Format: +249912345678")
    tenant_image = forms.ImageField(label=_("Tenant ID Image"), required=False)

    class Meta:
        model = RentProperty
        exclude = ["property", "tenant"]
        widgets = {
            "start_date": forms.DateInput(attrs={'type': 'date'}),
            "end_date": forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'payment': _("Rent Payment Type"),
            'start_date': _("Start Rent"),
            'end_date': _("End Rent"),
            'contract': _("Contract Image"),
            'damage_deposit': _("Damage Deposit"),
        }

    def __init__(self, *args, **kwargs):
        action = kwargs.pop('action', 'rent')
        property = kwargs.pop("property", None)
        tenant = kwargs.pop("tenant", None)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse_lazy('edit_rental', args=[self.instance.id]) if action == 'edit' else reverse_lazy('rent_property', args=[property.id]),
            'hx-target': '#main-content',
            'hx-swap': 'innerHTML',
        }
        self.helper.add_input(Submit('submit', 'Rent'))

        if property:
            self.fields['damage_deposit'].initial = property.price

        if tenant:
            self.fields["tenant_name"].initial = tenant.name
            self.fields["tenant_phone_number"].initial = tenant.phone_number
            self.fields["tenant_image"].initial = tenant.id_image

        self.helper.layout = Layout(
            Row(
                Column(
                    'tenant_name',
                    'tenant_phone_number',
                    'tenant_image',
                    'payment',
                    css_class="col-lg-7",
                ),
                Column(
                    'start_date',
                    'end_date',
                    'damage_deposit',
                    'contract',
                    css_class="col-lg-5",
                )
            )
        )
