import unittest
from cli import validated_input


class TestValidatedInput(unittest.TestCase):

    def test_should_return_success_on_valid_str_input(self):
        # Given
        def input(prompt): return 'test_string'
        expected = 1

        # When
        result = validated_input('Please Input A Letter', [str], {}, input=input)[0]

        # Then
        self.assertEquals(expected, result)

    def test_should_return_success_on_valid_int_input(self):
        # Given
        def input(prompt): return 1
        expected = 1

        # When
        result = validated_input('Please Input A Letter', [int], {}, input=input)[0]

        # Then
        self.assertEquals(expected, result)


if __name__ == '__main__':
    unittest.main()
