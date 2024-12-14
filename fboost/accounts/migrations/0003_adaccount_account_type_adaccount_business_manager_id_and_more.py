# Generated by Django 5.1.3 on 2024-12-03 08:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_adaccount_adaccounttransfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='adaccount',
            name='account_type',
            field=models.CharField(choices=[('PERSONAL', 'Personal Account'), ('BUSINESS', 'Business Account'), ('AGENCY', 'Agency Account')], default='PERSONAL', max_length=20),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='business_manager_id',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[django.core.validators.RegexValidator('^[0-9]+$', 'Business Manager ID must be a number')]),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='business_type',
            field=models.CharField(blank=True, choices=[('SOLE', 'Sole Proprietorship'), ('LLC', 'Limited Liability Company'), ('CORP', 'Corporation'), ('NONPROFIT', 'Non-Profit Organization'), ('PARTNERSHIP', 'Partnership')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='facebook_page_url_1',
            field=models.URLField(default='https://www.facebook.com/placeholder', help_text='Primary Facebook Page URL', max_length=500),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='facebook_page_url_2',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='facebook_page_url_3',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='facebook_page_url_4',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='facebook_page_url_5',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='payment_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='terms_conditions_agreed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='timezone',
            field=models.CharField(choices=[('US/Eastern', 'US Eastern'), ('US/Central', 'US Central'), ('US/Mountain', 'US Mountain'), ('US/Pacific', 'US Pacific'), ('UTC', 'UTC')], default='UTC', max_length=20),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='website_url_1',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='adaccount',
            name='website_url_2',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
