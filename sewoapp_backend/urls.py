from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
   openapi.Info(
      title="SewoApp API",
      default_version='v1',
      description="Dokumentasi API untuk sistem penyewaan kendaraan",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@sewoapp.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('sewoapp.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
