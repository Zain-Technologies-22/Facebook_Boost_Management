# Generated by Django 5.1.3 on 2024-12-03 10:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0002_credit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rechargetransaction',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Recharge Transaction', 'verbose_name_plural': 'Recharge Transactions'},
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='bank_reference',
            field=models.CharField(blank=True, help_text='Bank transfer or reference number', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='notes',
            field=models.TextField(blank=True, help_text='Additional notes about the transaction', null=True),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='payment_method',
            field=models.CharField(choices=[('BKASH', 'bKash'), ('NAGAD', 'Nagad'), ('ROCKET', 'Rocket'), ('UPAY', 'Upay'), ('TAP', 'Tap'), ('BANK', 'Bank Transfer'), ('ONLINE', 'Online Payment'), ('AUTO_CARD', 'Automatic Credit Card'), ('AUTO_BANK', 'Automatic Bank Transfer')], default='BKASH', max_length=20),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='payment_proof',
            field=models.FileField(blank=True, help_text='Upload payment receipt or screenshot', null=True, upload_to='recharge_proofs/'),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='sender_phone_number',
            field=models.CharField(blank=True, help_text='Phone number used for mobile banking transaction', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='transaction_id',
            field=models.CharField(blank=True, help_text='Unique transaction identifier from payment gateway', max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='rechargetransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, 'Recharge amount must be greater than zero')]),
        ),
        migrations.AlterField(
            model_name='rechargetransaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recharge_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]