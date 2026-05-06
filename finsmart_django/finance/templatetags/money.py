from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def comma_money(value):
    """Format numbers as comma-grouped integer text: 2000000 -> 2,000,000."""
    if value is None or value == "":
        return "0"

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    sign = "-" if amount < 0 else ""
    return f"{sign}{abs(int(amount)):,}"


@register.simple_tag(takes_context=True)
def money(context, value):
    """Format numbers with currency symbol based on user's currency preference.
    
    Usage in template: {% money transaction.amount %}
    
    Examples:
        VND: 2,000,000 ₫
        USD: $2,000,000
        EUR: €2,000,000
    """
    if value is None or value == "":
        return "0"

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    sign = "-" if amount < 0 else ""
    formatted_amount = f"{sign}{abs(int(amount)):,}"
    
    # Lấy currency từ user profile
    currency = 'VND'  # Mặc định
    user = context.get('user') or context.get('request', {}).get('user')
    if user and hasattr(user, 'profile'):
        currency = user.profile.currency
    
    # Thêm ký hiệu tiền tệ
    if currency == 'VND':
        return f"{formatted_amount} ₫"
    elif currency == 'USD':
        return f"${formatted_amount}"
    elif currency == 'EUR':
        return f"€{formatted_amount}"
    else:
        return f"{formatted_amount} {currency}"

