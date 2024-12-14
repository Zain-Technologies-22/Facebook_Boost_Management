# credits/admin.py

from django.contrib import admin
from .models import RechargeTransaction, Credit, BillingTransaction, UserPaymentMethod

@admin.register(RechargeTransaction)
class RechargeTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'payment_method', 'status', 'timestamp')
    search_fields = ('transaction_id', 'user__username', 'user__email')
    list_filter = ('payment_method', 'status', 'timestamp')
    readonly_fields = ('transaction_id', 'timestamp', 'updated_at')

@admin.register(BillingTransaction)
class BillingTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'description', 'amount', 'payment_method', 'status', 'timestamp')
    search_fields = ('transaction_id', 'user__username', 'user__email', 'description')
    list_filter = ('payment_method', 'status', 'timestamp')
    readonly_fields = ('transaction_id', 'timestamp', 'updated_at')

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'last_updated')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('balance', 'last_updated')

@admin.register(UserPaymentMethod)
class UserPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'is_default')
    search_fields = ('user__username', 'user__email', 'payment_method')
    list_filter = ('payment_method', 'is_default')
    readonly_fields = ('payment_method',)