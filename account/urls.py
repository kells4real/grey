from django.urls import path
from account import views

urlpatterns = [
    path('account/', views.AccountViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('account/<int:pk>/', views.AccountViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
]
