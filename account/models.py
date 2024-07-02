from django.db import models
from .utility import generate_account_number
from .validators import validate_pin
from django.conf import settings


# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=10, default=generate_account_number, unique=True, primary_key=True)
    pin = models.CharField(max_length=4, validators=[validate_pin], default='0000')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ACCOUNT_TYPE = [
        ('S', 'SAVINGS'),
        ('C', 'CURRENT'),
        ('D', 'DOMICILIARY'),
    ]
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPE, default='S')

    def get_first_name(self):
        return self.user.first_name

    def get_last_name(self):
        return self.user.last_name


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('DEB', 'DEBIT'),
        ('CRE', 'CREDIT'),
        ('TRA', 'TRANSFER'),
    ]
    TRANSACTION_STATUS = [
        ('S', 'SUCCESSFUL'),
        ('F', 'FAIL'),
        ('P', 'PENDING'),
    ]
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE, default='CRE')
    transaction_time = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    transaction_status = models.CharField(max_length=1, choices=TRANSACTION_STATUS, default='S')