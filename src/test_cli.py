import unittest
from unittest.mock import patch

from .cli import dicts_to_table, get_validated_input, list_to_table, validated_input


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
        # Given
        expected = 1

        # When
        actual = get_validated_input('Prompt', int)

        # Then
        self.assertEqual(expected, actual)

    @patch('src.cli.input', lambda x: '1.99')
    def test_should_return_str_as_float(self):
        # Given
        expected = 1.99

        # When
        actual = get_validated_input('Prompt', float)

        # Then
        self.assertEqual(expected, actual)

    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_loop_until_valid_input(self, mock_input):
        # Given
        mock_input.side_effect = ['string1', 'string2', '1.99']
        expected = 3

        # When
        get_validated_input('Prompt', float)

        # Then
        self.assertEqual(expected, mock_input.call_count)


@patch('src.cli.print', lambda x: None)
@patch('src.cli.input', lambda x: '')
@patch('src.cli.SingleTable')
class TestDictsToTable(unittest.TestCase):

    def test_should_create_correct_dict_from_list(self, mock_table):
        # Given
        lst = [{'id': 1, 'name': 'gary'}]
        expected = [['Id', 'Name'], ['1', 'Gary']]
        mock_table.table = lambda: None

        # When
        dicts_to_table(lst)

        # Then
        mock_table.assert_called_with(expected)

    def test_should_create_correct_dict_from_list_paginated(self, mock_table):
        # Given
        lst = [
            {'id': 1, 'name': 'gary'},
            {'id': 2, 'name': 'glen'},
            {'id': 3, 'name': 'mark'},
            {'id': 4, 'name': 'dawn'}
        ]
        expected = [['Id', 'Name'], ['1', 'Gary'], ['2', 'Glen']]
        mock_table.table = lambda: None
        # When
        dicts_to_table(lst, paginate=True, page_length=2)

        # Then
        mock_table.assert_called_with(expected)

    def test_should_create_correct_dict_from_list_enumerated(self, mock_table):
        # Given
        lst = [{'name': 'gary'}]
        expected = [['ID', 'Name'], [1, 'Gary']]
        mock_table.table = lambda: None

        # When
        dicts_to_table(lst, enumerated=True)

        # Then
        mock_table.assert_called_with(expected)


@patch('src.cli.print', lambda x: None)
@patch('src.cli.SingleTable')
class TestListToTable(unittest.TestCase):

    def test_should_create_correct_table(self, mock_table):
        # Given
        lst = ['Row 1', 'Separator', 'Row 2']
        expected = [['Row 1'], ['           ---           '], ['Row 2']]
        mock_table.table = lambda: None

        # When
        list_to_table(lst, 'test')

        # Then
        mock_table.assert_called_with(expected, title='test')

    def test_should_create_correct_table_enumerated(self, mock_table):
        # Given
        lst = ['Row 1', 'Row 2']
        expected = [['[1] Row 1'], ['[2] Row 2']]
        mock_table.table = lambda: None

        # When
        list_to_table(lst, 'test', enumerate=True)

        # Then
        mock_table.assert_called_with(expected, title='test')

    def test_should_create_correct_table_spilled(self, mock_table):
        # Given
        lst = ['Row 1', 'Row 2', 'Row 3', 'Row 4']
        expected = [['[1] Row 1', '[2] Row 2'], ['[3] Row 3', '[4] Row 4']]
        mock_table.table = lambda: None

        # When
        list_to_table(lst, 'test', enumerate=True, max_length=2)

        # Then
        mock_table.assert_called_with(expected, title='test')


if __name__ == '__main__':
    unittest.main()
