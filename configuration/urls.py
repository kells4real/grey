from django.urls import path
from configuration import views


urlpatterns = [
    path('withdraw/', views.WithdrawViewSet.as_view({'get': 'get'})),
    path('withdraw/<int:pk>/', views.WithdrawViewSet.as_view({'put': 'update'})),
    path('currencies/', views.CurrencyViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('currency/<int:pk>/', views.CurrencyViewSet.as_view({'get': 'get', 'put': 'update', 'delete': 'destroy'})),
    path('config/', views.getConfig),
    path('wallet/', views.getWalletAddress)
]
