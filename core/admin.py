from django.contrib import admin

from .models import *

admin.site.register(Property)
admin.site.register(RentProperty)
admin.site.register(Tenant)
admin.site.register(RentHistory)
admin.site.register(RecentActivity)
admin.site.register(Notifications)
