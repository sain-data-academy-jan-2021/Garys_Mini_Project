import unittest
from unittest import mock
from unittest.mock import patch


from .app import (
    add_item_to_list, get_dict_by_key, get_value_from_key, load_external_data, patch_value_from_key,
    search_items_in_list, sort_list_by_value, sort_orders_by_status, summerise_list,
    update_item_in_list,
    delete_item_in_list,
    get_external_data
)


class TestAddItem(unittest.TestCase):

    def test_should_add_to_list(self):
        # Given
        to_add_to = []
        item_to_add = {'id': '0', 'name': 'pepsi', 'price': '1.25'}
        expected = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]

        # When
        actual = add_item_to_list(item_to_add, to_add_to, 'name')

        # Then
        self.assertEqual(actual, expected)

    def test_should_not_update_list_on_duplicates(self):
        # Given
        to_add_to = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]
        item_to_add = {'id': '0', 'name': 'pepsi', 'price': '1.25'}
        expected = False

        # When
        actual = add_item_to_list(item_to_add, to_add_to, 'name')

        # Then
        self.assertEqual(actual, expected)


class TestUpdateItem(unittest.TestCase):

    def test_should_update_item_with_given_id(self):
        # Given
        current_list = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]
        item_to_add = {'id': '0', 'name': 'coke', 'price': '1.25'}
        expected = [{'id': '0', 'name': 'coke', 'price': '1.25'}]

        # When
        actual = update_item_in_list(item_to_add, current_list)

        # Then
        self.assertEqual(actual, expected)

    def test_should_return_false_if_id_not_found(self):
        # Given
        current_list = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]
        item_to_add = {'id': '1', 'name': 'coke', 'price': '1.25'}
        expected = False

        # When
        actual = update_item_in_list(item_to_add, current_list)

        # Then
        self.assertEqual(actual, expected)


class TestDeleteItem(unittest.TestCase):

    def test_should_delete_item_if_in_list(self):
        # Given
        current_list = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.25'},
            {'id': '2', 'name': 'water', 'price': '1.25'}, ]
        delete_id = '1'
        expected = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '2', 'name': 'water', 'price': '1.25'}, ]

        # When
        actual = delete_item_in_list(delete_id, current_list)

        # Then
        self.assertEqual(actual, expected)

    def test_should_return_false_item_if_not_in_list(self):
        # Given
        current_list = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.25'},
            {'id': '2', 'name': 'water', 'price': '1.25'}, ]
        delete_id = '10'
        expected = False

        # When
        actual = delete_item_in_list(delete_id, current_list)

        # Then
        self.assertEqual(actual, expected)


class TestSearchItem(unittest.TestCase):

    def test_should_return_result_on_matched_term(self):
        # Given
        list_to_search = [
            {'id': '0', 'name': 'pepsi', 'price': '1.99'},
            {'id': '1', 'name': 'coke', 'price': '1.99'}
        ]
        search_term = 'coke'
        expected = [{'id': '1', 'name': 'coke', 'price': '1.99'}]

        # When
        actual = search_items_in_list(search_term, list_to_search)

        # Then
        self.assertEqual(expected, actual)

    def test_should_return_empty_list_on_none_matched_term(self):
        # Given
        list_to_search = [
            {'id': '0', 'name': 'pepsi', 'price': '1.99'},
            {'id': '1', 'name': 'coke', 'price': '1.99'}
        ]
        search_term = 'water'
        expected = []

        # When
        actual = search_items_in_list(search_term, list_to_search)

        # Then
        self.assertEqual(expected, actual)


@patch('src.app.external_data', {"test_dict": {"name": "test", "data": [], "location": "test.csv", "type": "csv"}})
class TestGetExternalData(unittest.TestCase):

    def test_should_return_correct_data(self):
        # Given
        key = 'test_dict'
        attr = 'location'
        expected = 'test.csv'

        # When
        actual = get_external_data(key, attr)

        # Then
        self.assertEqual(expected, actual)

    def test_should_raise_key_error_on_invalid_key(self):
        # Given
        key = 'invalid_dict'
        attr = 'location'

        # When / Then
        self.assertRaises(KeyError, lambda: get_external_data(key, attr))


class TestSummeriseList(unittest.TestCase):

    def test_should_return_correct_summary(self):
        # Given
        lst = ['apple', 'banana', 'melon', 'apple']
        expected = ['1x banana', '1x melon', '2x apple']

        # When
        actual = summerise_list(lst)

        # Then
        self.assertEqual(expected, actual)


class TestGetDictByKey(unittest.TestCase):

    def test_should_return_correct_dict(self):
        # Given
        dtn = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.25'},
            {'id': '2', 'name': 'water', 'price': '1.25'}
        ]
        expected = {'id': '1', 'name': 'coke', 'price': '1.25'}

        # When
        actual = get_dict_by_key(source=dtn, where='name', equals='coke')

        # Then
        self.assertEqual(expected, actual)

    def test_should_return_false_if_not_found(self):
        # Given
        dtn = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.25'},
            {'id': '2', 'name': 'water', 'price': '1.25'}
        ]
        expected = False

        # When
        actual = get_dict_by_key(source=dtn, where='name', equals='vodka')

        # Then
        self.assertEqual(expected, actual)

    def test_should_raise_key_error_on_invalid_where(self):
        # Given
        dtn = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]

        #When / Then
        self.assertRaises(KeyError, lambda: get_dict_by_key(
            source=dtn, where='invalid_key', equals='vodka'))


class TestGetValueFromKey(unittest.TestCase):

    def test_should_return_correct_value(self):
        # Given
        dtn = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.20'}
        ]
        expected = '1.20'

        # When
        actual = get_value_from_key(
            source=dtn, get='price', where='id', equals='1')

        # Then
        self.assertEqual(expected, actual)

    def test_should_return_false_if_not_found(self):
        # Given
        dtn = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.20'}
        ]
        expected = False

        # When
        actual = get_value_from_key(
            source=dtn, get='id', where='name', equals='water')

        # Then
        self.assertEqual(expected, actual)

    def test_should_raise_key_error_on_invalid_where(self):
        # Given
        dtn = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]

        #When / Then
        self.assertRaises(KeyError, lambda: get_value_from_key(
            source=dtn, get='id', where='invalid', equals='vodka'))

    def test_should_raise_key_error_on_invalid_get(self):
        # Given
        dtn = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]

        #When / Then
        self.assertRaises(KeyError, lambda: get_value_from_key(
            source=dtn, get='invalid_key', where='name', equals='pepsi'))


class TestPatchValueFromKey(unittest.TestCase):

    def test_should_update_correct_key(self):
        # Given
        dtn = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.20'}
        ]
        expected = {'id': '0', 'name': 'pepsi', 'price': '1.50'}

        # When
        actual = patch_value_from_key(
            source=dtn, patch='price', to='1.50', where='id', equals='0')

        # Then
        self.assertEqual(expected, actual)

    def test_should_return_false_if_key_not_found(self):
        # Given
        dtn = [
            {'id': '0', 'name': 'pepsi', 'price': '1.25'},
            {'id': '1', 'name': 'coke', 'price': '1.20'}
        ]
        expected = False

        # When
        actual = patch_value_from_key(
            source=dtn, patch='invalid_key', to='1.50', where='id', equals='0')

        # Then
        self.assertEqual(expected, actual)


@patch('src.app.get_external_data', lambda key: [{'status': 'second'}, {'status': 'first'}])
@patch('src.app.order_status', {'first': None, 'second': None})
class TestSortOrderByStatus(unittest.TestCase):

    def test_should_sort_by_dict_keys(self):
        # Given
        expected = [{'status': 'first'}, {'status': 'second'}]

        # When
        actual = sort_orders_by_status()

        # Then
        self.assertEqual(expected, actual)


@patch('src.app.get_external_data', lambda key: [{'id': 1, 'name': 'Bob'}, {'id': 3, 'name': 'Charlie'}, {'id': 2, 'name': 'Alice'}])
class TestSortListByValue(unittest.TestCase):

    def test_should_sort_by_str_key(self):
        # Given
        expected = [{'id': 2, 'name': 'Alice'}, {
            'id': 1, 'name': 'Bob'}, {'id': 3, 'name': 'Charlie'}]

        # When
        actual = sort_list_by_value(key='name')

        # Then
        self.assertEqual(expected, actual)

    def test_should_sort_by_int_key(self):
        # Given
        expected = [{'id': 1, 'name': 'Bob'}, {
            'id': 2, 'name': 'Alice'}, {'id': 3, 'name': 'Charlie'}]

        # When
        actual = sort_list_by_value(key='id')

        # Then
        self.assertEqual(expected, actual)


class TestLoadExternalData(unittest.TestCase):

    def test_should_load_txt_data_to_list(self):
        # Given
        config = {"test":
                  {"name": "test",
                   "data": [],
                   "location": "./data/tests/test_txt_data.txt"}
                  }
        expected = ['Some', 'Test', 'Data', 'In', 'A', 'File']

        # When
        load_external_data(config)
        actual = config['test']['data']

        # Then
        self.assertEqual(expected, actual)

    def test_should_load_csv_data_to_dict(self):
        # Given
        config = {"test":
                  {"name": "test",
                   "data": [],
                   "location": "./data/tests/test_csv_data.csv",
                   'type': 'csv'}
                  }
        expected = [
            {'id': 1, 'name': 'alice'},
            {'id': 2, 'name': 'bob'}
        ]

        # When
        load_external_data(config)
        actual = config['test']['data']

        # Then
        self.assertEqual(expected, actual)

    def test_should_load_json_data_to_dict(self):
        # Given
        config = {"test":
                  {"name": "test",
                   "data": [],
                   "location": "./data/tests/test_json_data.json",
                   'type': 'json'}
                  }
        expected = [
            {'id': 1, 'name': 'alice'},
            {'id': 2, 'name': 'bob'}
        ]

        # When
        load_external_data(config)
        actual = config['test']['data']

        # Then
        self.assertEqual(expected, actual)

    @patch('src.file_system.log')
    def test_should_log_error_on_invalid_path(self, mock_log):
        # Given
        config = {"test":
                  {"name": "test",
                   "data": [],
                   "location": "./data/tests/invalid.txt"}
                  }

        # When
        load_external_data(config)
        # Then
        mock_log.assert_called_with(
            'error', "Failed to load data - [Errno 2] No such file or directory: '/Users/gary.spittel/Desktop/Bootcamp/Mini_Project/data/tests/invalid.txt'")


if __name__ == '__main__':
    unittest.main()
