import unittest
from pathlib import Path
from file_system import get_absolute_path


class TestGetAbsoultePath(unittest.TestCase):

    def test_should_return_path_on_valid_string(self):
        # Given
        filename = './data/products.txt'
        exp = Path(
            '/Users/gary.spittel/Desktop/Bootcamp/Mini_Project/data/products.txt')
        # When
        res = get_absolute_path(filename)
        # Then
        self.assertEqual(exp, res)

    def test_should_return_self_if_not_supplied_relative_path(self):
        # Given
        filename = '/data/products.txt'
        exp = Path(filename)
        # When
        res = get_absolute_path(filename)
        # Then
        self.assertEqual(exp, res)

    def test_should_return_current_path_if_empty(self):
        # Given
        exp = Path('/Users/gary.spittel/Desktop/Bootcamp/Mini_Project')
        # When
        res = get_absolute_path()
        # Then
        self.assertEqual(exp, res)

    def test_should_return_error_on_none_string_type(self):
        # Given
        filename = 1
        exp = TypeError
        # When
        res = get_absolute_path(filename)
        # Then
        self.assertEqual(res, exp)


if __name__ == '__main__':
    unittest.main()
