from django.urls import path
from piggyvest import views

urlpatterns = [
    path('piggy/', views.PiggyViewSet.as_view({'post': 'create'})),
    path('active_piggies/', views.runningPiggies),
    path('admin/', views.PiggyViewSet.as_view({'get': 'adminList'})),
    path('piggy/<int:pk>/', views.PiggyViewSet.as_view({'delete': 'destroy', 'get': 'get'})),
]