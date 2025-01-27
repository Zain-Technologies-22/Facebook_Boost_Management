
# fboost/accounts/models.py
from django.db import models
from django.core.validators import URLValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    credit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )



class TimeZone(models.TextChoices):
    """Predefined list of common timezones"""
    US_EASTERN = 'US/Eastern', 'US Eastern'
    US_CENTRAL = 'US/Central', 'US Central'
    US_MOUNTAIN = 'US/Mountain', 'US Mountain'
    US_PACIFIC = 'US/Pacific', 'US Pacific'
    UTC = 'UTC', 'UTC'
    # Add more timezones as needed

class BusinessType(models.TextChoices):
    """Predefined list of business types"""
    SOLE_PROPRIETORSHIP = 'SOLE', 'Sole Proprietorship'
    LLC = 'LLC', 'Limited Liability Company'
    CORPORATION = 'CORP', 'Corporation'
    NONPROFIT = 'NONPROFIT', 'Non-Profit Organization'
    PARTNERSHIP = 'PARTNERSHIP', 'Partnership'
    # Add more business types as needed

class AccountType(models.TextChoices):
    """Predefined list of account types"""
    Credit_Line = 'Credit Line', 'Credit Line'
    Card = 'Card', 'Card'
    Other = 'Other', 'Other'
    # Add more account types as needed

class AdAccount(models.Model):
    # User relationship
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    # Basic Account Information
    account_name = models.CharField(max_length=255)
    
    # Facebook Page URLs
    facebook_page_url_1 = models.URLField(
    max_length=500, 
    default='https://www.facebook.com/placeholder',  # Provide a default URL
    help_text="Primary Facebook Page URL"
)
    facebook_page_url_2 = models.URLField(max_length=500, blank=True, null=True)
    facebook_page_url_3 = models.URLField(max_length=500, blank=True, null=True)
    facebook_page_url_4 = models.URLField(max_length=500, blank=True, null=True)
    facebook_page_url_5 = models.URLField(max_length=500, blank=True, null=True)
    
    # Website/Destination URLs
    website_url_1 = models.URLField(max_length=500, blank=True, null=True)
    website_url_2 = models.URLField(max_length=500, blank=True, null=True)
    
    # Additional Account Details
    account_type = models.CharField(
        max_length=20, 
        choices=AccountType.choices,
        default=AccountType.Card
    )
    
    business_manager_id = models.CharField(
    max_length=50, 
    validators=[
        RegexValidator(
            r'^[0-9]+$', 
            'Business Manager ID must be a number'
        )
    ],
    blank=True,  # Allows the field to be left blank in forms
    null=True    # Allows NULL in the database
)
    
    timezone = models.CharField(
        max_length=20, 
        choices=TimeZone.choices,
        default=TimeZone.UTC
    )
    
    business_type = models.CharField(
        max_length=20, 
        choices=BusinessType.choices,
        blank=True,
        null=True
    )
    
    # Confirmation Fields
    payment_confirmed = models.BooleanField(default=False)
    terms_conditions_agreed = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add credit balance field
    credit_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Account Balance"
    )

    def __str__(self):
        return f"{self.account_name} ({self.user.username})"

    
class AdAccountTransfer(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='transfers_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='transfers_received', on_delete=models.CASCADE)
    ad_account = models.ForeignKey(AdAccount, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer of {self.ad_account} from {self.from_user} to {self.to_user}"
    



class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    facebook_url = models.URLField(max_length=200, blank=True)
    twitter_url = models.URLField(max_length=200, blank=True)
    instagram_url = models.URLField(max_length=200, blank=True)
    linkedin_url = models.URLField(max_length=200, blank=True)
    total_followers = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    def __str__(self):
        return f"{self.user.username}'s profile"

# Signal to automatically create/update Profile when CustomUser is created/updated
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class LoginHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']