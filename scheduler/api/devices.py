from rest_framework import viewsets
from scheduler.models import Device
from scheduler.serializer import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
