import unittest
from unittest.mock import patch
from .cli import get_validated_input, validated_input


class TestValidatedInput(unittest.TestCase):

    @patch('src.cli.input', lambda x: 'test_string')
    def test_should_return_success_on_valid_str_input(self):
        # Given
        expected = 1

        # When
        result = validated_input('Please Input A Letter', str)[0]

        # Then
        self.assertEqual(expected, result)


    @patch('src.cli.input', lambda x: '1')
    def test_should_return_success_on_valid_int_input(self):
        # Given
        expected = 1

        # When
        result = validated_input('Please Input A Number', int)[0]

        # Then
        self.assertEqual(expected, result)


class TestGetValidatedInput(unittest.TestCase):

    @patch('src.cli.input', lambda x: '1')
    def test_should_return_str_as_int(self):
        #Given
        expected = 1
        
        #When
        actual = get_validated_input('Prompt', int)
        
        #Then
        self.assertEqual(expected, actual)
        
        
    @patch('src.cli.input', lambda x: '1.99')
    def test_should_return_str_as_float(self):
        #Given
        expected = 1.99

        #When
        actual = get_validated_input('Prompt', float)

        #Then
        self.assertEqual(expected, actual)


    @patch('src.cli.input')
    def test_should_loop_until_valid_input(self, mock_input):
        #Given
        mock_input.side_effect = ['string1','string2', '1.99']
        expected = 3
        
        #When
        get_validated_input('Prompt', float)
        
        #Then
        self.assertEqual(expected, mock_input.call_count)
        



if __name__ == '__main__':
    unittest.main()
