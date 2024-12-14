# credits/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RechargeForm, BillingTransactionForm
from .models import RechargeTransaction, BillingTransaction, PaymentMethod, Credit, UserPaymentMethod
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from .utils import generate_invoice_pdf, upload_invoice
import json
import os
from django.conf import settings

@login_required
def recharge_balance(request):
    """
    View to handle the recharge form submission
    """
    if request.method == 'POST':
        form = RechargeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                recharge_transaction = form.save()
                
                # Update Credit balance
                credit, created = Credit.objects.get_or_create(user=request.user)
                credit.balance += recharge_transaction.amount
                credit.save()
                
                messages.success(request, "Recharge submitted successfully! Awaiting confirmation.")
                return redirect('recharge_history')
            except Exception as e:
                messages.error(request, f"Error processing your recharge: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RechargeForm()
    
    return render(request, 'credits/recharge_balance.html', {'form': form})

@login_required
def recharge_history(request):
    """
    View to display recharge transaction history with pagination
    """
    transactions = RechargeTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    paginator = Paginator(transactions, 10)  # 10 recharge transactions per page
    page = request.GET.get('page')
    
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'credits/recharge_history.html', context)

@login_required
def recharge_details(request, transaction_id):
    """
    View to display details of a specific recharge transaction
    """
    transaction = get_object_or_404(RechargeTransaction, transaction_id=transaction_id, user=request.user)
    return render(request, 'credits/recharge_details.html', {'transaction': transaction})

@login_required
def billing_view(request):
    """
    Integrated Billing and Subscription view with tabs for current plan, payment methods, recharge history, and billing history
    """
    # Fetch user-related billing information
    try:
        credit = Credit.objects.get(user=request.user)
    except Credit.DoesNotExist:
        credit = Credit.objects.create(user=request.user, balance=0.00)
    
    # Fetch other billing-related data
    # Assume user has a 'plan' attribute; adjust based on your actual user model
    plan = getattr(request.user, 'plan', None)  # Replace with actual plan retrieval
    
    # Fetch user payment methods
    user_payment_methods = request.user.payment_methods.all()  # Adjust related_name if necessary
    
    # Fetch recharge and billing transactions
    transactions = RechargeTransaction.objects.filter(user=request.user).order_by('-timestamp')
    billing_transactions = BillingTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    # Calculate credit usage percentage (Assuming 'plan.credits' exists)
    if plan and hasattr(plan, 'credits') and plan.credits > 0:
        # Replace `credits_used` with actual logic to calculate used credits
        credits_used = getattr(credit, 'balance', 0)
        credits_percentage = min((credits_used / plan.credits) * 100, 100)
    else:
        credits_percentage = 0
    
    context = {
        'plan': plan,
        'user_payment_methods': user_payment_methods,
        'transactions': transactions,
        'billing_transactions': billing_transactions,
        'credit': credit,
        'credits_percentage': credits_percentage,
    }
    
    return render(request, 'credits/billing.html', context)

@login_required
def billing_history(request):
    """
    View to display billing transaction history with pagination
    """
    transactions = BillingTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    paginator = Paginator(transactions, 10)  # 10 billing transactions per page
    page = request.GET.get('page')
    
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    
    context = {
        'billing_transactions': transactions,
    }
    
    return render(request, 'credits/billing_history.html', context)

@login_required
def create_billing_transaction(request):
    """
    View to handle the creation of a billing transaction, such as plan upgrades
    """
    if request.method == 'POST':
        form = BillingTransactionForm(request.POST)
        if form.is_valid():
            try:
                billing_transaction = form.save(commit=False)
                billing_transaction.user = request.user
                billing_transaction.save()
                
                # Generate invoice
                invoice_pdf = generate_invoice_pdf(billing_transaction)
                invoice_url = upload_invoice(billing_transaction, invoice_pdf)
                billing_transaction.invoice_url = invoice_url
                billing_transaction.save()
                
                messages.success(request, "Billing transaction created successfully!")
                return redirect('billing_history')
            except Exception as e:
                messages.error(request, f"Error creating billing transaction: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BillingTransactionForm()
    
    return render(request, 'credits/create_billing_transaction.html', {'form': form})

@login_required
def download_invoice(request, transaction_id):
    """
    View to download the invoice PDF for a specific billing transaction
    """
    transaction = get_object_or_404(BillingTransaction, transaction_id=transaction_id, user=request.user)
    if transaction.invoice_url:
        return redirect(transaction.invoice_url)
    else:
        messages.error(request, "Invoice not available.")
        return redirect('billing_history')

@login_required
def add_payment_method(request):
    """
    View to handle adding a new payment method via AJAX
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_type = data.get('payment_method')
        if payment_type not in dict(PaymentMethod.choices):
            return JsonResponse({'success': False, 'error': 'Invalid payment method.'})
        try:
            # Assuming a UserPaymentMethod model exists linking users to payment methods
            # Replace with your actual implementation
            UserPaymentMethod.objects.create(user=request.user, payment_method=payment_type, is_default=False)
            messages.success(request, "Payment method added successfully!")
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def set_default_payment(request):
    """
    View to set a payment method as default via AJAX
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        try:
            payment_method = UserPaymentMethod.objects.get(id=payment_id, user=request.user)
            # Reset all other payment methods to non-default
            UserPaymentMethod.objects.filter(user=request.user).update(is_default=False)
            payment_method.is_default = True
            payment_method.save()
            return JsonResponse({'success': True})
        except UserPaymentMethod.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment method does not exist.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def remove_payment_method(request, payment_id):
    """
    View to remove a payment method via AJAX
    """
    if request.method == 'POST':
        try:
            payment_method = UserPaymentMethod.objects.get(id=payment_id, user=request.user)
            payment_method.delete()
            messages.success(request, "Payment method removed successfully!")
            return JsonResponse({'success': True})
        except UserPaymentMethod.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment method does not exist.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



@login_required
def view_credits(request):
    """
    Display the user's current credit balance and related information.
    """
    try:
        credit = Credit.objects.get(user=request.user)
    except Credit.DoesNotExist:
        credit = Credit.objects.create(user=request.user, balance=0.00)
    
    billing_transactions = BillingTransaction.objects.filter(user=request.user).order_by('-timestamp')[:5]  # Example: latest 5 billing transactions
    
    context = {
        'credit': credit,
        'billing_transactions': billing_transactions,
    }
    
    return render(request, 'credits/view_credits.html', context)