from django.contrib import admin
# from chat.views import  RoomView
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Django API",
        default_version='v1',
        description="Документация API для вашего проекта",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls), path("", include("mess.urls")),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    re_path(r'^swagger-json/$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
                re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    path('api/mess/', include('mess.urls'))
]
