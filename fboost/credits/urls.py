# credits/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('recharge/', views.recharge_balance, name='recharge_balance'),
    path('recharge/details/<str:reference_id>/', views.recharge_details, name='recharge_details'),
        
    # Billing URLs
    path('billing/', views.billing_view, name='billing'),
    path('billing/create/', views.create_billing_transaction, name='create_billing_transaction'),
    path('billing/invoice/<str:reference_id>/', views.download_invoice, name='download_invoice'),
        
    # Payment Method URLs
    path('payment-methods/add/', views.add_payment_method, name='add_payment_method'),
    path('payment-methods/set-default/', views.set_default_payment, name='set_default_payment'),
    path('payment-methods/remove/<int:payment_id>/', views.remove_payment_method, name='remove_payment_method'),
    
    # View Credits URL
    path('credits/', views.view_credits, name='view_credits'),
    
    # Transfer URLs
    path('transfer/money/', views.transfer_money, name='transfer_money'),
    path('transfer/history/', views.transfer_history, name='transfer_history'),
    
    # Transaction History URLs (new)
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transaction/<str:reference_id>/', views.transaction_detail, name='transaction_detail'),
    
    # API Endpoints
    path('api/transaction-status/<str:reference_id>/', views.transaction_status, name='transaction_status'),
    path('account/<int:account_id>/add-money/', views.add_money_to_account, name='add_money_to_account'),
    path('api/get-balance/', views.get_balance, name='get_balance'),
   
]


