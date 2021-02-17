import unittest
from unittest.mock import patch

from .DbController import DbController

DbController('','','','')
instance = DbController.instance()

class TestSingleton(unittest.TestCase):

    def test_instance_is_same(self):
        #Given
        x = DbController('1','2','3','4')
        
        #When / Then
        self.assertEqual(instance, x)


@patch('src.DbController.DbController.execute')
class TestGetFieldNames(unittest.TestCase):

    
    def test_should_get_correct_names(self, mock_execute):
        #Given
        mock_execute.return_value = [{'Field': 'id'}, {'Field':'name'}]
        expected = ['name']
        table = 'test'
        
        #When
        actual = instance.get_field_names(table)
        
        #Then
        self.assertEqual(expected, actual)
     
       
    def test_should_return_empty_on_invalid_table(self, mock_execute):
        #Given
        mock_execute.return_value = [{'': 'error'}]
        expected = []
        table = 'invalid'
        #When
        actual = instance.get_field_names(table)
        
        #Then
        self.assertEqual(expected, actual)


@patch('src.DbController.DbController.execute')
class TestGetColumn(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_execute):
        #Given
        column = 'id'
        table = 'test'
        expected = 'SELECT id FROM test'
        
        #When
        instance.get_column(table, column)
        
        #Then
        mock_execute.assert_called_with(expected)
    
                
@patch('src.DbController.DbController.execute')
class TestGetAllRows(unittest.TestCase):

    def test_should_pass_correct_sql_no_order(self, mock_execute):
        #Given
        table = 'test'
        expected = 'SELECT * FROM test '
        get = '*'
        
        #When
        instance.get_all_rows(table, get)
        
        #Then
        mock_execute.assert_called_with(expected)
    
    def test_should_pass_correct_sql_with_order(self, mock_execute):
        #Given
        table = 'test'
        get = '*'
        order = 'ORDER BY 1'
        expected = 'SELECT * FROM test ORDER BY 1'

        #When
        instance.get_all_rows(table,get,order)

        #Then
        mock_execute.assert_called_with(expected)


@patch('src.DbController.DbController.execute')
class TestGetAllRowsWhere(unittest.TestCase):

    def test_should_pass_correct_sql_no_order(self, mock_execute):
        #Given
        table = 'test'
        get = '*'
        where_field = 'test_field'
        where_condition = 'test_condition'
        expected = 'SELECT * FROM test WHERE test_field = "test_condition"'

        #When
        instance.get_rows_where(table, get, where_field, where_condition)

        #Then
        mock_execute.assert_called_with(expected)


@patch('src.DbController.DbController.execute')
class TestInsert(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_execute):
        #Given
        to_insert = {'id': 1, 'name': 'Gary'}
        table = 'test'
        expected = "INSERT INTO test (id, name) VALUES (1, 'Gary')"
        
        #When
        instance.insert(table, to_insert)
        
        #Then
        mock_execute.assert_called_with(expected)
        

@patch('src.DbController.DbController.execute')
class TestDelete(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_execute):
        #Given
        to_delete = 1
        table = 'test'
        expected = "DELETE FROM test WHERE id = 1"

        #When
        instance.delete(table, to_delete)

        #Then
        mock_execute.assert_called_with(expected)


@patch('src.DbController.DbController.execute')
class TestDeleteWhere(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_execute):
        #Given
        table = 'test'
        fields = ['id', 'name']
        conditions = [1, 'Gary']
        expected = "DELETE FROM test WHERE id = 1 AND name = Gary "

        #When
        instance.delete_where(table, fields, conditions)

        #Then
        mock_execute.assert_called_with(expected)


@patch('src.DbController.DbController.execute')
class TestUpdate(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_execute):
        #Given
        table = 'test'
        id = 1
        to_update = {'name': 'Gary'}
        expected = "UPDATE test SET name = 'Gary' WHERE id = 1"
        
        #When
        instance.update(table, id, to_update)
        
        #Then
        mock_execute.assert_called_with(expected)
        

@patch('src.DbController.DbController.execute')
class TestUpdateWhere(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_execute):
        #Given
        table = 'test'
        where_fields = ['id', 'name']
        where_conditions = [1, 'Gary']
        to_update = {'name': 'Gary'}
        expected = "UPDATE test SET name = 'Gary' WHERE id = 1 AND name = Gary "

        #When
        instance.update_where(table, where_fields,where_conditions, to_update)

        #Then
        mock_execute.assert_called_with(expected)


@patch('src.DbController.DbController.execute')
class TestGetJoins(unittest.TestCase):

    def test_should_pass_correct_sql_default_join(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o']
        conditions = ['o.id = t.order_id']
        expected = 'SELECT t.test AS Test, o.test AS Order FROM test t LEFT OUTER JOIN order o ON o.id = t.order_id '
        
        #When
        instance.get_joins(fields, table, targets, conditions)
        
        #Then
        mock_execute.assert_called_with(expected)
        
    def test_should_pass_correct_sql_with_join_type(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o']
        conditions = ['o.id = t.order_id']
        join = 'RIGHT OUTER'
        expected = 'SELECT t.test AS Test, o.test AS Order FROM test t RIGHT OUTER JOIN order o ON o.id = t.order_id '
        
        #When
        instance.get_joins(fields, table, targets, conditions, join)
        
        #Then
        mock_execute.assert_called_with(expected)

    def test_should_pass_correct_sql_with_join_type_and_order(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o']
        conditions = ['o.id = t.order_id']
        join = 'RIGHT OUTER'
        order = 'ORDER BY 1'
        expected = 'SELECT t.test AS Test, o.test AS Order FROM test t RIGHT OUTER JOIN order o ON o.id = t.order_id ORDER BY 1'
        
        #When
        instance.get_joins(fields, table, targets, conditions, join, order)
        
        #Then
        mock_execute.assert_called_with(expected)

    def test_should_raise_error_on_diff_targets_conditions(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o', 'p.product']
        conditions = ['o.id = t.order_id']
        
        #When / Then
        self.assertRaises(AssertionError, lambda: instance.get_joins(
            fields, table, targets, conditions))
        
@patch('src.DbController.DbController.execute')
class TestGetJoinsWhere(unittest.TestCase):

    def test_should_pass_correct_sql_default_join(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o']
        where = 'id = 1'
        conditions = ['o.id = t.order_id']
        expected = 'SELECT t.test AS Test, o.test AS Order FROM test t LEFT OUTER JOIN order o ON o.id = t.order_id WHERE id = 1 '
        
        #When
        instance.get_joins_where(fields, table, targets, conditions, where)
        
        #Then
        mock_execute.assert_called_with(expected)
        
    def test_should_pass_correct_sql_with_join_type(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o']
        conditions = ['o.id = t.order_id']
        where = 'id = 1'
        join = 'RIGHT OUTER'
        expected = 'SELECT t.test AS Test, o.test AS Order FROM test t RIGHT OUTER JOIN order o ON o.id = t.order_id WHERE id = 1 '
        
        #When
        instance.get_joins_where(fields, table, targets, conditions,where, join)
        
        #Then
        mock_execute.assert_called_with(expected)

    def test_should_pass_correct_sql_with_join_type_and_order(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o']
        conditions = ['o.id = t.order_id']
        where = 'id = 1'
        join = 'RIGHT OUTER'
        order = 'ORDER BY 1'
        expected = 'SELECT t.test AS Test, o.test AS Order FROM test t RIGHT OUTER JOIN order o ON o.id = t.order_id WHERE id = 1 ORDER BY 1'
        
        #When
        instance.get_joins_where(fields, table, targets, conditions, where, join, order)
        
        #Then
        mock_execute.assert_called_with(expected)

    def test_should_raise_error_on_diff_targets_conditions(self, mock_execute):
        #Given
        fields = ['t.test AS Test','o.test AS Order']
        table = 'test t'
        targets = ['order o', 'p.product']
        conditions = ['o.id = t.order_id']
        where = 'id = 1'
        
        #When / Then
        self.assertRaises(AssertionError, lambda: instance.get_joins_where(
            fields, table, targets, conditions, where))
        
        
@patch('src.DbController.DbController.execute')
@patch('src.DbController.DbController.get_field_names')
class TestSearchTable(unittest.TestCase):

    def test_should_pass_correct_sql(self, mock_fields, mock_execute):
        #Given
        mock_fields.return_value = ['name', 'address']
        table = 'test'
        term = 'search'
        expected = f'SELECT * FROM test WHERE name LIKE "%search%" OR address LIKE "%search%" '
        
        #When
        instance.search_table(table, term)
        
        #Then
        mock_execute.assert_called_with(expected)
        
    def test_should_pass_correct_sql_one_field(self, mock_fields, mock_execute):
        #Given
        mock_fields.return_value = ['name']
        table = 'test'
        term = 'search'
        expected = f'SELECT * FROM test WHERE name LIKE "%search%" '
        
        #When
        instance.search_table(table, term)
        
        #Then
        mock_execute.assert_called_with(expected)
        

@patch('src.DbController.DbController.execute')
class TestSearchJoinedTable(unittest.TestCase):

    def test_should_pass_correct_sql_no_alias(self, mock_execute):
        #Given
        table = 'test t'
        term = 'search'
        fields = ['o.name', 'o.address']
        targets = ['order o']
        conditions = ['o.id = t.id']
        expected = f'SELECT o.name, o.address FROM test t LEFT OUTER JOIN order o ON o.id = t.id WHERE o.name LIKE "%search%" OR o.address LIKE "%search%" '
        
        #When
        instance.search_joined_table(table, term, fields, targets, conditions)
        
        #Then
        mock_execute.assert_called_with(expected)
        
    def test_should_pass_correct_sql_with_alias(self, mock_execute):
        #Given
        table = 'test t'
        term = 'search'
        fields = ['o.name AS Name', 'o.address AS Address']
        targets = ['order o']
        conditions = ['o.id = t.id']
        expected = f'SELECT o.name AS Name, o.address AS Address FROM test t LEFT OUTER JOIN order o ON o.id = t.id WHERE o.name  LIKE "%search%" OR o.address  LIKE "%search%" '
        
        #When
        instance.search_joined_table(table, term, fields, targets, conditions)
        
        #Then
        mock_execute.assert_called_with(expected)

        
if __name__ == '__main__':
    unittest.main()
