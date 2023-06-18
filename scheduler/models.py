from django.db import models
from safedelete.models import SafeDeleteModel, SOFT_DELETE
from . import utils

# Create your models here.
class BaseModel(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    original_objects = models.Manager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class Device(BaseModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    mac_address = models.CharField(max_length=20, null=False, blank=False, db_index=True)
    measurement = models.CharField(max_length=255, null=True, blank=True)
    bucket = models.CharField(max_length=255, null=True, blank=True)
    parameters = models.JSONField(default=dict, null=False, blank=False)
    deadman = models.IntegerField(default=3600, null=False, blank=False)
    period = models.IntegerField(default=60, null=False, blank=False)
    brand = models.CharField(max_length=64, null=True, blank=True)
    output_parameters = models.JSONField(default=dict, null=False, blank=False)
    control_parameters = models.JSONField(default=dict, null=False, blank=False)
    
    @property
    def details_context(self):
        return {
            'id': self.pk,
            'title': self.title,
            'mac_address': self.mac_address if self.mac_address else None,
            'created_at': self.created_at,
            'bucket': self.bucket if self.bucket else None,
            'measurement': self.measurement if self.measurement else None,
            'parameters': self.parameters,
            'deadman': self.deadman,
            'brand': self.brand,
            'output_parameters': self.output_parameters,
            'control_parameters': self.control_parameters
        }

    @property
    def choices_context(self):
        return {"value": self.pk, "label": f"{self.title}"}


class AlertSetting(BaseModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    condition = models.JSONField(default=list, null=False, blank=False)
    action = models.JSONField(default=list, null=False, blank=False)
    enable = models.BooleanField(default=False, null=False, blank=False)
    alarm = models.BooleanField(default=True, null=False, blank=False)
    last_alert = models.DateTimeField(default=None, null=True, blank=False)
    period = models.IntegerField(default=60, null=False, blank=False)
    delay_time = models.IntegerField(default=0, null=False, blank=False)
    snooze_time = models.IntegerField(default=0, null=False, blank=False)
    alert_type = models.IntegerField(default=0, choices=utils.CHOICE_ALERT_TYPE)
    alarm_type = models.IntegerField(default=0, choices=utils.CHOICE_ALARM_TYPE)
    devices = models.ForeignKey(Device, default=None, blank=True, on_delete=models.CASCADE, related_name="alert_setting_devices")
    last_view = models.DateTimeField(default=None, null=True, blank=False)

    @property
    def details_context(self):
        return {
            'id': self.pk,
            'title': self.title,
            'condition': self.condition,
            'action': self.action,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'delay_time': self.delay_time,
            'snooze_time': self.snooze_time,
            'alarm_type': self.alarm_type,
            'alert_type': self.alert_type,
            'alarm':self.alarm,
            'timestamp':self.last_alert,
            'period':self.period,
            'enable':self.enable
        }