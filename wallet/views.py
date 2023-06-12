from django.shortcuts import render
from rest_framework.response import Response
from authentication.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework import views, viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from .serializers import CRUDAddToWalletSerializer, AddToWalletSerializer, WalletTransfer,\
    WalletTransferCreateSerializer, WalletTransferSerializer, WithdrawSerializer, WithdrawCrudSerializer,\
    WithdrawUpdateSerializer, CryptoAddSerializer, CryptoAddCreateSerializer
from rest_framework import status
from .models import AddToWallet, Wallet, Withdraw, CryptoAdd
from configuration.models import Currency
from configuration.models import Withdraw as WithdrawConfig
from pagination.pagination import StandardPagination, AdminPagination
from django.db.models import Q
from fcm_django.models import FCMDevice
from notifications.signals import notify
from django.utils import timezone
from .utils import Util
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import locale
import string
from investment.models import percentage
import math
locale.setlocale(locale.LC_ALL, 'en_CA.UTF-8')


url = "https://trixfx.com"


class AddWalletViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    # Todo: Add a layer of security by using a random string that would be posted along with the data from the frontend.
    #  This would be check against the string here to confirm the data is coming from the frontend
    #  and not anywhere else.

    def create(self, request):
        if request.user.is_user:
            try:
                serializer = CRUDAddToWalletSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                walletUser = self.request.user
                amount = serializer.validated_data['amount']
                currency = Currency.objects.get(name=serializer.validated_data['local_currency'])
                Type = serializer.validated_data['type']
                shield = serializer.validated_data['shield']
                if shield == "AHSFNsgsrRSsdfo53724104YrUG4783nfhdtue64y--39ysreet35s3oe9-35952=2=262541hgstywsde23hsg":
                    AddToWallet.objects.create(user=walletUser, amount=amount, local_currency=currency, type=Type)
                    dict_response = {"error": False, "message": "Funds Added To Wallet Successfully"}
                    notify.send(request.user, recipient=request.user, verb=f"${amount} added to your wallet",
                                description=request.user.username)
                    stat = status.HTTP_201_CREATED

                else:
                    dict_response = {"error": True, "message": "Error"}
                    notify.send(request.user, recipient=request.user, verb=f"${amount} not added.",
                                description=request.user.username)
                    stat = status.HTTP_400_BAD_REQUEST
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        try:
            queryset = AddToWallet.objects.filter(user=request.user).order_by('-date')
            if queryset.count() > 0:
                paginator = StandardPagination()
                result_page = paginator.paginate_queryset(queryset, request)
                serializer = AddToWalletSerializer(result_page, many=True)

                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({}, status=status.HTTP_200_OK)

        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)


class WalletTransferViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        if request.user.is_user:
            try:
                serializer = WalletTransferCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user_from = request.user
                user_to = User.objects.get(email=serializer.validated_data["user"])
                amount = serializer.validated_data['amount']
                otp = serializer.validated_data['otp']
                wallet = Wallet.objects.get(user=user_from)
                if user_from and user_to and wallet.balance >= amount and otp:
                    if int(otp) == int(user_from.otp):
                        trans = WalletTransfer.objects.create(user_from=user_from, amount=amount, user_to=user_to)
                        dict_response = {"error": False, "message": "Funds Sent To Wallet Successfully"}
                        notify.send(request.user, recipient=request.user, verb=f"${amount} sent to {user_to.username}",
                                    description=request.user.username)
                        # fcm_devices = FCMDevice.objects.filter(user=user_from.id)
                        # if fcm_devices:
                        #     fcm_devices.send_message(
                        #         title=f"Transfer Successful",
                        #         body=f"${amount} transfer successful!",
                        #         time_to_live=604800,
                        #         click_action=f"{url}/wallet")
                        # fcm_devices2 = FCMDevice.objects.filter(user=user_to.id)
                        # if fcm_devices:
                        #     fcm_devices2.send_message(
                        #         title=f"Funds Received",
                        #         body=f"${amount} from {user_from} received!",
                        #         time_to_live=604800,
                        #         click_action=f"{url}/wallet")
                        print("AT")
                        ctx = {
                            'fullname': f'{user_from.first_name} {user_from.last_name}',
                            'amount': amount,
                            'username': user_to.username,
                            'balance': locale.currency(Wallet.objects.get(user=user_from).balance, grouping=True),
                            'date': trans.date.strftime("%Y-%m-%d %I:%M %p")
                        }
                        message = get_template('transfer.html').render(ctx)
                        plain_message = strip_tags(message)
                        msg = EmailMultiAlternatives(
                            'Debit Alert',
                            plain_message,
                            'Cighedge <noreply@cighedge.com>',
                            [user_from.email],
                        )
                        msg.attach_alternative(message, "text/html")  # Main content is now text/html
                        msg.send()

                        ctx2 = {
                            'fullname': f'{user_to.first_name} {user_from.last_name}',
                            'amount': amount,
                            'username': user_from.username,
                            'balance': locale.currency(Wallet.objects.get(user=user_to).balance, grouping=True),
                            'date': trans.date.strftime("%Y-%m-%d %I:%M %p")
                        }
                        message = get_template('transferto.html').render(ctx2)
                        plain_message = strip_tags(message)
                        msg = EmailMultiAlternatives(
                            'Credit Alert',
                            plain_message,
                            'Cighedge <noreply@cighedge.com>',
                            [user_to.email],
                        )
                        msg.attach_alternative(message, "text/html")  # Main content is now text/html
                        msg.send()

                        stat = status.HTTP_201_CREATED
                    else:
                        dict_response = {"error": True, "message": "Invalid OTP"}
                        stat = status.HTTP_200_OK
                else:
                    dict_response = {"error": True}
                    stat = status.HTTP_400_BAD_REQUEST
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        try:
            queryset = WalletTransfer.objects.filter(user=request.user).order_by('-date')
            if queryset.count() > 0:
                paginator = StandardPagination()
                result_page = paginator.paginate_queryset(queryset, request)
                serializer = WalletTransferSerializer(result_page, many=True)

                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({}, status=status.HTTP_200_OK)

        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)


class WithdrawViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        if self.request.user.is_user:
            try:
                serializer = WithdrawCrudSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = request.user
                wallet = Wallet.objects.get(user=user)
                if wallet.balance >= serializer.validated_data['amount']:
                    serializer.save(user=user)
                    dict_response = {"error": False, "message": "Withdraw created successfully"}
                    stat = status.HTTP_201_CREATED
                else:
                    dict_response = {"error": True}
                    stat = status.HTTP_400_BAD_REQUEST
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        if request.user.is_user:
            try:
                queryset = Withdraw.objects.filter(user=request.user).order_by('-date')
                if queryset.count() > 0:
                    paginator = StandardPagination()
                    result_page = paginator.paginate_queryset(queryset, request)
                    serializer = WithdrawSerializer(result_page, many=True)

                    return paginator.get_paginated_response(serializer.data)
                else:
                    return Response({}, status=status.HTTP_200_OK)

            except:
                response = status.HTTP_404_NOT_FOUND
            return Response(response)
        elif request.user.is_admin or request.user.is_staff:
            try:
                queryset = Withdraw.objects.all().order_by('-date')
                if queryset.count() > 0:
                    paginator = StandardPagination()
                    result_page = paginator.paginate_queryset(queryset, request)
                    serializer = WithdrawSerializer(result_page, many=True)

                    return paginator.get_paginated_response(serializer.data)
                else:
                    return Response({}, status=status.HTTP_200_OK)

            except:
                response = status.HTTP_404_NOT_FOUND
            return Response(response)

    def update(self, request, pk):
        if request.user.is_admin or request.user.is_staff:
            try:
                queryset = Withdraw.objects.all()
                withdraw = get_object_or_404(queryset, pk=pk)
                serializer = WithdrawUpdateSerializer(withdraw, data=request.data)
                serializer.is_valid(raise_exception=True)
                # Send the money to the user here using PayStack python sdk.
                # Make sure to remove the config.withdraw commission before.
                # withdrawCommission = WithdrawConfig.objects.all().first().withdraw_commission
                # amountToSend = withdraw.amount - (percentage(withdrawCommission, withdraw.amount))
                # amountToSend = math.floor(amountToSend)
                serializer.save(confirmed_by=f"{request.user.username}", confirmDate=timezone.now())
                if serializer.validated_data['approved']:
                    notify.send(request.user, recipient=withdraw.user, verb=f"${withdraw.amount} withdraw approved.",
                                description=request.user.username)
                    fcm_devices = FCMDevice.objects.filter(user=withdraw.user.id)
                    if fcm_devices:
                        fcm_devices.send_message(
                            title=f"Withdraw Approved",
                            body=f"Withdraw of ${withdraw.amount} approved",
                            time_to_live=604800,
                            click_action=f"{url}/wallet")
                    email_body = f"Hi {withdraw.user.username}, " \
                                 f"this is simply a message to notify you that you withdraw proposal was approved."
                    data = {'email_body': email_body, 'to_email': "kelvinsajere@gmail.com",
                            'email_subject': 'Withdraw Approved'}
                    Util.send_email(data)
                elif serializer.validated_data['declined']:
                    notify.send(request.user, recipient=withdraw.user, verb=f"${withdraw.amount} withdraw declined.",
                                description=request.user.username)
                    fcm_devices = FCMDevice.objects.filter(user=withdraw.user.id)
                    if fcm_devices:
                        fcm_devices.send_message(
                            title=f"Withdraw Declined",
                            body=f"Withdraw of ${withdraw.amount} has been declined.",
                            time_to_live=604800,
                            click_action=f"{url}/wallet")
                    email_body = f"Hi {withdraw.user.username}, " \
                                 f"this is simply a message to notify you that you withdraw proposal was declined."
                    data = {'email_body': email_body, 'to_email': "kelvinsajere@gmail.com",
                            'email_subject': 'Withdraw Declined'}
                    Util.send_email(data)
                response = serializer.data
            except:
                response = status.HTTP_404_NOT_FOUND
            return Response(response)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def adminList(self, request, stat):
        try:
            if stat == "approved":
                queryset = Withdraw.objects.filter(approved=True).order_by('-date')
            elif stat == "declined":
                queryset = Withdraw.objects.all().order_by('-date')
            else:
                queryset = Withdraw.objects.filter().order_by('-date')
            if queryset.count() > 0:
                paginator = StandardPagination()
                result_page = paginator.paginate_queryset(queryset, request)
                serializer = WithdrawSerializer(result_page, many=True)

                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({}, status=status.HTTP_200_OK)

        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def getTransfers(request):
    # user = User.objects.get(username="kelvinsajere")
    user = request.user
    if user.is_user:
        queryset = WalletTransfer.objects.filter(Q(user_to=user) | Q(user_from=user)).order_by('-date')
        if queryset.count() > 0:
            paginator = StandardPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = WalletTransferSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class CryptoRequest(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        if self.request.user.is_user:
            try:
                serializer = CryptoAddCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = request.user
                serializer.save(user=user)
                dict_response = {"error": False}
                stat = status.HTTP_201_CREATED
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        if request.user.is_staff or request.user.is_admin:
            requests = CryptoAdd.objects.all().order_by('-date')
            if requests.count() > 0:
                paginator = AdminPagination()
                result_page = paginator.paginate_queryset(requests, request)
                serializer = CryptoAddSerializer(result_page, many=True)

                return paginator.get_paginated_response(serializer.data)
            else:
                return Response({}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def updateRequest(request, pk, params):
    if request.user.is_admin or request.user.is_staff:
        try:
            req = CryptoAdd.objects.get(id=pk)
            if params == "approved":
                req.approved = True
                req.confirmedBy = request.user.username
                req.save(update_fields=['approved', 'confirmedBy'])
                fcm_devices = FCMDevice.objects.filter(user=req.user.id)
                if fcm_devices:
                    fcm_devices.send_message(
                        title=f"Crypto Request Approved",
                        body=f"${req.amount} added to your wallet!",
                        time_to_live=604800,
                        click_action=f"{url}/wallet")
            else:
                req.declined = True
                req.confirmedBy = request.user.username
                req.save(update_fields=['declined', 'confirmedBy'])
                fcm_devices = FCMDevice.objects.filter(user=req.user.id)
                if fcm_devices:
                    fcm_devices.send_message(
                        title=f"Crypto Request Declined",
                        body=f"${req.amount} not added to your wallet!",
                        time_to_live=604800,
                        click_action=f"{url}/wallet")
            response = {"status": "success"}
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
