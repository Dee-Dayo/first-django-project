from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Account
from .models import Transaction
from .serializers import AccountSerializer, AccountCreateSerializer, DepositSerializer, WithdrawSerializer, \
    QueryBalanceSerializer, TransferSerializer
from rest_framework import status


# Create your views here.

# API view if you want to do custom post and all, Mixin when u want to do list and create
# viewset has all in 1

class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountCreateSerializer


class Deposit(APIView):

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = serializer.data['account_number']
        amount = Decimal(request.data['amount'])
        transaction_details = {}
        account = get_object_or_404(Account, pk=account_number)
        balance = account.balance
        balance += amount
        Account.objects.filter(account_number=account_number).update(balance=balance)

        Transaction.objects.create(
            account=account,
            amount=amount
        )
        transaction_details['account_number'] = account_number
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'CREDIT'

        return Response(data=transaction_details, status=status.HTTP_200_OK)


class Withdraw(APIView):
    permission_classes = [IsAuthenticated]  #security

    def patch(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = request.data['account_number']
        amount = Decimal(request.data['amount'])
        pin = request.data['pin']
        transaction_details = {}
        account = get_object_or_404(Account, pk=account_number)

        if account.pin == pin:
            if account.balance >= amount:
                account.balance -= amount
                account.save()

                Transaction.objects.create(
                    account=account,
                    transaction_type='DEB',
                    amount=amount,
                    transaction_status='S'
                )
                transaction_details['account_number'] = account_number
                transaction_details['amount'] = amount
                transaction_details['transaction_type'] = 'DEBIT'

                return Response(data=transaction_details, status=status.HTTP_200_OK)
            else:
                return Response(data={"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"message": "Incorrect pin"}, status=status.HTTP_400_BAD_REQUEST)


class CheckBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        account = get_object_or_404(Account, user=user.id)
        balance_details = {'account number': account.account_number, 'balance': account.balance}
        message = f'''
        your new balance is {account.balance}
        Thank you for banking with jaguda
        '''
        send_mail(subject="JAGUDA BANK",
                  message=message,
                  from_email='noreply@jaguda.com',
                  recipient_list=[f'{user.email}'])
        return Response(data=balance_details, status=status.HTTP_200_OK)


@api_view()
@login_required
def check_balance(request):
    user = request.user
    account = get_object_or_404(Account, user=user.id)
    balance_details = {'account_number': account.account_number, 'balance': account.balance}
    return Response(data=balance_details, status=status.HTTP_200_OK)


class TransferViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_account = serializer.data['sender_account']
        receiver_account = serializer.data['receiver_account']
        amount = Decimal(serializer.data['amount'])
        transaction_details = {}
        sender_account_from = get_object_or_404(Account, pk=sender_account)
        receiver_account_to = get_object_or_404(Account, pk=receiver_account)
        balance = sender_account_from.balance
        if balance > amount:
            balance = balance - amount
            Account.objects.filter(pk=sender_account).update(balance=balance)
        else:
            return Response(data={"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        try:

            transferred_balance = receiver_account_to.balance + amount
            Account.objects.filter(pk=receiver_account).update(balance=transferred_balance)
        except Account.DoesNotExist:
            return Response(data={"message": "Transaction failed"}, status=status.HTTP_400_BAD_REQUEST)
        Transaction.objects.create(
            account=sender_account_from,
            amount=amount,
            transaction_type='TRA'
        )
        transaction_details['receiver_account'] = receiver_account
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'TRANSFER'
        return Response(data=transaction_details, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)

# class ListAccount(ListCreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer
#
#
# class AccountDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer

#
# @api_view(['GET', 'POST'])
# def list_account(request):
#     if request.method == 'GET':
#         accounts = Account.objects.all()
#         serializer = AccountSerializer(accounts, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         serializer = AccountCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def account_detail(request, pk):
#     account = get_object_or_404(Account, pk=pk)
#     if request.method == 'GET':
#         serializer = AccountSerializer(account)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'PUT':
#         serializer = AccountCreateSerializer(account, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         account.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(['POST'])
# def deposit(request):
#     account_number = request.data['account_number']
#     amount = Decimal(request.data['amount'])
#     account = get_object_or_404(Account, pk=account_number)
#     account.balance += amount
#     account.save()
#     Transaction.objects.create(
#         account=account,
#         amount=amount
#     )
#     return Response(data={"message": "Transaction successful"}, status=status.HTTP_200_OK)
#
#
# @api_view(['PATCH'])
# def withdraw(request):
#     account_number = request.data['account_number']
#     amount = request.data['amount']
#     pin = request.data['pin']
#     account = get_object_or_404(Account, pk=account_number)
#     if account.pin == pin:
#         if account.balance > amount:
#             account.balance -= Decimal(amount)
#             account.save()
#             Transaction.objects.create(
#                 account=account,
#                 transaction_type='DEB',
#                 amount=amount,
#                 transaction_status='S'
#             )
#         else:
#             return Response(data={"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(data={"message": "Incorrect pin"}, status=status.HTTP_400_BAD_REQUEST)
#     return Response(data={"message": "Withdraw successful"}, status=status.HTTP_200_OK)
