"""
Unit tests for the validator module.
"""

import unittest
from guess_simulator.validator import InputValidator, ValidationError


class TestInputValidator(unittest.TestCase):
    """Test cases for InputValidator class."""

    def test_validate_number_valid(self):
        """Test validating a valid number."""
        result = InputValidator.validate_number(50, 1, 100)
        self.assertEqual(result, 50)

    def test_validate_number_below_min(self):
        """Test number below minimum raises error."""
        with self.assertRaises(ValidationError) as context:
            InputValidator.validate_number(0, 1, 100)

        self.assertIn("between 1 and 100", str(context.exception))

    def test_validate_number_above_max(self):
        """Test number above maximum raises error."""
        with self.assertRaises(ValidationError) as context:
            InputValidator.validate_number(101, 1, 100)

        self.assertIn("between 1 and 100", str(context.exception))

    def test_validate_string_valid(self):
        """Test validating a valid string."""
        result = InputValidator.validate_string("test", min_length=1, max_length=10)
        self.assertEqual(result, "test")

    def test_validate_range_valid(self):
        """Test validating a valid range."""
        min_val, max_val = InputValidator.validate_range(1, 100)
        self.assertEqual(min_val, 1)
        self.assertEqual(max_val, 100)


if __name__ == "__main__":
    unittest.main()
