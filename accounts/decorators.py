from django.contrib.auth.decorators import user_passes_test

def role_required(allowed_roles):
    def decorator(view_func):
        def check_role(user):
            if user.is_authenticated and user.role in allowed_roles:
                return True
            return False
        return user_passes_test(check_role, login_url='/accounts/login/')(view_func)
    return decorator

# Usage: @role_required(['admin', 'manager'])
