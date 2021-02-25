import unittest
from unittest.mock import patch

from pymysql import NULL

from src.DbController import DbController

from src.app import get_cats, show_add_item_menu, show_add_order_menu, show_delete_item_menu, show_update_item_menu, show_update_order_menu, show_update_status_menu

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


@patch('src.app.DbController.get_all_rows', lambda *a: [{'id': 1, 'name': 'test_catagory'}])
class TestGetCats(unittest.TestCase):
    
    def test_should_return_data_with_no_cat(self):
        #Given
        data = [{'id': 1, 'name': 'test_name', 'catagory': 1}]
        expected = [{'id': 1, 'name': 'test_name'}]
        
        #When
        actual = get_cats(data, 'delete')
        
        #Then
        self.assertEqual(expected, actual)
        
    def test_should_return_data_with_cat_name(self):
        #Given
        data = [{'id': 1, 'name': 'test_name', 'catagory': 1}]
        expected = [{'id': 1, 'name': 'test_name', 'catagory': 'test_catagory'}]

        #When
        actual = get_cats(data, 'join')

        #Then
        self.assertEqual(expected, actual)
        
    def test_should_do_nothing_if_catagory_not_in_fields(self):
        #Given
        data = [{'id': 1, 'name': 'test_name'}]
        
        #When
        actual = get_cats(data, 'join')
        
        #Then
        self.assertEqual(data, actual)


@patch('src.app.input')
@patch('src.app.DbController.insert') 
@patch('src.app.dict_builder')
@patch('src.app.dicts_to_table', lambda x: None)
@patch('src.app.clear', lambda: None)
@patch('src.app.get_cats', lambda *x, **k: [{'id': 1, 'name': 'test_name'}])
class TestAddItemMenu(unittest.TestCase):

    def test_should_call_sql_with_correct_dict(self,mock_builder, mock_insert, mock_input):
        #Given
        expected = {'id': 1, 'name': 'new_name'}
        key = 'test'
        mock_input.return_value = 'n'
        mock_builder.return_value = {'id': 1 , 'name': 'new_name'}
        
        #When
        show_add_item_menu(key)
        
        #Then
        mock_insert.assert_called_with(key, expected)
    
    def test_should_return_on_input_cancelled(self, mock_builder, mock_insert, mock_input):
        #Given
        call_count = 0
        mock_builder.return_value = {}
        key = 'test'
        
        #When
        show_add_item_menu(key)
        
        #Then
        self.assertEqual(mock_insert.call_count, call_count)


@patch('src.app.get_validated_input')
@patch('src.app.input')
@patch('src.app.DbController.update')
@patch('src.app.dict_builder')
@patch('src.app.dicts_to_table', lambda x: None)
@patch('src.app.clear', lambda: None)
@patch('src.app.get_cats', lambda *x, **k: [{'id': 1, 'name': 'test_name'}])
class TestUpdateItemMenu(unittest.TestCase):

    def test_should_call_sql_with_correct_dict(self, mock_builder, mock_update, mock_input, mock_valid_input):
        #Given
        expected = {'id': 1, 'name': 'updated_name'}
        key = 'test'
        mock_input.return_value = 'n'
        mock_valid_input.return_value = 1
        mock_builder.return_value = {'id': 1, 'name': 'updated_name'}
        
        #When
        show_update_item_menu(key)

        #Then
        mock_update.assert_called_with(key, 1,  expected)

    def test_should_return_on_input_cancelled(self, mock_builder, mock_update, mock_input, mock_valid_input):
        #Given
        call_count = 0
        mock_builder.return_value = {}
        key = 'test'

        #When
        show_update_item_menu(key)

        #Then
        self.assertEqual(mock_update.call_count, call_count)


@patch('src.app.input')
@patch('src.app.DbController.insert')
@patch('src.app.dict_builder')
@patch('src.app.dicts_to_table', lambda *a, **k: None)
@patch('src.app.clear', lambda: None)
@patch('src.app.print', lambda a: None)
@patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test_order'}])
class TestAddOrder(unittest.TestCase):

    def test_should_add_with_correct_sql(self, mock_builder, mock_insert, mock_input):
        #Given
        mock_builder.return_value = {'name': 'new_name'}
        mock_input.side_effect = ['y', 'n']
        expected = {'name': 'new_name'}
        
        #When
        show_add_order_menu()
        
        #Then
        mock_insert.assert_called_with('orders', expected)
    
    def test_should_cancel_on_input(self, mock_builder, mock_insert, mock_input):
        #Given
        mock_builder.return_value = {}
        call_count = 0        
        
        #When
        show_add_order_menu()
        
        #Then
        self.assertEqual(mock_insert.call_count, call_count)
        

@patch('src.app.input')
@patch('src.app.get_validated_input')
@patch('src.app.DbController.update')
@patch('src.app.dict_builder')
@patch('src.app.DbController.get_rows_where', lambda *a, **k: [{'id': 1, 'name': 'test_order'}])
@patch('src.app.DbController.get_all_rows', lambda *a, **k: [1])
@patch('src.app.dicts_to_table', lambda *a, **k: None)
@patch('src.app.clear', lambda: None)
@patch('src.app.print', lambda a: None)
@patch('src.app.get_order_data', lambda: [{'id': 1, 'name': 'test_order'}])
class TestUpdateOrderStatus(unittest.TestCase):

    def test_should_update_with_correct_sql(self, mock_builder, mock_insert, mock_valid_input, mock_input):
        #Given
        mock_builder.return_value = {'id': 1, 'status': 1}
        mock_valid_input.side_effect = [1, 1]
        mock_input.return_value = 'n'
        expected = {'id': 1, 'name':'test_order', 'status': 1}
        
        #When
        show_update_status_menu()

        #Then
        mock_insert.assert_called_with('orders', 1, expected)

    def test_should_cancel_on_input(self, mock_builder, mock_insert, mock_valid_input, mock_input):
        #Given
        mock_valid_input.return_value = False
        call_count = 0

        #When
        show_update_status_menu()

        #Then
        self.assertEqual(mock_insert.call_count, call_count)
        
           

if __name__ == '__main__':
    unittest.main()
