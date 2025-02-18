# Generated by Django 5.1.3 on 2025-01-17 09:39

import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_profile_location_profile_timezone'),
        ('credits', '0004_billingtransaction_userpaymentmethod'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credit',
            name='user',
        ),
        migrations.RemoveField(
            model_name='rechargetransaction',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userpaymentmethod',
            name='user',
        ),
        migrations.CreateModel(
            name='MoneyTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('transaction_type', models.CharField(choices=[('RECHARGE', 'Account Recharge'), ('BILLING', 'Billing Payment'), ('AD_DEPOSIT', 'Deposit to Ad Account'), ('AD_WITHDRAW', 'Withdraw from Ad Account')], max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled'), ('REFUNDED', 'Refunded')], default='PENDING', max_length=20)),
                ('payment_method', models.CharField(blank=True, choices=[('BKASH', 'bKash'), ('NAGAD', 'Nagad'), ('ROCKET', 'Rocket'), ('UPAY', 'Upay'), ('TAP', 'Tap'), ('BANK', 'Bank Transfer'), ('ONLINE', 'Online Payment'), ('AUTO_CARD', 'Automatic Credit Card'), ('AUTO_BANK', 'Automatic Bank Transfer')], max_length=20, null=True)),
                ('initial_balance', models.DecimalField(decimal_places=2, help_text="User's balance before transaction", max_digits=10)),
                ('final_balance', models.DecimalField(blank=True, decimal_places=2, help_text="User's balance after transaction", max_digits=10, null=True)),
                ('reference_id', models.CharField(help_text='External reference ID (e.g., payment gateway ID)', max_length=100, null=True, unique=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ad_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='accounts.adaccount')),
                ('processed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_transactions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='money_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'permissions': [('can_process_transactions', 'Can process money transactions'), ('can_view_all_transactions', 'Can view all transactions')],
            },
        ),
        migrations.CreateModel(
            name='RechargeProof',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proof_file', models.FileField(help_text='Payment receipt or screenshot', upload_to='recharge_proofs/')),
                ('sender_phone', models.CharField(blank=True, help_text="Sender's phone number for mobile banking", max_length=15, null=True)),
                ('bank_reference', models.CharField(blank=True, help_text='Bank transfer reference number', max_length=100, null=True)),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recharge_proof', to='credits.moneytransaction')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=50)),
                ('old_status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled'), ('REFUNDED', 'Refunded')], max_length=20)),
                ('new_status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled'), ('REFUNDED', 'Refunded')], max_length=20)),
                ('balance_change', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_logs', to='credits.moneytransaction')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.DeleteModel(
            name='BillingTransaction',
        ),
        migrations.DeleteModel(
            name='Credit',
        ),
        migrations.DeleteModel(
            name='RechargeTransaction',
        ),
        migrations.DeleteModel(
            name='UserPaymentMethod',
        ),
        migrations.AddIndex(
            model_name='moneytransaction',
            index=models.Index(fields=['user', 'transaction_type', 'status'], name='credits_mon_user_id_a0db7d_idx'),
        ),
        migrations.AddIndex(
            model_name='moneytransaction',
            index=models.Index(fields=['reference_id'], name='credits_mon_referen_c75ed5_idx'),
        ),
        migrations.AddIndex(
            model_name='moneytransaction',
            index=models.Index(fields=['created_at'], name='credits_mon_created_72a81d_idx'),
        ),
    ]
