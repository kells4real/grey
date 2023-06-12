from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# from ckeditor_uploader import views as ck_views
from django.views.decorators.cache import never_cache, cache_page
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
# from django.contrib.auth.views import LoginView , LogoutView
# from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from django.contrib import admin
from django.urls import path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Khub API",
        default_version='v1.2',
        description="Test description",
        terms_of_service="https://khub.com",
        contact=openapi.Contact(email="contact@khub.com"),
        license=openapi.License(name="Test License"),
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('social_auth/', include('social_auth.urls')),
    path('wallet/', include('wallet.urls')),
    path('config/', include('configuration.urls')),
    path('investment/', include('investment.urls')),
    path('loan/', include('loan.urls')),
    path('account/', include('account.urls')),
    path('piggy/', include('piggyvest.urls')),
    path('register-notif-token/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('', schema_view.with_ui('swagger',
                                 cache_timeout=0), name='schema-swagger-ui'),

    path('api/api.json/', schema_view.without_ui(cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
                                       cache_timeout=0), name='schema-redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
