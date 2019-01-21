from django.db import models

TYPE_CHOICES = (
    ('W', 'WiFi'),
    ('B', 'Bluetooth'),
)

SCANNER_CHOICES = (
    ('PC', 'Paxcounter'),
)


class Device(models.Model):
    mac = models.CharField(db_index=True, max_length=16)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, editable=False)
    name = models.CharField(max_length=256, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.mac}'


class Scanner(models.Model):
    devid = models.CharField(db_index=True, max_length=128)
    type = models.CharField(max_length=4, choices=SCANNER_CHOICES)
    name = models.CharField(max_length=256, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.type}({self.devid})'


class Seen(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    scanner = models.ForeignKey(Scanner, on_delete=models.CASCADE)
    rssimin = models.IntegerField()
    rssimax = models.IntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f'{self.device}'
