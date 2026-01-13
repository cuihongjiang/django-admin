from django.urls import path
from django.urls import include

from JsAdmin.router import api_router

urlpatterns = [
    path('api/', include(api_router.urls))
]
