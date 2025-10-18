from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Job, Bid


class CustomUserAdmin(UserAdmin):
    pass


admin.site.register(User, CustomUserAdmin)
admin.site.register(Job)
admin.site.register(Bid)


