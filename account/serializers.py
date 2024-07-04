from rest_framework import serializers
from .models import Account, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'transaction_time', 'transaction_status', 'description']


class AccountSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['account_number', 'first_name', 'last_name', 'balance', 'account_type', 'transactions']


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['user', 'account_number', 'pin', 'account_type']


class DepositSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)


class WithdrawSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    pin = serializers.CharField(max_length=4)