# credits/views.py
from accounts.models import AdAccount
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    MoneyTransaction,
    TransactionTypes,
    TransactionStatus,
    PaymentMethod,
    RechargeProof,
)
from .forms import (
    RechargeForm,
    BillingTransactionForm,
    AdAccountMoneyTransferForm,
)
import json

@login_required
def recharge_balance(request):
    """Handle recharge form submission"""
    if request.method == 'POST':
        form = RechargeForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            try:
                transaction = form.save()
                messages.success(request, "Recharge request submitted successfully! Awaiting confirmation.")
                return redirect('recharge_details', transaction_id=transaction.reference_id)
            except Exception as e:
                messages.error(request, f"Error processing your recharge: {str(e)}")
    else:
        form = RechargeForm(request.user)
    
    return render(request, 'credits/recharge_balance.html', {'form': form})

@login_required
def recharge_details(request, reference_id):
    """Show details of a specific recharge transaction"""
    transaction = get_object_or_404(
        MoneyTransaction,
        reference_id=reference_id,
        user=request.user
    )
    return render(request, 'credits/recharge_details.html', {'transaction': transaction})


@login_required
def billing_view(request):
    """Main billing and subscription view"""
    # Get all transactions first
    all_transactions = MoneyTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Calculate billing totals before pagination
    billing_total = all_transactions.filter(
        transaction_type=TransactionTypes.BILLING,
        status=TransactionStatus.COMPLETED
    ).count()
    
    billing_pending = all_transactions.filter(
        transaction_type=TransactionTypes.BILLING,
        status=TransactionStatus.PENDING
    ).count()
    
    # Then paginate
    paginator = Paginator(all_transactions, 10)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'recent_transactions': all_transactions[:5],  # Get first 5 from unpaginated queryset
        'billing_total': billing_total,
        'billing_pending': billing_pending
    }
    
    return render(request, 'credits/billing.html', context)

@login_required
def create_billing_transaction(request):
    """Create a new billing transaction"""
    if request.method == 'POST':
        form = BillingTransactionForm(request.user, request.POST)
        if form.is_valid():
            try:
                transaction = form.save()
                messages.success(request, "Billing transaction created successfully!")
                return redirect('billing')
            except Exception as e:
                messages.error(request, f"Error creating billing transaction: {str(e)}")
    else:
        form = BillingTransactionForm(request.user)
    
    return render(request, 'credits/create_billing_transaction.html', {'form': form})

@login_required
def download_invoice(request, reference_id):
    """Download invoice for a transaction"""
    transaction = get_object_or_404(
        MoneyTransaction,
        reference_id=reference_id,
        user=request.user
    )
    # Add your invoice generation logic here
    messages.info(request, "Invoice generation will be available soon.")
    return redirect('billing')

@login_required
def add_payment_method(request):
    """Add a new payment method"""
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_method = data.get('payment_method')
        
        if payment_method not in dict(PaymentMethod.choices):
            return JsonResponse({'success': False, 'error': 'Invalid payment method.'})
            
        try:
            # Add your payment method creation logic here
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def set_default_payment(request):
    """Set a payment method as default"""
    if request.method == 'POST':
        data = json.loads(request.body)
        # Add your default payment setting logic here
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def remove_payment_method(request, payment_id):
    """Remove a payment method"""
    if request.method == 'POST':
        # Add your payment method removal logic here
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def view_credits(request):
    """View user's current credit balance and transactions"""
    transactions = MoneyTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'credit': request.user.credit_balance,
        'recent_transactions': transactions
    }
    
    return render(request, 'credits/view_credits.html', context)

@login_required
def transfer_money(request):
    """Handle money transfers between accounts"""
    if request.method == 'POST':
        form = AdAccountMoneyTransferForm(request.user, request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.initial_balance = request.user.credit_balance 
                transaction = form.save()
                messages.success(request, "Transfer request submitted successfully!")
                return redirect('transfer_history')
            except Exception as e:
                messages.error(request, f"Error processing transfer: {str(e)}")
    else:
        form = AdAccountMoneyTransferForm(request.user)
    
    return render(request, 'credits/transfer_money.html', {'form': form})

@login_required
def transfer_history(request):
    """View transfer transaction history"""
    transfers = MoneyTransaction.objects.filter(
        user=request.user,
        transaction_type__in=[
            TransactionTypes.AD_ACCOUNT_DEPOSIT,
            TransactionTypes.AD_ACCOUNT_WITHDRAW
        ]
    ).order_by('-created_at')
    
    paginator = Paginator(transfers, 10)
    page = request.GET.get('page')
    transfers = paginator.get_page(page)
    
    return render(request, 'credits/transfer_history.html', {'transfers': transfers})

@login_required
def transaction_status(request, reference_id):
    """API endpoint to check transaction status"""
    transaction = get_object_or_404(
        MoneyTransaction,
        reference_id=reference_id,
        user=request.user
    )
    
    return JsonResponse({
        'status': transaction.get_status_display(),
        'updated_at': transaction.updated_at.isoformat(),
        'final_balance': float(transaction.final_balance) if transaction.final_balance else None,
    })

@login_required
def transaction_history(request):
    """View for all transactions history"""
    transactions = MoneyTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Add filtering by type if needed
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Add filtering by status if needed
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)

    # Paginate results
    paginator = Paginator(transactions, 10)  # 10 items per page
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    context = {
        'transactions': transactions,
        'transaction_types': TransactionTypes.choices,
    }
    
    return render(request, 'credits/recharge_history.html', context)

@login_required
def transaction_detail(request, reference_id):
    """View for individual transaction details"""
    transaction = get_object_or_404(
        MoneyTransaction,
        reference_id=reference_id,
        user=request.user
    )
    return render(request, 'credits/transaction_detail.html', {'transaction': transaction})

@login_required
def add_money_to_account(request, account_id):
    """Handle adding money to ad account"""
    ad_account = get_object_or_404(AdAccount, id=account_id, user=request.user)
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            
            # Validate amount
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
                
            # Check user balance
            if request.user.credit_balance < amount:
                messages.error(request, "Insufficient balance in your main account")
                return redirect('my_ad_account')
                
            # Create transaction
            transaction = MoneyTransaction.objects.create(
                user=request.user,
                ad_account=ad_account,
                amount=amount,
                transaction_type=TransactionTypes.AD_ACCOUNT_DEPOSIT,
                initial_balance=request.user.credit_balance,
                status=TransactionStatus.PENDING
            )
            
            messages.success(request, f"Added ৳{amount} to {ad_account.account_name}")
            return redirect('transaction_detail', reference_id=transaction.reference_id)
            
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "An error occurred while processing your request")
    
    return redirect('my_ad_account')

@login_required
def get_balance(request):
    """API endpoint to get current user balance"""
    return JsonResponse({
        'balance': float(request.user.credit_balance),
        'formatted_balance': f"৳{request.user.credit_balance:,.2f}"
    })