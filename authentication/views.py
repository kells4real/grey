import datetime
import time
from compression_middleware.decorators import compress_page
from notifications.models import Notification
from notifications.signals import notify
from django.shortcuts import render, redirect, reverse
from compression_middleware.decorators import compress_page
from rest_framework import generics, status, views, permissions, viewsets
from .serializers import ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LoginSerializer, \
    LogoutSerializer, RegisterStaffSerializer, PassSerializer, UserImageSerializer, StaffDetailsSerializer, \
    UserCrudSerializer, UserDetailSerializer, RegisterUserSerializer, ChatSerializer, AddChatSerializer,\
    GetUserSerializer, AddTraderSerializer
from django.http import Http404
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Chat, Traders
# from .utils import Util
from investment.models import Investment, Profit
from investment.serializers import InvestmentSerializer
from wallet.models import AddToWallet, WalletTransfer, Withdraw
from wallet.serializers import WalletTransferSerializer, AddToWalletSerializer, WithdrawSerializer
from account.models import BankAccount
from django.db.models import Q
from pagination.pagination import StandardUserPagination
from .pagination import StandardStudentPagination, StandardAllStudentPagination
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponsePermanentRedirect
import os
from cryptography.fernet import Fernet
import random
import string
import random as ran
from notifications.models import Notification
from .serializers import NotificationsSerializer
from django.core.cache import cache
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import locale
import string
from wallet.models import Wallet


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        ref = serializer.validated_data['refereeCodeLiteral']
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        Traders.objects.create(user=user)
        email_token = get_random_alphanumeric_string(80)
        user.email_token = email_token
        user.is_user = True
        user.set_password(password)
        Wallet.objects.create(user=user)
        if ref and User.objects.filter(referenceCode=ref).exists():
            user.referee = User.objects.get(referenceCode=ref)
            user.referred = True
        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(password.encode())
        user.password_string = token.decode()
        user.key = key.decode()
        current_site = "trixswift.com/email-verification/"
        relativeLink = f"{user_data['email']}/"
        absurl = 'https://' + current_site + relativeLink + email_token
        # email_body = 'Hi ' + user.username + \
        #              ' Use the link below to verify your email \n' + absurl
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Verify your email'}
        ctx = {
            'username': user.username,
            'link': absurl
        }
        message = get_template('verify_mail.html').render(ctx)
        plain_message = strip_tags(message)
        msg = EmailMultiAlternatives(
            'Verify Email',
            plain_message,
            'Trix Swift <noreply@trixswift.com>',
            [user.email],
        )
        msg.attach_alternative(message, "text/html")  # Main content is now text/html
        msg.send()
        user.save()

        return Response(user_data, status=status.HTTP_201_CREATED)


class RegisterStaffView(generics.GenericAPIView):
    serializer_class = RegisterStaffSerializer
    permission_classes = ([IsAuthenticated])

    def post(self, request):
        user = self.request.user
        total_staff = User.objects.filter(is_staff=True)
        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        if user.is_admin or user.is_superuser:
            # cached = cache.get(f"{user.username}staffs")
            if total_staff.count() <= 30:
                usr = serializer.save()
                usr.set_password(serializer.validated_data['password'])
                usr.is_staff = True
                usr.is_verified = True
                usr.save()
                # if cached is not None:
                #     cache.delete(f"{user.username}staffs")
                return Response({"Staff Created"}, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_staffs(request):
    user = request.user
    if user.is_admin and not user.is_superuser:
        staffs = User.objects.filter(is_staff=True, is_admin=False).order_by('-created_at')
        serializer = StaffDetailsSerializer(staffs, many=True)
        # cache.set(f"{user.username}staffs", {"staffs": serializer.data, "total_staffs": staffs.count()})
        return Response({"staffs": serializer.data, "total_staffs": staffs.count()})
    elif user.is_superuser:
        staffs = User.objects.filter((Q(is_staff=True) | Q(is_admin=True)) &
                                     Q(is_superuser=False)).order_by('-created_at')
        serializer = StaffDetailsSerializer(staffs, many=True)
        # cache.set(f"{user.username}staffs", {"staffs": serializer.data, "total_staffs": staffs.count()})
        return Response({"staffs": serializer.data, "total_staffs": staffs.count()})
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def update_staff(request, username, stat):
    user = request.user
    staff = User.objects.get(username=username)
    if user and (user.is_admin or user.is_superuser):
        if stat == "activate":
            # if cached is not None:
            #     cache.delete(f"{user.username}staffs")
            staff.is_active = True
            staff.save(update_fields=['is_active'])
            return Response({"Staff Deleted!"}, status=status.HTTP_200_OK)
        elif stat == "disable":
            staff.is_active = False
            staff.save(update_fields=['is_active'])
            return Response({"Staff Deleted!"}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def resend_verification(request, email):
    user = User.objects.get(email=email)

    if user:
        if not user.is_verified:

            email_token = get_random_alphanumeric_string(80)
            user.email_token = email_token
            user.save()

            current_site = "trixswift.com/email-verification/"
            relativeLink = f"{user.email}/"
            absurl = 'https://' + current_site + relativeLink + email_token
            if user.is_admin:
                email_body = 'Hi ' + user.school.name + \
                             ' click on the link below to verify your email. Link can also be copied and pasted' \
                             ' directly on a browser. \n' + absurl
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Verify your email'}
                Util.send_email(data)
            else:
                ctx = {
                    'username': user.username,
                    'link': absurl
                }
                message = get_template('verify_mail.html').render(ctx)
                plain_message = strip_tags(message)
                msg = EmailMultiAlternatives(
                    'Verify Email',
                    plain_message,
                    'Trix Swift <noreply@trixswift.com>',
                    [user.email],
                )
                msg.attach_alternative(message, "text/html")  # Main content is now text/html
                msg.send()
                user.save()

            return Response({'data': "Verification Email Sent"}, status=status.HTTP_200_OK)
        else:
            return Response({'data': "Email already verified"}, status=status.HTTP_200_OK)

    else:
        return Response({'error': 'Email Not Found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def reset_pass(request, email):
    user = User.objects.get(email=email)

    if user.is_verified:
        email_token = get_random_alphanumeric_string(80)
        users = User.objects.filter(email=email)
        users.update(email_token=email_token)

        current_site = "trixswift.com/reset-password/"
        relativeLink = f"{user.email}/"
        absurl = 'https://' + current_site + relativeLink + email_token
        email_body = 'Hi ' + user.username + \
                     ' Use the link below to to reset your password. If you did no initialize this, please do ignore. \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Reset your password'}
        Util.send_email(data)
        return Response({'success': "Reset Password Email Sent"}, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Failed"}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'error': "Email Not Verified Yet"}, status=status.HTTP_200_OK)
    #
    # else:
    #     return Response({'error': 'Email Not Found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def confirm_reset_pass(request, email, token):
    user = User.objects.filter(email=email, email_token=token)
    # print(user)
    serializer = PassSerializer(user, data=request.data)
    if user:
        user = user[0]
        if serializer.is_valid():
            password = serializer.validated_data['password']
            key = user.key.encode()
            f = Fernet(key)
            user.set_password(password)
            token = f.encrypt(password.encode())
            user.password_string = token.decode()
            user.email_token = ""
            if user.auth_provider != "email":
                user.auth_provider = "email"
            user.save()

            return Response({'success': "Your password has been changed, you may now login"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # elif user.is_verified:
        #     return Response({'error': "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'error': "Invalid verification code or user with this email does not exist.."},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_image(request):
    user = request.user
    if user.is_user:
        serializer = UserImageSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"image": user.image.url}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'data': 'User not an author'}, status=status.HTTP_400_BAD_REQUEST)


from .serializers import UserImageIdSerializer
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_image_id(request):
    user = request.user
    if user.is_user:
        serializer = UserImageIdSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("success", status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'data': 'User not an author'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def email_verification(request, email, token):
    user = User.objects.get(email=email)

    if user:
        if not user.is_verified and user.email_token == token:
            user.is_verified = True
            user.email_token = "Xvafd44GsD0BiKl8pfxa-86x_-9s/i!m"
            user.save(update_fields=['is_verified', 'email_token'])

            return Response("Your email is now verified you may now login.", status=status.HTTP_200_OK)
        elif user.is_verified:
            return Response("Email is already verified. You may login.", status=status.HTTP_200_OK)
        else:
            return Response({'error': "Invalid verification code or user with this email does not exist.."},
                            status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'error': "Invalid verification code or user with this email does not exist.."},
                        status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                         absurl + "?redirect_url=" + redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User with this email does not exist!'}, status=status.HTTP_404_NOT_FOUND)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


# Checks if an email exists
@api_view(['GET'])
def check_email(request, email):
    user = User.objects.filter(email=email).exists()
    if user:
        return Response(True)
    else:
        return Response(False)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def check_email_transfer(request, email):
    user = User.objects.filter(email=email)
    if request.user and user[0].is_user:
        user = User.objects.get(email=email)
        if user != request.user:
            return Response({"firstName": user.first_name, "lastName": user.last_name})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@compress_page
def user_detail(request):
    user = request.user
    if user:
        serializer = UserDetailSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_detail(request):
    user = request.user
    user1 = User.objects.filter(username=user.username)
    if user.is_user:
        serializer = UserCrudSerializer(user, data=request.data)
        if serializer.is_valid():
            # This was written like this, to make sure image don't save and duplicate as well
            if user.otp == serializer.validated_data['otp']:
                user1.update(first_name=serializer.validated_data['first_name'],
                             last_name=serializer.validated_data['last_name'],
                             mobile_no1=serializer.validated_data['mobile_no1'],
                             address=serializer.validated_data['address'],
                             gender=serializer.validated_data['gender'],
                             country=serializer.validated_data['country'],
                             state=serializer.validated_data['state'],
                             bitcoin=serializer.validated_data['bitcoin'],
                             about=serializer.validated_data['about'],
                             twitter=serializer.validated_data['twitter'],
                             instagram=serializer.validated_data['instagram'], updated=True, otp=214231)
                return Response({"success": True}, status=status.HTTP_200_OK)
            else:
                return Response({"error": True})

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def updateStatus(request):
    user = request.user
    if user:
        return Response({"status": user.updated})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOtp(request):
    user = request.user
    if user:
        a = ran.randint(0, 9)
        b = ran.randint(0, 9)
        c = ran.randint(0, 9)
        d = ran.randint(0, 9)
        e = ran.randint(0, 9)
        f = ran.randint(0, 9)
        get_code = "{}{}{}{}{}{}".format(a, b, c, d, e, f)
        User.objects.filter(username=user.username).update(otp=int(get_code))
        ctx = {
            'user': user.first_name,
            'fullname': f'{user.first_name} {user.last_name}',
            'otp': get_code,
        }
        message = get_template('otp.html').render(ctx)
        plain_message = strip_tags(message)
        msg = EmailMultiAlternatives(
            'OTP',
            plain_message,
            'Trix Swift <noreply@trixswift.com>',
            [user.email],
        )
        msg.attach_alternative(message, "text/html")  # Main content is now text/html
        msg.send()

        return Response("success")
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notices(request):
    usr = request.user
    if usr.is_user:
        queryset = Notification.objects.filter(recipient=usr, unread=True)[:16]

        return Response(NotificationsSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notice_read(request, pk):
    usr = request.user
    if usr.is_user:
        note = Notification.objects.get(id=pk)
        note.unread = False
        note.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


from account.serializers import BankAccountSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@compress_page
def admin_user_detail(request, username):
    admin = request.user
    user = User.objects.filter(username=username)
    if user and (admin.is_staff or admin.is_admin):
        user = user.first()
        serializer = UserDetailSerializer(user, many=False)
        investments = Investment.objects.filter(user=user)
        serializer2 = InvestmentSerializer(investments, many=True)
        totalInvestments = sum(investments.values_list('amount', flat=True))
        profit = Profit.objects.filter(user=user)
        totalProfit = sum(profit.values_list('amount', flat=True))
        wallet = Wallet.objects.get(user=user)
        referrals = User.objects.filter(referee=user)
        refs = AddToWallet.objects.filter(user=user, type="Referral")
        referralBonus = sum(refs.values_list('amount', flat=True))
        projectedProfitMonthly = sum([investment.interest() for investment in investments
                                      if investment.portfolio.profit_frequency == "Monthly"]) * 12
        projectedProfitWeekly = sum([investment.interest() for investment in investments
                                     if investment.portfolio.profit_frequency == "Weekly"]) * 52
        projectedProfit = projectedProfitMonthly + projectedProfitWeekly
        withdraws = Withdraw.objects.filter(user=user, approved=True).order_by('-date')[:3]
        transfers = WalletTransfer.objects.filter(Q(user_from=user) |
                                                  Q(user_to=user)).order_by('-date').distinct()[:3]
        add_wallet = AddToWallet.objects.filter(user=user).order_by('-date')[:3]
        if BankAccount.objects.filter(user=user, primary=True):
            accounts = BankAccount.objects.filter(user=user, primary=True)[0]
            account = {"account_bank": accounts.account_bank, "account_no": accounts.account_no,
                       "account_name": accounts.account_name}
        else:
            account = {"account_bank": "", "account_no": "", "account_name": ""}
        return Response({"data": serializer.data, "investments": {"investments": serializer2.data,
                         "totalInvestments": totalInvestments,
                         "walletBalance": wallet.balance, "totalProfit": totalProfit,
                         "projectedProfit": projectedProfit, "referrals": referrals.count(),
                         "referralBonus": referralBonus, "withdraws": WithdrawSerializer(withdraws, many=True).data,
                         "transfers": WalletTransferSerializer(transfers, many=True).data,
                         "add_wallet": AddToWalletSerializer(add_wallet, many=True).data,
                         "code": user.referenceCode, "country": user.country,
                         "bitcoin": user.bitcoin, "account": account}})
    else:
        return Response(None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verifyUser(request, username):
    user = request.user
    usr = User.objects.get(username=username)
    if user.is_admin or user.is_superuser:
        if usr.verified:
            usr.verified = False
            usr.save(update_fields=['verified'])
            return Response({"stat": False}, status=status.HTTP_200_OK)
        else:
            usr.verified = True
            usr.save(update_fields=['verified'])
            return Response({"stat": True}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMessages(request):
    user = request.user
    if user:
        messages = Chat.objects.all().order_by('date')
        if messages.count() > 0:
            paginator = StandardUserPagination()
            result_page = paginator.paginate_queryset(messages, request)
            serializer = ChatSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addMessage(request):
    user = request.user
    if user.verified:
        serializer = AddChatSerializer(data=request.data)
        if serializer.is_valid():
            Chat.objects.create(user=user, text=serializer.validated_data['text'])
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getVerifiedUsers(request):
    user = request.user
    if user:
        users = User.objects.filter(verified=True)
        if users.count() > 0:
            paginator = StandardUserPagination()
            result_page = paginator.paginate_queryset(users, request)
            serializer = GetUserSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getVerifiedUser(request, username):
    user = request.user
    if user:
        usr = User.objects.get(username=username)
        serializer = GetUserSerializer(usr, many=False)
        return Response(serializer.data)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserDetail(request):
    user = request.user
    if user:
        serializer = GetUserSerializer(user, many=False)
        return Response(serializer.data)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAppliedUsers(request):
    user = request.user
    if user:
        users = User.objects.filter(Q(applied=True) | Q(verified=True))
        if users.count() > 0:
            paginator = StandardUserPagination()
            result_page = paginator.paginate_queryset(users, request)
            serializer = GetUserSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def applyVerification(request):
    user = request.user
    if not user.verified:
        if user.applied:
            user.applied = False
            user.save(update_fields=['applied'])
            return Response({"status": False}, status=status.HTTP_200_OK)
        else:
            user.applied = True
            user.save(update_fields=['applied'])
            return Response({"status": True}, status=status.HTTP_200_OK)
    else:
        return Response({"status": "user already verified"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSignal(request):
    user = request.user
    if user:
        return Response({"signal": user.signal_strength})
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTraders(request):
    user = request.user
    if user:
        users = Traders.objects.get(user=user).traders.all()
        traders = []
        for usr in users:
            traders.append({"username": usr.username, "name": f"{usr.first_name} {usr.last_name}",
                            "profit": usr.profit_percentage, "image": usr.thumbnail.url})
        return Response(traders)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addTrader(request):
    user = request.user
    if user:
        serializer = AddTraderSerializer(data=request.data)
        userTrade = Traders.objects.get(user=user)
        if serializer.is_valid():
            traders = Traders.objects.get(user=user).traders.all()
            trader = User.objects.get(username=serializer.validated_data['username'])
            if trader in traders:
                userTrade.traders.remove(trader)
                return Response("Removed", status=status.HTTP_200_OK)
            else:
                userTrade.traders.add(trader)
                return Response("Copied", status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
