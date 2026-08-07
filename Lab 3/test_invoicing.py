import unittest
from decimal import Decimal
from invoicing import apply_discount


class TestApplyDiscount(unittest.TestCase):

    def test_empty_items_list_raises_error(self):  # Empty list should raise an error. I just want to check this out
        with self.assertRaises(ValueError):
            apply_discount([], 10)

    def test_basic_discount(self):
        items = [
            {'name': 'Widget A', 'unit_price': Decimal('10.00'), 'quantity': 2},
            {'name': 'Widget B', 'unit_price': Decimal('5.50'), 'quantity': 4},
        ]
        # Subtotal: (10.00 * 2) + (5.50 * 4) = 20.00 + 22.00 = 42.00
        # Discount 10%: 42.00 * 0.90 = 37.80
        result = apply_discount(items, 10)
        self.assertEqual(result, Decimal('37.80'))
        self.assertIsInstance(result, Decimal)

    def test_zero_percent_discount(self):
        items = [
            {'name': 'Item 1', 'unit_price': Decimal('15.99'), 'quantity': 1}
        ]
        result = apply_discount(items, 0)
        self.assertEqual(result, Decimal('15.99'))

    def test_hundred_percent_discount(self):
        items = [
            {'name': 'Item 1', 'unit_price': Decimal('99.99'), 'quantity': 3}
        ]
        result = apply_discount(items, 100)
        self.assertEqual(result, Decimal('0.00'))

    def test_rounding_to_two_decimal_places(self):
        items = [
            {'name': 'Item X', 'unit_price': Decimal('19.99'), 'quantity': 1}
        ]
        # Subtotal: 19.99
        # Discount 15%: 19.99 * 0.85 = 16.9915 -> rounds to 16.99
        result = apply_discount(items, 15)
        self.assertEqual(result, Decimal('16.99'))

    def test_rounding_half_up(self):
        items = [
            {'name': 'Item Y', 'unit_price': Decimal('10.00'), 'quantity': 1}
        ]
        # Discount 12.55%: 10.00 * (1 - 0.1255) = 10.00 * 0.8745 = 8.745 -> rounds up to 8.75
        result = apply_discount(items, Decimal('12.55'))
        self.assertEqual(result, Decimal('8.75'))

    def test_empty_items_list(self):
        with self.assertRaises(ValueError) as ctx:
            apply_discount([], 20)
        self.assertEqual(str(ctx.exception), "Items list cannot be empty")

    def test_reject_discount_below_zero(self):
        items = [{'name': 'Item', 'unit_price': Decimal('10.00'), 'quantity': 1}]
        with self.assertRaises(ValueError):
            apply_discount(items, -1)
        with self.assertRaises(ValueError):
            apply_discount(items, -0.01)

    def test_reject_discount_above_hundred(self):
        items = [{'name': 'Item', 'unit_price': Decimal('10.00'), 'quantity': 1}]
        with self.assertRaises(ValueError):
            apply_discount(items, 101)
        with self.assertRaises(ValueError):
            apply_discount(items, Decimal('100.01'))

    def test_reject_float_unit_price(self):
        items = [{'name': 'Item', 'unit_price': 10.50, 'quantity': 1}]
        with self.assertRaises(TypeError):
            apply_discount(items, 10)

    def test_reject_invalid_quantity(self):
        items = [{'name': 'Item', 'unit_price': Decimal('10.00'), 'quantity': -1}]
        with self.assertRaises(ValueError):
            apply_discount(items, 10)

        items_bad_type = [{'name': 'Item', 'unit_price': Decimal('10.00'), 'quantity': "2"}]
        with self.assertRaises(TypeError):
            apply_discount(items_bad_type, 10)

    def test_rounding_per_item(self):
        items = [
            {'name': 'Item A', 'unit_price': Decimal('2.675'), 'quantity': 1},
            {'name': 'Item B', 'unit_price': Decimal('2.675'), 'quantity': 1}
        ]
        # Item A: 2.675 round up hoye hobe 2.68
        # Item B: 2.675 round up hoye hobe 2.68
        # Sothik Total Hawa Uchit: 2.68 + 2.68 = 5.36
        # Kintu agent er vul code korbe: (2.675 + 2.675) = 5.350 -> round hoye 5.35
        
        result = apply_discount(items, 0)
        self.assertEqual(result, Decimal('5.36'))
if __name__ == '__main__':
    unittest.main()
