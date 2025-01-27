# credits/context_processors.py

def credit_balance(request):
    """
    Adds the user's credit balance to the template context.
    """
    if request.user.is_authenticated:
        return {'credit': {
            'balance': request.user.credit_balance
        }}
    return {'credit': {
        'balance': 0
    }}