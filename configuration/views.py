from django.shortcuts import render
from .serializers import CurrencySerializer, WithdrawSerializer
from .models import Config, Currency, Withdraw
from rest_framework import views, viewsets, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication


class CurrencyViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = CurrencySerializer

    def create(self, request):
        if self.request.user.is_admin:
            try:
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                dict_response = {"error": False, "message": "Currency Created Successfully"}
                stat = status.HTTP_201_CREATED
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        try:
            queryset = Currency.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)

    def get(self, request, pk=None):
        try:
            queryset = Currency.objects.all()
            currency = get_object_or_404(queryset, pk=pk)
            serializer = self.serializer_class(currency, many=False)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)

    def update(self, request, pk=None):
        if self.request.user.is_admin:
            try:
                queryset = Currency.objects.all()
                currency = get_object_or_404(queryset, pk=pk)
                serializer = self.serializer_class(currency, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                dict_response = {"error": False, "message": "Updated Currency Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk=None):
        if self.request.user.is_admin:
            try:
                queryset = Currency.objects.all()
                currency = get_object_or_404(queryset, pk=pk)
                currency.delete()
                dict_response = {"error": False, "message": "Deleted Currency Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)


class WithdrawViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = WithdrawSerializer

    def get(self, request):
        try:
            queryset = Withdraw.objects.all().first()
            serializer = self.serializer_class(queryset, many=False)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)

    def update(self, request, pk=None):
        if self.request.user.is_admin:
            try:
                queryset = Withdraw.objects.all()
                withdraw = get_object_or_404(queryset, pk=pk)
                serializer = self.serializer_class(withdraw, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                dict_response = {"error": False, "message": "Updated Withdraw Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def getConfig(request):
    config = Config.objects.all().first()
    if config:
        return Response({"sell_percentage": config.portfolio_value_percentage,
                         "loan_rate": config.loan_interest_rate_percentage})
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def getWalletAddress(request):
    config = Config.objects.all().first()
    if config:
        return Response(config.wallet_address)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
