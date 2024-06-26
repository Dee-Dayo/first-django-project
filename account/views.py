from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Account
from .models import Transaction
from .serializers import AccountSerializer, AccountCreateSerializer
from rest_framework import status


# Create your views here.


@api_view(['GET', 'POST'])
def list_account(request):
    if request.method == 'GET':
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'GET':
        serializer = AccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = AccountCreateSerializer(account, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def deposit(request):
    account_number = request.data['account_number']
    amount = Decimal(request.data['amount'])
    account = get_object_or_404(Account, pk=account_number)
    account.balance += amount
    account.save()
    Transaction.objects.create(
        account=account,
        amount=amount
    )
    return Response(data={"message": "Transaction successful"}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def withdraw(request):
    account_number = request.data['account_number']
    amount = request.data['amount']
    pin = request.data['pin']
    account = get_object_or_404(Account, pk=account_number)
    if account.pin == pin:
        if account.balance > amount:
            account.balance -= Decimal(amount)
            account.save()
            Transaction.objects.create(
                account=account,
                transaction_type='DEB',
                amount=amount,
                transaction_status='S'
            )
        else:
            return Response(data={"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={"message": "Incorrect pin"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={"message": "Withdraw successful"}, status=status.HTTP_200_OK)
