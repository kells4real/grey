from django.shortcuts import render

# Create your views here.

from rest_framework import views, viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import LoanApplicationSerializer, LoanCrudSerializer, LoanListSerializer, LoanSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import LoanApplication, Loan
from authentication.models import User
from wallet.models import Wallet, AddToWallet, WalletTransfer, Withdraw
from wallet.serializers import WalletTransferSerializer, WithdrawSerializer, AddToWalletSerializer
from django.db.models import Q
from pagination.pagination import StandardPagination
from django.db.models.functions import TruncMonth
from django.db.models.aggregates import Count, Sum
from fcm_django.models import FCMDevice
from notifications.signals import notify
from django.utils import timezone


url = "http://localhost:8080"


class LoanViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = LoanApplicationSerializer

    def create(self, request):
        if request.user.is_user:
            loans = LoanApplication.objects.filter(user=request.user, approved=False, declined=False)
            try:
                if loans.count() < 1:
                    serializer = self.serializer_class(data=request.data, context={"request": request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save(user=request.user)
                    dict_response = {"error": False, "message": "Loan Created Successfully"}
                    fcm_devices = FCMDevice.objects.filter(user=request.user.id)
                    if fcm_devices:
                        fcm_devices.send_message(
                            title=f"Loan application successful",
                            body=f"Loan application of ${56} successful.",
                            time_to_live=604800,
                            click_action=f"{url}/loans")
                    stat = status.HTTP_201_CREATED
                else:
                    dict_response = {"error": True}
                    stat = status.HTTP_403_FORBIDDEN
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        try:
            loans = LoanApplication.objects.filter(user=request.user)
            serializer = LoanListSerializer(loans, many=True)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)

    def adminList(self, request):
        if request.user.is_staff or request.user.is_admin:
            try:
                loans = LoanApplication.objects.all().order_by('-date')
                if loans.count() > 0:
                    paginator = StandardPagination()
                    result_page = paginator.paginate_queryset(loans, request)
                    serializer = LoanListSerializer(result_page, many=True)

                    response = paginator.get_paginated_response(serializer.data)
                else:
                    response = Response({})

            except:
                response = Response(status.HTTP_404_NOT_FOUND)
            return response

    def update(self, request, pk=None):
        if request.user.is_admin or request.user.is_staff:
            try:
                queryset = LoanApplication.objects.all()
                loan = get_object_or_404(queryset, pk=pk)
                serializer = LoanCrudSerializer(loan, data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                serializer.save(confirmed_by=f"{request.user.username}", confirmDate=timezone.now())
                dict_response = {"error": False, "message": "Updated Loan Successfully"}

                if serializer.validated_data['approved']:
                    notify.send(request.user, recipient=loan.user, verb=f"${loan.amount} loan approved.",
                                description=request.user.username)
                    fcm_devices = FCMDevice.objects.filter(user=loan.user.id)
                    if fcm_devices:
                        fcm_devices.send_message(
                            title=f"Loan Approved",
                            body=f"Loan of ${loan.amount} approved",
                            time_to_live=604800,
                            click_action=f"{url}/loans")
                elif serializer.validated_data['declined']:
                    notify.send(request.user, recipient=loan.user, verb=f"${loan.amount} loan declined.",
                                description=request.user.username)
                    fcm_devices = FCMDevice.objects.filter(user=loan.user.id)
                    if fcm_devices:
                        fcm_devices.send_message(
                            title=f"Loan Declined",
                            body=f"Loan of ${loan.amount} declined.",
                            time_to_live=604800,
                            click_action=f"{url}/loans")
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk=None):
        user = request.user
        queryset = LoanApplication.objects.all()
        loan = get_object_or_404(queryset, pk=pk)
        if user.is_user and loan.user == user:
            try:
                loan.delete()
                dict_response = {"error": False, "message": "Deleted Loan Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def runningLoans(request):
    user = request.user
    if user.is_user:
        try:
            loans = Loan.objects.filter(user=user)
            serializer = LoanSerializer(loans, many=True)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
