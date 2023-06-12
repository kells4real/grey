from django.urls import path
from wallet import views

urlpatterns = [
    path('transactions/', views.AddWalletViewSet.as_view({"post": "create", "get": "list"})),
    path('transfers/', views.WalletTransferViewSet.as_view({"post": "create", "get": "list"})),
    path('withdraw/', views.WithdrawViewSet.as_view({"post": "create", "get": "list"})),
    path('admin_withdraw/', views.WithdrawViewSet.as_view({"get": "adminList"})),
    path('admin_withdraw/<int:pk>/', views.WithdrawViewSet.as_view({"put": "update"})),
    path('crypto_requests/', views.CryptoRequest.as_view({"get": "list", "post": "create"})),
    path('crypto_requests/<int:pk>/<str:params>/', views.updateRequest),
    path('user_transfers/', views.getTransfers),

]
