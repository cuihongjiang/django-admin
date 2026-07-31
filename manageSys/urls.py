from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls import include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.router import api_router

urlpatterns = [
    path('api/', include(api_router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# 开发环境下由 Django 直接提供上传文件访问，生产环境应交给 Nginx
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
