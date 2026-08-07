from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import List, Dict, Any, Union


def apply_discount(
    items: List[Dict[str, Any]],
    discount_percent: Union[int, float, str, Decimal]
) -> Decimal:
    """
    Calculates the total cost of items after applying a discount percentage.

    :param items: List of dicts, each with 'name' (str), 'unit_price' (Decimal), and 'quantity' (int)
    :param discount_percent: Discount percentage between 0 and 100
    :return: Total price after discount, rounded to 2 decimal places as a Decimal
    :raises ValueError: If discount_percent is < 0 or > 100, or item data is invalid
    :raises TypeError: If inputs are of invalid types or float is used for money
    """
    # Convert discount_percent to Decimal safely
    if isinstance(discount_percent, float):
        discount_dec = Decimal(str(discount_percent))
    elif isinstance(discount_percent, (int, str, Decimal)):
        discount_dec = Decimal(str(discount_percent)) if not isinstance(discount_percent, Decimal) else discount_percent
    else:
        raise TypeError(f"Unsupported discount_percent type: {type(discount_percent).__name__}")

    # Reject discounts below 0 or above 100
    if discount_dec < Decimal('0') or discount_dec > Decimal('100'):
        raise ValueError(f"Discount percentage must be between 0 and 100. Got: {discount_percent}")

    subtotal = Decimal('0.00')

    for item in items:
        if not isinstance(item, dict):
            raise TypeError(f"Item must be a dictionary, got {type(item).__name__}")

        if 'unit_price' not in item or 'quantity' not in item:
            raise ValueError("Item dict must contain 'unit_price' and 'quantity' keys")

        unit_price = item['unit_price']
        quantity = item['quantity']

        # Enforce Decimal for money (reject floats)
        if isinstance(unit_price, float):
            raise TypeError("unit_price must be a Decimal, float is strictly disallowed for money")

        if not isinstance(unit_price, Decimal):
            try:
                unit_price = Decimal(str(unit_price))
            except (InvalidOperation, TypeError):
                raise ValueError(f"Invalid unit_price value: {unit_price}")

        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise TypeError(f"Quantity must be an integer, got {type(quantity).__name__}")

        if quantity < 0:
            raise ValueError(f"Quantity cannot be negative, got {quantity}")
            
        print("Calculation shuru hocche!")
        subtotal += unit_price * Decimal(quantity)

    # Apply discount
    multiplier = Decimal('1') - (discount_dec / Decimal('100'))
    total = subtotal * multiplier

    # Round to 2 decimal places
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
