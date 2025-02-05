from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('check-server-status/', views.check_server_status),
    path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('docs/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ----------------------------------------
    # ----------------------------------------
    # token refresh view
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # token blacklist view
    path('auth/logout/', TokenBlacklistView.as_view(), name='logout'),
    # for authentication
    path('', include(router.urls)),
]
