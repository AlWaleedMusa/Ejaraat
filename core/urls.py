from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("add/", views.add_property, name="add_property"),
    path("rent_property/<int:pk>/", views.rent_property, name="rent_property"),
    path("edit_rental/<int:pk>/", views.edit_rental, name="edit_rental"),
    path("all_properties/", views.all_properties, name="all_properties"),
    path("delete_property/<int:pk>", views.delete_property, name="delete_property"),
    path("edit_property/<int:pk>", views.edit_property, name="edit_property"),
    path("view_property/<int:pk>", views.view_property, name="view_property"),
    path("mark_as_paid/<int:pk>", views.mark_as_paid, name="mark_as_paid"),
    path("empty_property/<int:pk>", views.empty_property, name="empty_property"),
    path("search_all_properties/", views.search_all_properties, name="search_all_properties"),
]
