from django.conf.urls import url
from . import views

__author__ = "Hariom"


urlpatterns = [
    url(r'^register$', views.show_registration, name='registration'),
    url(r'^address$', views.show_address_form, name="address"),
    url(r'^show_registration_id', views.show_registration_id, name="registration_id"),
    url(r'^logout', views.logout, name='logout'),
    url(r'^address_api', views.AddressApi.as_view(), name="address_api")
]
