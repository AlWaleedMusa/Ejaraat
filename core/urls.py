from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("add/", views.add_property, name="add_property"),
    path("rent/<int:pk>/", views.rent_property, name="rent_property"),
    path("all_properties/", views.all_properties, name="all_properties")
]
