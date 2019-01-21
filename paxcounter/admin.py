from django.contrib import admin
from .models import Device


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('mac', 'type', 'name', 'updated_at', 'created_at')


admin.site.register(Device, DeviceAdmin)
