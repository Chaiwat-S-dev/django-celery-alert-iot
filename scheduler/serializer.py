from rest_framework import serializers
from scheduler.models import Device, AlertSetting

class DeviceSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data["output_parameters"] = {"tag": "mb001"}
        if data["brand"] and data["brand"] == "beacon":
            data["period"] = 3600
        return data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({"user": "me"})
        alerts = AlertSettingSerializer(instance=instance.alert_setting_devices, many=True).data
        data.update({"alerts": alerts})
        return data
    
    class Meta:
        model = Device
        fields = '__all__' 

class AlertSettingSerializer(serializers.ModelSerializer):
    action = serializers.JSONField()
    condition = serializers.JSONField()

    class Meta:
        model = AlertSetting
        fields = '__all__'