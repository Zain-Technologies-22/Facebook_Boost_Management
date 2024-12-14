# credits/models.py

from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

CustomUser = get_user_model()

class PaymentMethod(models.TextChoices):
    """Supported payment methods for recharging and billing"""
    # Mobile Banking Options
    BKASH = 'BKASH', 'bKash'
    NAGAD = 'NAGAD', 'Nagad'
    ROCKET = 'ROCKET', 'Rocket'
    UPAY = 'UPAY', 'Upay'
    TAP = 'TAP', 'Tap'
    
    # Bank Transfer Options
    BANK_TRANSFER = 'BANK', 'Bank Transfer'
    
    # Online Payment Gateways
    ONLINE_PAYMENT = 'ONLINE', 'Online Payment'
    
    # Automatic Recharge Methods
    AUTO_CREDIT_CARD = 'AUTO_CARD', 'Automatic Credit Card'
    AUTO_BANK_TRANSFER = 'AUTO_BANK', 'Automatic Bank Transfer'

class RechargeStatus(models.TextChoices):
    """Status of recharge transaction"""
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class RechargeTransaction(models.Model):
    """
    Model to track recharge transactions with comprehensive details
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='recharge_transactions'
    )
    
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01, "Recharge amount must be greater than zero")]
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BKASH
    )
    
    status = models.CharField(
        max_length=20,
        choices=RechargeStatus.choices,
        default=RechargeStatus.PENDING
    )
    
    # Transaction Identification
    transaction_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Unique transaction identifier from payment gateway"
    )
    
    # Manual Recharge Specific Fields
    sender_phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Phone number used for mobile banking transaction"
    )
    
    bank_reference = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Bank transfer or reference number"
    )
    
    # Timestamp Fields
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes and Additional Information
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the transaction"
    )
    
    # Proof of Payment (optional)
    payment_proof = models.FileField(
        upload_to='recharge_proofs/',
        blank=True,
        null=True,
        help_text="Upload payment receipt or screenshot"
    )
    
    class Meta:
        verbose_name = _('Recharge Transaction')
        verbose_name_plural = _('Recharge Transactions')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - ৳{self.amount} via {self.get_payment_method_display()} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """
        Custom save method to ensure consistent processing
        """
        # Automatically generate transaction ID if not provided
        if not self.transaction_id:
            self.transaction_id = f"RCH-{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)

class Credit(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.balance}"

class BillingStatus(models.TextChoices):
    """Status of billing transaction"""
    PENDING = 'PENDING', 'Pending'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    REFUNDED = 'REFUNDED', 'Refunded'

class BillingTransaction(models.Model):
    """
    Model to track billing transactions such as subscriptions, plan upgrades, etc.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='billing_transactions'
    )
    
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01, "Billing amount must be greater than zero")]
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.ONLINE_PAYMENT  # Adjust default as necessary
    )
    
    status = models.CharField(
        max_length=20,
        choices=BillingStatus.choices,
        default=BillingStatus.PENDING
    )
    
    # Transaction Identification
    transaction_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )
    
    # Description of the billing transaction
    description = models.CharField(
        max_length=255,
        help_text="Description of the billing transaction"
    )
    
    # Timestamp Fields
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Invoice URL
    invoice_url = models.URLField(
        blank=True, 
        null=True,
        help_text="URL to download the invoice"
    )
    
    # Notes and Additional Information
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the billing transaction"
    )
    
    class Meta:
        verbose_name = _('Billing Transaction')
        verbose_name_plural = _('Billing Transactions')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - ৳{self.amount} - {self.description} ({self.get_status_display()})"
    
class UserPaymentMethod(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_methods')
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )
    is_default = models.BooleanField(default=False)
    
    # Additional fields like card_number, expiry_date can be added as needed
    
    def __str__(self):
        return f"{self.get_payment_method_display()} for {self.user.username}"