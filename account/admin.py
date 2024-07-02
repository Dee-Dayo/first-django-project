from django.contrib import admin
from .models import Account


# Register your models here.

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass
    # list_display = ['account_number', 'first_name', 'last_name', 'account_type', 'balance']
    # list_per_page = 10
    # search_fields = ['account_number', 'first_name', 'last_name']
    # list_editable = ['first_name', 'last_name', 'account_type']

