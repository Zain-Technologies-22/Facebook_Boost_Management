# credits/models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from decimal import Decimal
import uuid

class PaymentMethod(models.TextChoices):
    """Supported payment methods for all transactions"""
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

class TransactionTypes(models.TextChoices):
    """Unified transaction types for all money movements"""
    RECHARGE = 'RECHARGE', 'Account Recharge'
    BILLING = 'BILLING', 'Billing Payment'
    AD_ACCOUNT_DEPOSIT = 'AD_DEPOSIT', 'Deposit to Ad Account'
    AD_ACCOUNT_WITHDRAW = 'AD_WITHDRAW', 'Withdraw from Ad Account'

class TransactionStatus(models.TextChoices):
    """Unified status for all transactions"""
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded'

class MoneyTransaction(models.Model):
    """
    Base model for all money transactions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='money_transactions'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionTypes.choices
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )
    
    # Balance tracking
    initial_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="User's balance before transaction"
    )
    final_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User's balance after transaction"
    )
    
    # Reference fields
    reference_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,  # Allow null initially, will be set in save()
        help_text="External reference ID (e.g., payment gateway ID)"
    )
    ad_account = models.ForeignKey(
        'accounts.AdAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_transactions'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_type', 'status']),
            models.Index(fields=['reference_id']),
            models.Index(fields=['created_at']),
        ]
        permissions = [
            ("can_process_transactions", "Can process money transactions"),
            ("can_view_all_transactions", "Can view all transactions"),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.user.username} - ৳{self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference_id:
            prefix = {
                TransactionTypes.RECHARGE: 'RCH',
                TransactionTypes.BILLING: 'BIL',
                TransactionTypes.AD_ACCOUNT_DEPOSIT: 'ADD',
                TransactionTypes.AD_ACCOUNT_WITHDRAW: 'ADW',
            }.get(self.transaction_type, 'TXN')
            
            self.reference_id = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
            
        if not self.pk:  # New transaction
            self.initial_balance = self.user.credit_balance
            
        super().save(*args, **kwargs)

    

    def process_transaction(self, processed_by):
        """Process any type of money transaction"""
        try:
            with transaction.atomic():
                if self.status != TransactionStatus.PENDING:
                    raise ValidationError("Only pending transactions can be processed")

                # Lock relevant records
                user = type(self.user).objects.select_for_update().get(pk=self.user.pk)
                ad_account = None
                if self.ad_account:
                    ad_account = type(self.ad_account).objects.select_for_update().get(pk=self.ad_account.pk)

                # Process based on transaction type
                if self.transaction_type == TransactionTypes.RECHARGE:
                    user.credit_balance += self.amount
                
                elif self.transaction_type == TransactionTypes.BILLING:
                    if user.credit_balance < self.amount:
                        raise ValidationError("Insufficient balance")
                    user.credit_balance -= self.amount
                
                elif self.transaction_type == TransactionTypes.AD_ACCOUNT_DEPOSIT:
                    if not ad_account:
                        raise ValidationError("Ad account required for deposit")
                    if user.credit_balance < self.amount:
                        raise ValidationError("Insufficient balance")
                    user.credit_balance -= self.amount
                    ad_account.credit_balance += self.amount
                
                elif self.transaction_type == TransactionTypes.AD_ACCOUNT_WITHDRAW:
                    if not ad_account:
                        raise ValidationError("Ad account required for withdrawal")
                    if ad_account.credit_balance < self.amount:
                        raise ValidationError("Insufficient ad account balance")
                    ad_account.credit_balance -= self.amount
                    user.credit_balance += self.amount

                # Update transaction record
                self.status = TransactionStatus.COMPLETED
                self.processed_by = processed_by
                self.final_balance = user.credit_balance
                
                # Save all changes
                user.save()
                if ad_account:
                    ad_account.save()
                self.save()

                # Create audit log
                TransactionAuditLog.objects.create(
                    transaction=self,
                    action='COMPLETE',
                    performed_by=processed_by,
                    old_status=TransactionStatus.PENDING,
                    new_status=TransactionStatus.COMPLETED,
                    balance_change=self.final_balance - self.initial_balance
                )

                return True

        except Exception as e:
            self.status = TransactionStatus.FAILED
            self.admin_notes = f"Error processing transaction: {str(e)}"
            self.save()
            
            TransactionAuditLog.objects.create(
                transaction=self,
                action='FAIL',
                performed_by=processed_by,
                old_status=TransactionStatus.PENDING,
                new_status=TransactionStatus.FAILED,
                notes=str(e)
            )
            
            return False

class TransactionAuditLog(models.Model):
    """Audit trail for all money transactions"""
    transaction = models.ForeignKey(
        MoneyTransaction,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    old_status = models.CharField(max_length=20, choices=TransactionStatus.choices)
    new_status = models.CharField(max_length=20, choices=TransactionStatus.choices)
    balance_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

class RechargeProof(models.Model):
    """Proof of payment for recharge transactions"""
    transaction = models.OneToOneField(
        MoneyTransaction,
        on_delete=models.CASCADE,
        related_name='recharge_proof'
    )
    proof_file = models.FileField(
        upload_to='recharge_proofs/',
        help_text="Payment receipt or screenshot"
    )
    sender_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Sender's phone number for mobile banking"
    )
    bank_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Bank transfer reference number"
    )


# # credits/models.py

# from django.db import models
# from django.core.validators import MinValueValidator, RegexValidator
# from django.contrib.auth import get_user_model
# from django.utils.translation import gettext_lazy as _
# from django.conf import settings
# import uuid

# CustomUser = get_user_model()

# class PaymentMethod(models.TextChoices):
#     """Supported payment methods for recharging and billing"""
#     # Mobile Banking Options
#     BKASH = 'BKASH', 'bKash'
#     NAGAD = 'NAGAD', 'Nagad'
#     ROCKET = 'ROCKET', 'Rocket'
#     UPAY = 'UPAY', 'Upay'
#     TAP = 'TAP', 'Tap'
    
#     # Bank Transfer Options
#     BANK_TRANSFER = 'BANK', 'Bank Transfer'
    
#     # Online Payment Gateways
#     ONLINE_PAYMENT = 'ONLINE', 'Online Payment'
    
#     # Automatic Recharge Methods
#     AUTO_CREDIT_CARD = 'AUTO_CARD', 'Automatic Credit Card'
#     AUTO_BANK_TRANSFER = 'AUTO_BANK', 'Automatic Bank Transfer'

# class RechargeStatus(models.TextChoices):
#     """Status of recharge transaction"""
#     PENDING = 'PENDING', 'Pending'
#     PROCESSING = 'PROCESSING', 'Processing'
#     COMPLETED = 'COMPLETED', 'Completed'
#     FAILED = 'FAILED', 'Failed'
#     CANCELLED = 'CANCELLED', 'Cancelled'

# class RechargeTransaction(models.Model):
#     """
#     Model to track recharge transactions with comprehensive details
#     """
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         related_name='recharge_transactions'
#     )
    
#     amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         validators=[MinValueValidator(0.01, "Recharge amount must be greater than zero")]
#     )
    
#     payment_method = models.CharField(
#         max_length=20,
#         choices=PaymentMethod.choices,
#         default=PaymentMethod.BKASH
#     )
    
#     status = models.CharField(
#         max_length=20,
#         choices=RechargeStatus.choices,
#         default=RechargeStatus.PENDING
#     )
    
#     # Transaction Identification
#     transaction_id = models.CharField(
#         max_length=100, 
#         unique=True, 
#         null=True, 
#         blank=True,
#         help_text="Unique transaction identifier from payment gateway"
#     )
    
#     # Manual Recharge Specific Fields
#     sender_phone_number = models.CharField(
#         max_length=15, 
#         blank=True, 
#         null=True,
#         help_text="Phone number used for mobile banking transaction"
#     )
    
#     bank_reference = models.CharField(
#         max_length=100, 
#         blank=True, 
#         null=True,
#         help_text="Bank transfer or reference number"
#     )
    
#     # Timestamp Fields
#     timestamp = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Notes and Additional Information
#     notes = models.TextField(
#         blank=True, 
#         null=True,
#         help_text="Additional notes about the transaction"
#     )
    
#     # Proof of Payment (optional)
#     payment_proof = models.FileField(
#         upload_to='recharge_proofs/',
#         blank=True,
#         null=True,
#         help_text="Upload payment receipt or screenshot"
#     )
    
#     class Meta:
#         verbose_name = _('Recharge Transaction')
#         verbose_name_plural = _('Recharge Transactions')
#         ordering = ['-timestamp']
    
#     def __str__(self):
#         return f"{self.user.username} - ৳{self.amount} via {self.get_payment_method_display()} ({self.get_status_display()})"
    
#     def save(self, *args, **kwargs):
#         """
#         Custom save method to ensure consistent processing
#         """
#         # Automatically generate transaction ID if not provided
#         if not self.transaction_id:
#             self.transaction_id = f"RCH-{uuid.uuid4().hex[:8].upper()}"
        
#         super().save(*args, **kwargs)

# class Credit(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     last_updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.balance}"

# class BillingStatus(models.TextChoices):
#     """Status of billing transaction"""
#     PENDING = 'PENDING', 'Pending'
#     COMPLETED = 'COMPLETED', 'Completed'
#     FAILED = 'FAILED', 'Failed'
#     REFUNDED = 'REFUNDED', 'Refunded'

# class BillingTransaction(models.Model):
#     """
#     Model to track billing transactions such as subscriptions, plan upgrades, etc.
#     """
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         related_name='billing_transactions'
#     )
    
#     amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         validators=[MinValueValidator(0.01, "Billing amount must be greater than zero")]
#     )
    
#     payment_method = models.CharField(
#         max_length=20,
#         choices=PaymentMethod.choices,
#         default=PaymentMethod.ONLINE_PAYMENT  # Adjust default as necessary
#     )
    
#     status = models.CharField(
#         max_length=20,
#         choices=BillingStatus.choices,
#         default=BillingStatus.PENDING
#     )
    
#     # Transaction Identification
#     transaction_id = models.UUIDField(
#         default=uuid.uuid4, 
#         editable=False, 
#         unique=True
#     )
    
#     # Description of the billing transaction
#     description = models.CharField(
#         max_length=255,
#         help_text="Description of the billing transaction"
#     )
    
#     # Timestamp Fields
#     timestamp = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Invoice URL
#     invoice_url = models.URLField(
#         blank=True, 
#         null=True,
#         help_text="URL to download the invoice"
#     )
    
#     # Notes and Additional Information
#     notes = models.TextField(
#         blank=True, 
#         null=True,
#         help_text="Additional notes about the billing transaction"
#     )
    
#     class Meta:
#         verbose_name = _('Billing Transaction')
#         verbose_name_plural = _('Billing Transactions')
#         ordering = ['-timestamp']
    
#     def __str__(self):
#         return f"{self.user.username} - ৳{self.amount} - {self.description} ({self.get_status_display()})"
    
# class UserPaymentMethod(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_methods')
#     payment_method = models.CharField(
#         max_length=20,
#         choices=PaymentMethod.choices
#     )
#     is_default = models.BooleanField(default=False)
    
#     # Additional fields like card_number, expiry_date can be added as needed
    
#     def __str__(self):
#         return f"{self.get_payment_method_display()} for {self.user.username}"

# class AdAccountTransferStatus(models.TextChoices):
#     """Status for transfers between main balance and ad accounts"""
#     PENDING = 'PENDING', 'Pending'
#     APPROVED = 'APPROVED', 'Approved'
#     REJECTED = 'REJECTED', 'Rejected'
#     CANCELLED = 'CANCELLED', 'Cancelled'

# class AdAccountTransferTransaction(models.Model):
#     """
#     Model to track money transfers between user's main balance and ad accounts
#     """
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='ad_account_transfers'
#     )
#     ad_account = models.ForeignKey(
#         'accounts.AdAccount',
#         on_delete=models.CASCADE,
#         related_name='money_transfers'
#     )
#     amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(0.01)]
#     )
#     transaction_type = models.CharField(
#         max_length=20,
#         choices=[
#             ('DEPOSIT', 'Deposit to Ad Account'),
#             ('WITHDRAW', 'Withdraw from Ad Account')
#         ]
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=AdAccountTransferStatus.choices,
#         default=AdAccountTransferStatus.PENDING
#     )
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     processed_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='processed_transfers'
#     )
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'Ad Account Transfer'
#         verbose_name_plural = 'Ad Account Transfers'

#     def __str__(self):
#         return f"{self.user.username} - {self.transaction_type} - {self.amount} ({self.get_status_display()})"

#     def process_transfer(self, processed_by):
#         """Process the transfer between main balance and ad account"""
#         from django.db import transaction
        
#         try:
#             with transaction.atomic():
#                 credit = Credit.objects.select_for_update().get(user=self.user)
                
#                 if self.transaction_type == 'DEPOSIT':
#                     if credit.balance < self.amount:
#                         raise ValueError("Insufficient balance in main account")
#                     credit.balance -= self.amount
#                     self.ad_account.credit_balance += self.amount
#                 else:  # WITHDRAW
#                     if self.ad_account.credit_balance < self.amount:
#                         raise ValueError("Insufficient balance in ad account")
#                     credit.balance += self.amount
#                     self.ad_account.credit_balance -= self.amount
                
#                 credit.save()
#                 self.ad_account.save()
#                 self.status = AdAccountTransferStatus.APPROVED
#                 self.processed_by = processed_by
#                 self.save()
                
#                 return True
#         except Exception as e:
#             self.status = AdAccountTransferStatus.REJECTED
#             self.notes = f"Transfer failed: {str(e)}"
#             self.save()
#             return False