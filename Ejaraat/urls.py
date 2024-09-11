from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("core.urls")),
]
urlpatterns += i18n_patterns(
    path('set-language/', set_language, name='set_language'),
)
