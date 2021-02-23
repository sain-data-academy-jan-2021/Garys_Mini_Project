import unittest
from unittest.mock import patch

from pymysql import NULL

from .DbController import DbController

from .app import show_add_item_menu, show_add_order_menu, show_delete_item_menu, show_update_item_menu, show_update_order_menu, show_update_status_menu

DbController('','','','')

        
class TestDeleteItemMenu(unittest.TestCase):

    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.delete')
    @patch('src.app.dicts_to_table', lambda x: None)
    @patch('src.app.input', lambda x: 'n')
    @patch('src.app.clear', lambda: None)
    def test_should_call_correct_delete(self, mock_delete, mock_valid_input, mock_rows):
        #Given
        mock_valid_input.return_value = 1
        mock_rows.return_value = [{'id': 1, 'name': 'gary', 'phone': '999'}]
        get_key = 'test'
        
        #When
        show_delete_item_menu(get_key)
        
        #Then
        mock_delete.assert_called_with(get_key, 1)

class TestUpdateStatus(unittest.TestCase):

    @patch('src.app.DbController.update')  
    @patch('src.app.get_validated_input')  
    @patch('src.app.input', lambda x: 'n')  
    @patch('src.app.print', lambda x: None)
    @patch('src.app.DbController.get_rows_where', lambda *a: [{'id': 1, 'name': 'gary', 'phone': '999', 'status': 1}])   
    @patch('src.app.DbController.get_all_rows', lambda *a: [{'id': 2, 'code': 'test_status'}])
    @patch('src.app.dicts_to_table', lambda x: None)
    @patch('src.app.clear', lambda: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test', 'status': 1}])
    def test_update_status_should_call_correct_dict(self, mock_valid_input, mock_update):
        #Given
        mock_valid_input.side_effect = [1, 2]

        #When
        show_update_status_menu()        
        
        #Then
        mock_update.assert_called_with(
            'orders', 1, {'id': 1, 'name': 'gary', 'phone': '999', 'status': 2})
        
        
    @patch('src.app.DbController.update')  
    @patch('src.app.get_validated_input')  
    @patch('src.app.DbController.get_all_rows', lambda *a: [{'id': 2, 'code': 'test_status'}])
    @patch('src.app.dicts_to_table', lambda x: None)
    @patch('src.app.clear', lambda: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test', 'status': 1}])
    def test_should_cancel_update_status(self, mock_valid_input, mock_update):
        #Given
        mock_valid_input.return_value = False

        #When
        show_update_status_menu()        
        
        #Then
        assert mock_update.call_count == 0

     

if __name__ == '__main__':
    unittest.main()
