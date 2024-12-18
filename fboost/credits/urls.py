# credits/urls.py

from django.urls import path
from . import views


urlpatterns = [
    # Recharge URLs
    path('recharge/', views.recharge_balance, name='recharge_balance'),
    path('recharge/history/', views.recharge_history, name='recharge_history'),
    path('recharge/details/<str:transaction_id>/', views.recharge_details, name='recharge_details'),
    
    # Billing URLs
    path('billing/', views.billing_view, name='billing'),
    path('billing/history/', views.billing_history, name='billing_history'),
    path('billing/create/', views.create_billing_transaction, name='create_billing_transaction'),
    path('billing/invoice/<str:transaction_id>/', views.download_invoice, name='download_invoice'),
    
    # Payment Method URLs
    path('payment-methods/add/', views.add_payment_method, name='add_payment_method'),
    path('payment-methods/set-default/', views.set_default_payment, name='set_default_payment'),
    path('payment-methods/remove/<int:payment_id>/', views.remove_payment_method, name='remove_payment_method'),

    # New URL Pattern for View Credits
    path('credits/', views.view_credits, name='view_credits'),
    
  ]