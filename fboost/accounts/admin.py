#fboost/accounts/admin.py


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, 
    AdAccount, 
    AdAccountTransfer, 
    Profile, 
    LoginHistory
)

# CustomUser Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'credit_balance', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'credit_balance')}),
    )

# AdAccount Admin
class AdAccountAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'user', 'account_type', 'payment_confirmed', 'created_at')
    list_filter = ('account_type', 'payment_confirmed', 'business_type', 'timezone')
    search_fields = ('account_name', 'user__username', 'business_manager_id')
    readonly_fields = ('created_at', 'updated_at')

# AdAccountTransfer Admin
class AdAccountTransferAdmin(admin.ModelAdmin):
    list_display = ('ad_account', 'from_user', 'to_user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('from_user__username', 'to_user__username', 'ad_account__account_name')

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'location', 'total_followers')
    list_filter = ('is_verified', 'timezone')
    search_fields = ('user__username', 'location')

# LoginHistory Admin
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username',)
    readonly_fields = ('timestamp',)

# Register all models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AdAccount, AdAccountAdmin)
admin.site.register(AdAccountTransfer, AdAccountTransferAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(LoginHistory, LoginHistoryAdmin)