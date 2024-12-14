# Generated by Django 5.1.3 on 2024-12-14 08:56

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0003_alter_rechargetransaction_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, 'Billing amount must be greater than zero')])),
                ('payment_method', models.CharField(choices=[('BKASH', 'bKash'), ('NAGAD', 'Nagad'), ('ROCKET', 'Rocket'), ('UPAY', 'Upay'), ('TAP', 'Tap'), ('BANK', 'Bank Transfer'), ('ONLINE', 'Online Payment'), ('AUTO_CARD', 'Automatic Credit Card'), ('AUTO_BANK', 'Automatic Bank Transfer')], default='ONLINE', max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')], default='PENDING', max_length=20)),
                ('transaction_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('description', models.CharField(help_text='Description of the billing transaction', max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice_url', models.URLField(blank=True, help_text='URL to download the invoice', null=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the billing transaction', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Billing Transaction',
                'verbose_name_plural': 'Billing Transactions',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserPaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('BKASH', 'bKash'), ('NAGAD', 'Nagad'), ('ROCKET', 'Rocket'), ('UPAY', 'Upay'), ('TAP', 'Tap'), ('BANK', 'Bank Transfer'), ('ONLINE', 'Online Payment'), ('AUTO_CARD', 'Automatic Credit Card'), ('AUTO_BANK', 'Automatic Bank Transfer')], max_length=20)),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]