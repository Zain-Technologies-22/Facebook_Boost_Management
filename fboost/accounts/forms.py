# accounts/forms.py

from django import forms
from .models import AdAccount, AdAccountTransfer, Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser

CustomUser = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class ApplyAdAccountForm(forms.ModelForm):
    confirm_payment = forms.BooleanField(
        required=True, 
        label="I confirm payment has been made and has left my account"
    )
    confirm_balance_update = forms.BooleanField(
        required=True, 
        label="I understand the balance on my account can only be updated after the funds are received by Aurora"
    )
    confirm_transfer_details = forms.BooleanField(
        required=True, 
        label="If making a transfer, I have checked the payment details and confirm I sent the funds to the correct bank details"
    )
    agree_terms = forms.BooleanField(
        required=True, 
        label="I have read and agree to the Terms and Conditions"
    )

    class Meta:
        model = AdAccount
        fields = [
            'account_name',
            'facebook_page_url_1',
            'facebook_page_url_2',
            'facebook_page_url_3',
            'facebook_page_url_4',
            'facebook_page_url_5',
            'website_url_1',
            'website_url_2',
            'account_type',
            'business_manager_id',
            'timezone',
            'business_type',
        ]

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('confirm_payment'):
            raise forms.ValidationError("Payment confirmation is required")
        if not cleaned_data.get('agree_terms'):
            raise forms.ValidationError("You must agree to the terms and conditions")
        return cleaned_data

    def save(self, commit=True):
        ad_account = super().save(commit=False)
        # Map agree_terms to terms_conditions_agreed
        ad_account.terms_conditions_agreed = self.cleaned_data.get('agree_terms')
        if commit:
            ad_account.save()
        return ad_account

class TransferAdAccountForm(forms.ModelForm):
    to_user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Transfer To")

    class Meta:
        model = AdAccountTransfer
        fields = ['ad_account', 'to_user']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['ad_account'].queryset = AdAccount.objects.filter(user=user)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')