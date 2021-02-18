import unittest
from unittest.mock import patch

from pymysql import NULL

from .DbController import DbController

from .app import show_add_item_menu, show_add_order_menu, show_delete_item_menu, show_update_item_menu, show_update_order_menu, show_update_status_menu

DbController('','','','')

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
    @patch('src.app.clear', lambda: None)
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
              
    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.dicts_to_table')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.update')
    @patch('builtins.input')
    @patch('src.app.clear', lambda: None)
    def test_should_cancel(self, mock_input, mock_update, mock_valid_input, mock_table, mock_rows):
        
        #Given
        mock_input.return_value = 'n'
        mock_valid_input.return_value = False
        mock_rows.return_value = [{'id': 1, 'name': 'gary', 'phone': '999'}]
        get_key = 'test'
        
        #When
        show_update_item_menu(get_key)
        
        #Then
        assert mock_update.call_count == 0        


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


class TestAddOrder(unittest.TestCase):

    @patch('src.app.DbController.insert')
    @patch('src.app.get_validated_input')
    @patch('src.app.input')
    @patch('src.app.print', lambda x: None)
    @patch('src.app.dicts_to_table', lambda x, **a: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test'}])
    @patch('src.app.clear', lambda: None)
    def test_should_add_correct_dict(self, mock_input, mock_valid_input, mock_insert):
        #Given
        mock_input.side_effect = ['y', 'n']
        mock_valid_input.return_value = 'new_test'
        
        
        #When
        show_add_order_menu()
        
        #Then
        mock_insert.assert_called_with('orders', {'name':'new_test'})
        
    @patch('src.app.DbController.insert')
    @patch('src.app.get_validated_input')
    @patch('src.app.input')
    @patch('src.app.print', lambda x: None)
    @patch('src.app.dicts_to_table', lambda x, **kwargs: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test', 'basket': 1, 'courier': 1}])
    @patch('src.app.clear', lambda: None)
    def test_should_add_correct_dict_with_default(self, mock_input, mock_valid_input, mock_insert):
        #Given
        mock_input.side_effect = ['y', 'n']
        mock_valid_input.return_value = 'new_test'
        
        
        #When
        show_add_order_menu()
        
        #Then
        mock_insert.assert_called_with('orders', {'name':'new_test', 'basket': NULL})

    @patch('src.app.DbController.insert')
    @patch('src.app.get_validated_input')
    @patch('src.app.print', lambda x: None)
    @patch('src.app.dicts_to_table', lambda x, **a: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test', 'basket': 1}])
    @patch('src.app.clear', lambda: None)
    def test_should_cancel_add_order(self, mock_valid_input, mock_insert):
        #Given
        mock_valid_input.return_value = False
        
        
        #When
        show_add_order_menu()
        
        #Then
        assert mock_insert.call_count == 0


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


class TestUpdateOrder(unittest.TestCase):

    @patch('src.app.DbController.update')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.get_rows_where')
    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.select_order_items', lambda x: None) 
    @patch('src.app.input', lambda x: 'n') 
    @patch('src.app.print', lambda x: None)
    @patch('src.app.DbController.get_joins_where', lambda *v, **k: [{'id': 1, 'name': 'gary', 'phone': '999', 'status': 1}])
    @patch('src.app.dicts_to_table', lambda x: None)
    @patch('src.app.clear', lambda: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'gary', 'phone': '999','courier': 1, 'status': 1}])
    def test_update_order_should_call_on_correct_dict_with_skip(self, mock_all_rows, mock_rows_where, mock_input, mock_update):
        #Given
        mock_all_rows.side_effect = [
            [{'id': 1, 'code': 'pending', 'style': 'Red'}],
            [{'id': 1, 'name': 'test_courier', 'phone': '555'}]
        ]
        mock_rows_where.return_value =  [{'id': 1, 'name': 'gary', 'phone': '999','courier': 1, 'status': 1}]
        mock_input.side_effect = [1,False, False, False, False]
       
        #When
        show_update_order_menu()
        
        #Then
        mock_update.assert_called_with(
            'orders', 1, {'name':'gary', 'phone': '999', 'courier': 1, 'status': 1})
        

    @patch('src.app.DbController.update')
    @patch('src.app.get_validated_input')
    @patch('src.app.DbController.get_rows_where')
    @patch('src.app.DbController.get_all_rows')
    @patch('src.app.select_order_items', lambda x: None) 
    @patch('src.app.input', lambda x: 'n') 
    @patch('src.app.print', lambda x: None)
    @patch('src.app.DbController.get_joins_where', lambda *v, **k: [{'id': 1, 'name': 'gary', 'phone': '999', 'status': 1}])
    @patch('src.app.dicts_to_table', lambda x: None)
    @patch('src.app.clear', lambda: None)
    @patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'gary', 'phone': '999','courier': 1, 'status': 1}])
    def test_update_order_should_call_on_correct_dict_no_skip(self, mock_all_rows, mock_rows_where, mock_input, mock_update):
        #Given
        mock_all_rows.side_effect = [
            [{'id': 1, 'code': 'pending', 'style': 'Red'}],
            [{'id': 1, 'name': 'test_courier', 'phone': '555'}]
        ]
        mock_rows_where.return_value =  [{'id': 1, 'name': 'gary', 'phone': '999','courier': 1, 'status': 1}]
        mock_input.side_effect = [1,'new_name', 'new_phone', 2 , 2]
       
        #When
        show_update_order_menu()
        
        #Then
        mock_update.assert_called_with(
            'orders', 1, {'name':'new_name', 'phone': 'new_phone', 'courier': 2, 'status': 2})
        

if __name__ == '__main__':
    unittest.main()
