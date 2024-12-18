from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Admin site özelleştirmeleri
admin.site.site_header = 'UAV Üretim Yönetim Paneli'
admin.site.site_title = 'UAV Üretim Admin'
admin.site.index_title = 'Yönetim Paneli'

schema_view = get_schema_view(
    openapi.Info(
        title="UAV Production API",
        default_version='v1',
        description="API documentation for UAV Production System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@uavproduction.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),  # staff_member_required zaten admin içinde var
    path('', include('production.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('production.api.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
