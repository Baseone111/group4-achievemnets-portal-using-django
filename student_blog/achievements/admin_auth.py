from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

def staff_required(function=None, login_url='home'):
    """
    Decorator for views that checks that the user is staff (is_staff=True),
    redirecting to the homepage if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def superuser_required(function=None, login_url='home'):
    """
    Decorator for views that checks that the user is superuser,
    redirecting to the homepage if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url=login_url,
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator