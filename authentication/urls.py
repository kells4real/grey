from django.urls import path
from .views import RegisterView, LogoutAPIView, confirm_reset_pass, user_detail, updateStatus,\
    update_user_image, reset_pass, VerifyEmail, LoginAPIView, update_user_detail, check_email,\
    email_verification, resend_verification, getOtp, check_email_transfer, notices, notice_read, admin_user_detail,\
    get_staffs, update_staff, RegisterStaffView, verifyUser, getVerifiedUser, addMessage, getMessages, getVerifiedUsers,\
    getUserDetail, getAppliedUsers, applyVerification, getSignal, getTraders, addTrader, update_user_image_id
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('update_user/', update_user_detail),
    path('update_status/', updateStatus),
    path('staffs/', get_staffs),
    path('register_staff/', RegisterStaffView.as_view()),
    path('update_staff/<str:username>/<str:stat>/', update_staff),
    path('otp/', getOtp),
    path('user_detail/', user_detail),
    path('admin_user_detail/<str:username>/', admin_user_detail),
    path('logout/', LogoutAPIView.as_view()),
    path('email-verify/<str:email>/<str:token>/', email_verification),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('notices/', notices, name='notices'),
    path('notice_read/<int:pk>/', notice_read, name='notice-read'),
    path('check_email/<str:email>/', check_email),
    path('check_email_transfer/<str:email>/', check_email_transfer),
    path('resend/<str:email>/', resend_verification),
    path('update_image/', update_user_image),
    path('request_password_reset/<email>/', reset_pass),
    path('confirm_reset_password/<email>/<str:token>/', confirm_reset_pass),
    path('verify-user/<str:username>/', verifyUser),
    path('verified-user/<str:username>/', getVerifiedUser),
    path('verified-users/', getVerifiedUsers),
    path('applied-users/', getAppliedUsers),
    path('chat-messages/', getMessages),
    path('add-message/', addMessage),
    path('get-user/', getUserDetail),
    path('apply_for_verification/', applyVerification),
    path('signal/', getSignal),
    path('user_traders/', getTraders),
    path('add_trader/', addTrader),
    path('update_id/', update_user_image_id)

]
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
