from django.contrib import admin

from .models import User, Address, State, District, SubDistrict, Village
# Register your models here.

admin.site.register(User)
admin.site.register(State)
admin.site.register(District)
admin.site.register(SubDistrict)
admin.site.register(Village)

