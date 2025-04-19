from django.db import models

class VehicleLog(models.Model):
    plate_number = models.CharField(max_length=20)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.plate_number
