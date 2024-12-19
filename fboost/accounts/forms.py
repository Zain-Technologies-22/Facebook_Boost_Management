# accounts/forms.py

from django import forms
from .models import AdAccount, AdAccountTransfer, Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from .models import Profile
import pytz 



CustomUser = get_user_model()

class ProfileForm(forms.ModelForm):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    location = forms.CharField(max_length=100, required=False)
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        required=False
    )
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'location', 'timezone']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

def save(self, commit=True):
    profile = super().save(commit=False)
    if commit:
        profile.save()
        # Save user fields
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
    return profile


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