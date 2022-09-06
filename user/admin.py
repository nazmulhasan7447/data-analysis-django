from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import *

class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('userID', 'email', 'username', 'phone_no', 'is_admin', 'is_paid_member', 'is_a_staff')
    list_filter = ('is_admin', 'is_paid_member', 'is_a_staff',)
    fieldsets = (
        (None, {'fields': ('userID', 'email', 'password')}),
        ('Personal info', {'fields': ('username', 'phone_no', 'fname', 'lname', 'date_of_birth', 'membershipStartingDate', 'membershipEndingDate',)}),
        ('Permissions', {'fields': ('is_admin', 'is_paid_member', 'is_a_staff', 'is_active', 'status', 'is_agreed_with_termsConsition',)}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_no', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(Account, UserAdmin)

admin.site.register(ProfileImage)
admin.site.unregister(Group)
