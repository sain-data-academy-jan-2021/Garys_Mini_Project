import unittest
from unittest import mock
from unittest.mock import patch

from .app import show_add_item_menu, show_update_item_menu


class TestShowAddItem(unittest.TestCase):

    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.dicts_to_table')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.insert')
    @patch('builtins.input')
    def test_should_create_new_dict(self, mock_input, mock_insert,
                                    mock_valid_input, mock_to_table, mock_all_rows):
        # Given
        mock_input.return_value = 'n'
        mock_all_rows.return_value = [{'id': 1, 'name': 'gary'}]
        mock_to_table.return_value = None
        mock_valid_input.return_value = 'glen'
        key = 'test'
        # When
        show_add_item_menu(key)

        # Then
        mock_insert.assert_called_with(key, {'id': 2, 'name': 'glen'})


    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.dicts_to_table')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.insert')
    @patch('builtins.input')
    def test_should_cancel_on_input(self, mock_input, mock_insert,
                                    mock_valid_input, mock_to_table, mock_all_rows):
        # Given
        mock_input.return_value = 'n'
        mock_all_rows.return_value = [{'id': 1, 'name': 'gary'}]
        mock_to_table.return_value = None
        mock_valid_input.return_value = False
        key = 'test'

        # When
        show_add_item_menu(key)
        
        # Then
        assert mock_insert.call_count == 0
        
        
class TestUpdateItemMenu(unittest.TestCase):

    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.dicts_to_table')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.update')
    @patch('builtins.input')
    def test_should_call_with_correct_dict(self, mock_input, mock_update, mock_valid_input, mock_table, mock_rows):
        #Given
        mock_input.return_value = 'n'
        mock_valid_input.side_effect = [1, 'gary', '555']
        mock_rows.return_value = [{'id': 1, 'name': 'gary', 'phone': '999'}]
        mock_table.return_value = None
        get_key = 'test'
        #When
        show_update_item_menu(get_key)
        
        #Then
        mock_update.assert_called_with(get_key, 1, {'id':1, 'name': 'gary', 'phone': '555'})
              

if __name__ == '__main__':
    unittest.main()
