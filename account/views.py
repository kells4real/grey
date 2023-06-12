from django.shortcuts import render
from rest_framework import views, viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import BankAccountSerializer, BankAccountUpdateSerializer
from .models import BankAccount
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from wallet.models import Wallet, AddToWallet, WalletTransfer, Withdraw
from wallet.serializers import WalletTransferSerializer, WithdrawSerializer, AddToWalletSerializer
from django.db.models import Q


class AccountViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = BankAccountSerializer

    def create(self, request):
        if request.user.is_user:
            try:
                serializer = self.serializer_class(data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                accounts = BankAccount.objects.filter(user=request.user)
                if serializer.validated_data['primary'] and accounts.count() >= 1:
                    BankAccount.objects.filter(user=request.user).update(primary=False)
                    serializer.save(user=request.user)
                elif accounts.count() < 1:
                    serializer.save(user=request.user, primary=True)
                else:
                    serializer.save(user=request.user)
                dict_response = {"error": False, "message": "Account Created Successfully"}
                stat = status.HTTP_201_CREATED
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        try:
            accounts = BankAccount.objects.filter(user=request.user).order_by('-date')
            serializer = self.serializer_class(accounts, many=True)
            accounts = serializer.data
            accountPrimary = BankAccount.objects.filter(user=request.user, primary=True)
            if accountPrimary:
                serializer2 = self.serializer_class(accountPrimary[0], many=False)
            else:
                serializer2 = {"data": {}}
            account = serializer2.data

        except:
            accounts = []
            account = {}
        return Response({"accounts": accounts, "primary": account})

    def update(self, request, pk=None):
        queryset = BankAccount.objects.filter(user=request.user)
        account = get_object_or_404(queryset, pk=pk)
        if request.user == account.user:
            try:
                serializer = BankAccountUpdateSerializer(account, data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                if serializer.validated_data['primary']:
                    BankAccount.objects.filter(user=request.user).update(primary=False)
                serializer.save()
                dict_response = {"error": False, "message": "Updated Account Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk=None):
        queryset = BankAccount.objects.filter(user=request.user)
        account = get_object_or_404(queryset, pk=pk)
        if request.user == account.user:
            try:
                account.delete()
                dict_response = {"error": False, "message": "Deleted Account Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"error": True, "message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

