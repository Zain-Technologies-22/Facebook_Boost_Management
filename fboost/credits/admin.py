# credits/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from .models import (
    MoneyTransaction,
    TransactionAuditLog,
    RechargeProof,
    TransactionTypes,
    TransactionStatus
)

@admin.register(MoneyTransaction)
class MoneyTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id',
        'user_link',
        'amount_display',
        'transaction_type',
        'status',
        'payment_method',
        'created_at',
        'processed_by'
    )
    
    list_filter = (
        'status',
        'transaction_type',
        'created_at',
        ('processed_by', admin.RelatedOnlyFieldListFilter),
    )
    
    search_fields = (
        'reference_id',
        'user__username',
        'user__email',
        'notes',
        'admin_notes'
    )
    
    readonly_fields = (
        'reference_id',
        'initial_balance',
        'final_balance',
        'created_at',
        'updated_at'
    )

    def user_link(self, obj):
        # Fixed URL pattern for custom user model
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    def amount_display(self, obj):
        amount = float(obj.amount)
        formatted_amount = '{:,.2f}'.format(amount)
        return format_html('৳{}', formatted_amount)
    amount_display.short_description = 'Amount'

    actions = ['approve_transactions', 'reject_transactions']

    def approve_transactions(self, request, queryset):
        success_count = 0
        error_count = 0
        
        for transaction in queryset.filter(status=TransactionStatus.PENDING):
            if transaction.process_transaction(request.user):
                success_count += 1
            else:
                error_count += 1
        
        if success_count:
            self.message_user(
                request,
                f"{success_count} transaction(s) successfully approved."
            )
        if error_count:
            self.message_user(
                request,
                f"{error_count} transaction(s) failed to process. Check transaction logs for details.",
                level='ERROR'
            )
    approve_transactions.short_description = "Approve selected transactions"

    def reject_transactions(self, request, queryset):
        count = queryset.filter(status=TransactionStatus.PENDING).update(
            status=TransactionStatus.REJECTED,
            processed_by=request.user,
            admin_notes="Rejected through admin action"
        )
        
        self.message_user(
            request,
            f"{count} transaction(s) marked as rejected."
        )
    reject_transactions.short_description = "Reject selected transactions"

    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'reference_id',
                'user',
                'transaction_type',
                'amount',
                'status',
                'payment_method',
            )
        }),
        ('Balance Information', {
            'fields': (
                'initial_balance',
                'final_balance',
            )
        }),
        ('Notes', {
            'fields': (
                'notes',
                'admin_notes',
            )
        }),
        ('Processing Information', {
            'fields': (
                'processed_by',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(TransactionAuditLog)
class TransactionAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'transaction',
        'timestamp',
        'action',
        'performed_by',
        'old_status',
        'new_status'
    )
    list_filter = ('action', 'timestamp')
    search_fields = ('transaction__reference_id', 'notes')
    readonly_fields = (
        'transaction',
        'timestamp',
        'action',
        'performed_by',
        'old_status',
        'new_status',
        'balance_change',
        'notes'
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(RechargeProof)
class RechargeProofAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'sender_phone', 'bank_reference')
    search_fields = (
        'transaction__reference_id',
        'sender_phone',
        'bank_reference'
    )
    readonly_fields = ('transaction',)