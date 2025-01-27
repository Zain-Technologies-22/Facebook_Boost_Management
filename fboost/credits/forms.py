# credits/forms.py

from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from .models import (
    MoneyTransaction, 
    RechargeProof,
    PaymentMethod,
    TransactionTypes,
    TransactionStatus
)
from decimal import Decimal

class BaseTransactionForm(forms.ModelForm):
    """Base form for all transactions"""
    class Meta:
        model = MoneyTransaction
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            })
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user  # Store the user
        super().__init__(*args, **kwargs)
        
        if 'payment_method' in self.fields:
            self.fields['payment_method'].widget.attrs['class'] = 'form-control'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

class RechargeForm(BaseTransactionForm):
    """Form for recharging main account balance"""
    phone_number = forms.CharField(
        label="Sender Phone Number",
        required=False,
        max_length=15,
        validators=[
            RegexValidator(
                r'^(\+?88)?0?1[3-9]\d{8}$', 
                message='Enter a valid Bangladeshi mobile number.'
            )
        ],
        help_text="Enter the phone number used for the transaction (required for mobile banking recharges)."
    )
    
    bank_reference = forms.CharField(
        label="Bank Reference/Transaction ID",
        required=False,
        max_length=100,
        help_text="Enter the bank transfer reference or transaction ID (required for bank transfers)."
    )
    
    payment_proof = forms.FileField(
        label="Payment Proof (Optional)",
        required=False,
        help_text="Upload payment receipt or screenshot (max 5MB, JPEG, PNG, or PDF)."
    )

    terms_agreement = forms.BooleanField(
        label="I agree to the terms and conditions for recharging.",
        required=True
    )

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.user = self.user  # Add this line
        transaction.transaction_type = TransactionTypes.RECHARGE
        transaction.initial_balance = self.user.credit_balance
        
        if commit:
            transaction.save()
            
            # Create recharge proof if provided
            if self.cleaned_data.get('payment_proof') or self.cleaned_data.get('bank_reference'):
                RechargeProof.objects.create(
                    transaction=transaction,
                    proof_file=self.cleaned_data.get('payment_proof'),
                    sender_phone=self.cleaned_data.get('phone_number'),
                    bank_reference=self.cleaned_data.get('bank_reference')
                )
        
        return transaction

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number')
        bank_reference = cleaned_data.get('bank_reference')
        
        mobile_banking_methods = [
            PaymentMethod.BKASH,
            PaymentMethod.NAGAD,
            PaymentMethod.ROCKET,
            PaymentMethod.UPAY,
            PaymentMethod.TAP
        ]
        
        if payment_method in mobile_banking_methods and not phone_number:
            self.add_error('phone_number', 'Phone number is required for mobile banking methods.')
            
        bank_methods = [PaymentMethod.BANK_TRANSFER, PaymentMethod.AUTO_BANK_TRANSFER]
        if payment_method in bank_methods and not bank_reference:
            self.add_error('bank_reference', 'Bank reference is required for bank transfer methods.')
            
        return cleaned_data

class AdAccountMoneyTransferForm(BaseTransactionForm):
    """Form for transferring money to/from ad accounts"""
    
    transaction_type = forms.ChoiceField(
        choices=[
            (TransactionTypes.AD_ACCOUNT_DEPOSIT, 'Deposit to Ad Account'),
            (TransactionTypes.AD_ACCOUNT_WITHDRAW, 'Withdraw from Ad Account')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    confirm_transfer = forms.BooleanField(
        label="I confirm this transfer and understand it cannot be undone",
        required=True
    )

    class Meta(BaseTransactionForm.Meta):
        fields = BaseTransactionForm.Meta.fields + ['ad_account', 'transaction_type']

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['ad_account'].queryset = user.adaccount_set.all()
        self.fields['ad_account'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        transaction_type = cleaned_data.get('transaction_type')
        ad_account = cleaned_data.get('ad_account')

        if transaction_type == TransactionTypes.AD_ACCOUNT_DEPOSIT:
            if self.user.credit_balance < amount:
                raise forms.ValidationError("Insufficient balance in main account")
        elif transaction_type == TransactionTypes.AD_ACCOUNT_WITHDRAW:
            if ad_account and ad_account.credit_balance < amount:
                raise forms.ValidationError("Insufficient balance in ad account")

        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.user = self.user
        transaction.transaction_type = self.cleaned_data['transaction_type']
        transaction.initial_balance = self.user.credit_balance
        if commit:
            transaction.save()
        return transaction

class BillingTransactionForm(BaseTransactionForm):
    """Form for billing transactions"""
    description = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta(BaseTransactionForm.Meta):
        fields = BaseTransactionForm.Meta.fields + ['payment_method', 'description']

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['payment_method'] = forms.ChoiceField(
            choices=PaymentMethod.choices,
            widget=forms.Select(attrs={'class': 'form-control'})
        )

    def clean_amount(self):
        amount = super().clean_amount()
        if self.user.credit_balance < amount:
            raise forms.ValidationError("Insufficient balance")
        return amount

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.user = self.user
        transaction.transaction_type = TransactionTypes.BILLING
        if commit:
            transaction.save()
        return transaction
