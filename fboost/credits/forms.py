# credits/forms.py

from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from .models import RechargeTransaction, PaymentMethod, BillingTransaction

class RechargeForm(forms.ModelForm):
    """
    Comprehensive form for manual recharge transactions
    """
    phone_number = forms.CharField(
        required=False,
        max_length=15,
        validators=[
            RegexValidator(
                r'^(\+?88)?0?1[3-9]\d{8}$', 
                message='Enter a valid Bangladeshi mobile number'
            )
        ],
        help_text="Your mobile number used for the transaction (optional for some methods)"
    )
    
    bank_reference = forms.CharField(
        required=False,
        max_length=100,
        help_text="Bank transfer or transaction reference number (optional)"
    )
    
    payment_proof = forms.FileField(
        required=False,
        help_text="Upload payment receipt or screenshot (optional)"
    )
    
    amount = forms.DecimalField(
        min_value=50,  # Minimum recharge amount (in BDT)
        max_value=100000,  # Maximum recharge amount
        decimal_places=2,
        max_digits=10,
        help_text="Minimum recharge amount is ৳50"
    )
    
    terms_agreement = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions for recharging"
    )
    
    class Meta:
        model = RechargeTransaction
        fields = [
            'amount', 
            'payment_method',
        ]
        widgets = {
            'payment_method': forms.Select(
                choices=PaymentMethod.choices, 
                attrs={'class': 'form-control'}
            )
        }
    
    def clean(self):
        """
        Additional form-level validation
        """
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number')
        bank_reference = cleaned_data.get('bank_reference')
        
        # Validate phone number for mobile banking methods
        mobile_banking_methods = [
            PaymentMethod.BKASH, 
            PaymentMethod.NAGAD, 
            PaymentMethod.ROCKET,
            PaymentMethod.UPAY,
            PaymentMethod.TAP
        ]
        
        if payment_method in mobile_banking_methods and not phone_number:
            self.add_error('phone_number', 'Phone number is required for mobile banking methods')
        
        # Validate bank reference for bank transfer methods
        bank_methods = [
            PaymentMethod.BANK_TRANSFER,
            PaymentMethod.AUTO_BANK_TRANSFER
        ]
        
        if payment_method in bank_methods and not bank_reference:
            self.add_error('bank_reference', 'Bank reference is required for bank transfer methods')
        
        # Ensure terms are agreed
        if not cleaned_data.get('terms_agreement'):
            self.add_error('terms_agreement', 'You must agree to the terms and conditions to proceed.')
        
        return cleaned_data
    
    def clean_payment_proof(self):
        payment_proof = self.cleaned_data.get('payment_proof')
        if payment_proof:
            if payment_proof.size > 5*1024*1024:  # Limit to 5MB
                raise forms.ValidationError("Payment proof file size should not exceed 5MB.")
            if not payment_proof.content_type in ['image/jpeg', 'image/png', 'application/pdf']:
                raise forms.ValidationError("Unsupported file type. Please upload a JPEG, PNG, or PDF file.")
        return payment_proof
    
    def save(self, commit=True):
        """
        Custom save method to handle additional form fields
        """
        # Create the model instance
        instance = super().save(commit=False)
        
        # Set additional fields
        instance.sender_phone_number = self.cleaned_data.get('phone_number')
        instance.bank_reference = self.cleaned_data.get('bank_reference')
        
        # Handle payment proof
        payment_proof = self.cleaned_data.get('payment_proof')
        if payment_proof:
            instance.payment_proof = payment_proof
        
        # Set initial status
        instance.status = 'PENDING'
        
        if commit:
            instance.save()
        
        return instance

class BillingTransactionForm(forms.ModelForm):
    """
    Form for creating billing transactions like plan upgrades
    """
    class Meta:
        model = BillingTransaction
        fields = [
            'amount',
            'payment_method',
            'description',
        ]
        widgets = {
            'payment_method': forms.Select(
                choices=PaymentMethod.choices, 
                attrs={'class': 'form-control'}
            ),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount