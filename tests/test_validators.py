
import unittest
from modules import validators


class TestValidateMenuChoice(unittest.TestCase):
    def test_valid_choice(self):
        self.assertEqual(validators.validate_menu_choice("2", {"1", "2", "3"}), "2")

    def test_valid_choice_with_whitespace(self):
        self.assertEqual(validators.validate_menu_choice("  2  ", {"1", "2", "3"}), "2")

    def test_invalid_choice(self):
        self.assertIsNone(validators.validate_menu_choice("9", {"1", "2", "3"}))

    def test_empty_input(self):
        self.assertIsNone(validators.validate_menu_choice("", {"1", "2", "3"}))

    def test_none_input(self):
        self.assertIsNone(validators.validate_menu_choice(None, {"1", "2", "3"}))

    def test_non_numeric_junk(self):
        self.assertIsNone(validators.validate_menu_choice("abc", {"1", "2", "3"}))


class TestValidateNonEmptyString(unittest.TestCase):
    def test_normal_string(self):
        self.assertEqual(validators.validate_non_empty_string("  iPhone  "), "iPhone")

    def test_empty_string(self):
        self.assertIsNone(validators.validate_non_empty_string(""))

    def test_whitespace_only(self):
        self.assertIsNone(validators.validate_non_empty_string("    "))

    def test_none(self):
        self.assertIsNone(validators.validate_non_empty_string(None))


class TestValidatePositiveInt(unittest.TestCase):
    def test_valid_positive(self):
        self.assertEqual(validators.validate_positive_int("10"), 10)

    def test_zero_is_rejected(self):
        self.assertIsNone(validators.validate_positive_int("0"))

    def test_negative_is_rejected(self):
        self.assertIsNone(validators.validate_positive_int("-5"))

    def test_non_numeric_is_rejected(self):
        self.assertIsNone(validators.validate_positive_int("ten"))

    def test_float_string_is_rejected(self):
        self.assertIsNone(validators.validate_positive_int("3.5"))

    def test_empty_string(self):
        self.assertIsNone(validators.validate_positive_int(""))


class TestValidateDateString(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(validators.validate_date_string("2026-05-10"), "2026-05-10")

    def test_wrong_format(self):
        self.assertIsNone(validators.validate_date_string("10/05/2026"))

    def test_impossible_date(self):
        self.assertIsNone(validators.validate_date_string("2026-02-30"))

    def test_empty_string(self):
        self.assertIsNone(validators.validate_date_string(""))


class TestValidateYesNo(unittest.TestCase):
    def test_yes_variants(self):
        for val in ("y", "Y", "yes", "YES"):
            self.assertTrue(validators.validate_yes_no(val))

    def test_no_variants(self):
        for val in ("n", "N", "no", "NO"):
            self.assertFalse(validators.validate_yes_no(val))

    def test_unrecognised_input(self):
        self.assertIsNone(validators.validate_yes_no("maybe"))

    def test_empty_string(self):
        self.assertIsNone(validators.validate_yes_no(""))


if __name__ == "__main__":
    unittest.main()
