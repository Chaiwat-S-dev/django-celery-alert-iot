from rest_framework import viewsets
from scheduler.models import AlertSetting
from scheduler.serializer import AlertSettingSerializer

class AlertSettingViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = AlertSetting.objects.all()
    serializer_class = AlertSettingSerializer