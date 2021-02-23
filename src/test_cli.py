from typing import overload
import unittest
from unittest.mock import patch, Mock

from .cli import dict_builder, dicts_to_table, fmt_string, get_validated_input, list_to_table, validated_input


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

    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_int_max_value(self, mock_input):
        #Given
        mock_input.side_effect = [2, 1]
        
        #When
        get_validated_input('Test', int, max_value=1)
        
        #Then
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_int_min_value(self, mock_input):
        #Given
        mock_input.side_effect = [1, 2]
        
        #When
        get_validated_input('Test', int, min_value=2)
        
        #Then
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_float_max_value(self, mock_input):
        #Given
        mock_input.side_effect = [2.5, 1.5]

        #When
        get_validated_input('Test', float, max_value=1.5)

        #Then
        self.assertEqual(mock_input.call_count, 2)

    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_float_min_value(self, mock_input):
        #Given
        mock_input.side_effect = [1.5, 2.5]

        #When
        get_validated_input('Test', float, min_value=2.5)

        #Then
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_unique(self, mock_input):
        #Given
        unique = ['not unique']
        mock_input.side_effect = ['Not Unique', 'Unique']

        #When
        get_validated_input('Test', str, unique=unique)

        #Then
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_is_present(self, mock_input):
        #Given
        lst = ['not unique']
        mock_input.side_effect = ['Unique', 'Not Unique']

        #When
        get_validated_input('Test', str, is_present=lst)

        #Then
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_is_max_length(self, mock_input):
        #Given
        mock_input.side_effect = ['1234', '123']

        #When
        get_validated_input('Test', str, max_length=3)

        #Then
        self.assertEqual(mock_input.call_count, 2)
        
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_apply_is_min_length(self, mock_input):
        #Given
        mock_input.side_effect = ['123', '1234']

        #When
        get_validated_input('Test', str, min_length=4)

        #Then
        self.assertEqual(mock_input.call_count, 2)
    
    @patch('src.cli.input')
    @patch('builtins.print', lambda x: None)
    def test_should_escape_float(self, mock_input):
        #Given
        mock_input.return_value = 'Name."\\,.,.'
        expected = 'name'
        
        #When
        actual = get_validated_input('Test', str)
        
        #Then
        self.assertEqual(expected, actual)
        
        

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


@patch('src.cli.get_validated_input')
class TestDictBulider(unittest.TestCase):

    def test_should_build_dict_no_kwargs(self, mock_input):
        #Given
        schema = {'id': int, 'name': str}
        mock_input.side_effect = [1, 'Test Name']
        expected = {'id': 1, 'name': 'Test Name'}
        
        #When
        actual = dict_builder(schema)
        
        #Then
        self.assertEqual(expected, actual)
        
    def test_should_return_empty_if_no_schema(self, mock_input):
        #Given
        expected = {}
        
        #When
        actual = dict_builder({})
 
        #Then
        self.assertEqual(expected, actual)
        
    def test_should_ignore_given_keys(self, mock_input):
        #Given
        schema = {'id': int, 'name': str}
        ignore_keys = ['id']
        mock_input.return_value = 'Test Name'
        expected = {'name': 'Test Name'}
        
        #When
        actual = dict_builder(schema, ignore_keys=ignore_keys)
        
        #Then
        self.assertEqual(expected, actual)
        
    def test_should_apply_correct_defaults(self, mock_input):
        #Given
        schema = {'id': int, 'name': str}
        defaults = {'name': 'default_value'}
        mock_input.side_effect = [1, False]
        expected = {'id': 1, 'name': 'default_value'}
        
        #When
        actual = dict_builder(schema, defaults=defaults)
        
        #Then
        self.assertEqual(expected, actual)
        
    def test_should_run_correct_on_key_function(self, mock_input):
        #Given
        mock_func = Mock()
        schema = {'id': int}
        on_key = {'id': [mock_func]}
        mock_input.return_value = 1
        call_count = 1
        
        #When
        dict_builder(schema, on_key=on_key)
        
        #Then
        self.assertEqual(mock_func.call_count, call_count)
    
    def test_should_return_correct_dict_on_override(self, mock_input):
        #Given
        mock_input.side_effect = [False, 'New Name']
        schema = {'id': int, 'name': str}
        override = {'id': 2}
        defaults = {'id': 1, 'name': 'Test Name'}
        expected = {'id': 2, 'name': 'New Name'}
        
        #When
        actual = dict_builder(schema,defaults=defaults, override=override)
        
        #Then
        self.assertEqual(expected, actual)
    
    def test_should_skip_on_cancel(self, mock_input):
        #Given
        mock_input.side_effect = [1, False]
        schema = {'id': 1, 'name': str}
        on_cancel = 'skip'
        expected = {'id': 1}
        
        #When
        actual = dict_builder(schema, on_cancel=on_cancel)
        
        #Then
        self.assertEqual(expected, actual)

 
class TestFmtString(unittest.TestCase):

    def test_behaviour(self):
        #Given
        fg = 'White'
        bg='Red'
        msg = 'Test'
        expected = '\u001b[37;1m\u001b[41;1mTest\u001b[0m'
        
        #When
        actual = fmt_string(msg, fg, bg)
        
        #Then
        self.assertEqual(expected, actual)
        
           
    
if __name__ == '__main__':
    unittest.main()
