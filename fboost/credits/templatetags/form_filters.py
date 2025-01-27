# credits/templatetags/form_filters.py

from django import template
from ..models import MoneyTransaction, TransactionTypes

register = template.Library()
@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value
    
@register.filter
def model_type(instance):
    """
    Determine the type of transaction based on the TransactionTypes.
    Returns a user-friendly string identifier.
    """
    if isinstance(instance, MoneyTransaction):
        if instance.transaction_type == TransactionTypes.RECHARGE:
            return "recharge"
        elif instance.transaction_type == TransactionTypes.BILLING:
            return "billing"
        elif instance.transaction_type == TransactionTypes.AD_ACCOUNT_DEPOSIT:
            return "ad_deposit"
        elif instance.transaction_type == TransactionTypes.AD_ACCOUNT_WITHDRAW:
            return "ad_withdraw"
    return "unknown"

@register.filter
def transaction_css_class(transaction_type):
    """
    Returns appropriate CSS classes based on transaction type
    """
    css_classes = {
        TransactionTypes.RECHARGE: 'bg-success',
        TransactionTypes.BILLING: 'bg-primary',
        TransactionTypes.AD_ACCOUNT_DEPOSIT: 'bg-info',
        TransactionTypes.AD_ACCOUNT_WITHDRAW: 'bg-warning'
    }
    return css_classes.get(transaction_type, 'bg-secondary')

@register.filter
def transaction_icon(transaction_type):
    """
    Returns appropriate icon class based on transaction type
    """
    icons = {
        TransactionTypes.RECHARGE: 'bi-plus-circle',
        TransactionTypes.BILLING: 'bi-credit-card',
        TransactionTypes.AD_ACCOUNT_DEPOSIT: 'bi-box-arrow-in-down',
        TransactionTypes.AD_ACCOUNT_WITHDRAW: 'bi-box-arrow-up'
    }
    return icons.get(transaction_type, 'bi-question-circle')

@register.simple_tag
def transaction_display(transaction):
    """
    Returns a formatted display string for the transaction
    """
    type_names = {
        TransactionTypes.RECHARGE: 'Recharge',
        TransactionTypes.BILLING: 'Billing',
        TransactionTypes.AD_ACCOUNT_DEPOSIT: 'Ad Account Deposit',
        TransactionTypes.AD_ACCOUNT_WITHDRAW: 'Ad Account Withdrawal'
    }
    
    return type_names.get(transaction.transaction_type, 'Unknown Transaction')