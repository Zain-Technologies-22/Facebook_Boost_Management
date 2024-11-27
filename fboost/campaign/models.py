from django.db import models
from accounts.models import CustomUser

class Campaign(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Active', 'Active'), ('Completed', 'Completed')])