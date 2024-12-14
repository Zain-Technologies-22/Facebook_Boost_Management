# credits/context_processors.py

from .models import Credit

def credit_balance(request):
    """
    Adds the user's credit balance to the template context.
    """
    if request.user.is_authenticated:
        try:
            credit = Credit.objects.get(user=request.user)
        except Credit.DoesNotExist:
            credit = Credit.objects.create(user=request.user, balance=0.00)
        return {'credit': credit}
    return {}