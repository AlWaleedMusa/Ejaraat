from django.contrib import admin
from .models import Property, RentProperty, Tenant

admin.site.register(Property)
admin.site.register(RentProperty)
admin.site.register(Tenant)
