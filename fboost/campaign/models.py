from django.db import models
from django.utils import timezone
from datetime import datetime

from accounts.models import CustomUser

class Campaign(models.Model):
    # Existing fields
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed')
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.TextField()
    
    # New fields
    platform = models.CharField(max_length=50, default='Facebook')
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    auto_renewal = models.BooleanField(default=False)
    budget_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    followers_gained = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)

    @property
    def duration(self):
        return (self.end_date - self.start_date).days

    @property
    def days_remaining(self):
        return (self.end_date - timezone.now().date()).days

    @property
    def progress(self):
        total_days = self.duration
        days_passed = (timezone.now().date() - self.start_date).days
        if total_days > 0:
            return min(100, max(0, int((days_passed / total_days) * 100)))
        return 0

    @property
    def target_tags(self):
        return [tag.strip() for tag in self.target_audience.split(',') if tag.strip()]
    

class CampaignActivity(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)