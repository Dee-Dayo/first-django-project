from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_number', 'first_name', 'last_name', 'balance', 'account_type']


    # first used serializers.Serializer  thats wt made us use this
    # account_number = serializers.CharField(max_length=10)
    # first_name = serializers.CharField(max_length=255)
    # last_name = serializers.CharField(max_length=255)
    # balance = serializers.DecimalField(max_digits=6, decimal_places=2)
    # account_type = serializers.CharField(max_length=10)
