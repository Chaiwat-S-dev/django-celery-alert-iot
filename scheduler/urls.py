# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ---------- Created Tools --------------------------------------------------------------------------------------------
from .api import devices, alert_settings

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'devices', devices.DeviceViewSet, basename="deivces")
router.register(r'alert_settings', alert_settings.AlertSettingViewSet, basename="alert_setting")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
]