# Let's create a simple test suite for the Calculator class using Python's built-in unittest module

import unittest

from calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_add(self):
        self.assertEqual(self.calculator.add(10, 5), 15)

    def test_subtract(self):
        self.assertEqual(self.calculator.subtract(10, 5), 5)

    def test_multiply(self):
        self.assertEqual(self.calculator.multiply(10, 5), 50)

    def test_divide(self):
        self.assertEqual(self.calculator.divide(10, 5), 2.0)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            self.calculator.divide(10, 0)

# Run the tests
unittest.main(argv=[''], exit=False)
