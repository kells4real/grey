from django.urls import path
from loan import views

urlpatterns = [
    path('loan/', views.LoanViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('active_loan/', views.runningLoans),
    path('admin/', views.LoanViewSet.as_view({'get': 'adminList'})),
    path('loan/<int:pk>/', views.LoanViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
]
