import unittest
from app import add_item_to_list, search_items_in_list, update_item_in_list, delete_item_in_list


class TestAddItem(unittest.TestCase):

    def test_should_add_to_list(self):
        # Given
        to_add_to = []
        item_to_add = {'id': '0', 'name': 'pepsi', 'price': '1.25'}
        expected = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]

        # When
        actual = add_item_to_list(item_to_add, to_add_to, 'name')

        # Then
        self.assertEquals(actual, expected)

    def test_should_not_update_list_on_duplicates(self):
        # Given
        to_add_to = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]
        item_to_add = {'id': '0', 'name': 'pepsi', 'price': '1.25'}
        expected = False

        # When
        actual = add_item_to_list(item_to_add, to_add_to, 'name')

        # Then
        self.assertEquals(actual, expected)


class TestUpdateItem(unittest.TestCase):

    def test_should_update_item_with_given_id(self):
        # Given
        current_list = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]
        item_to_add = {'id': '0', 'name': 'coke', 'price': '1.25'}
        expected = [{'id': '0', 'name': 'coke', 'price': '1.25'}]

        # When
        actual = update_item_in_list(item_to_add, current_list)

        # Then
        self.assertEquals(actual, expected)

    def test_should_return_false_if_id_not_found(self):
        # Given
        current_list = [{'id': '0', 'name': 'pepsi', 'price': '1.25'}]
        item_to_add = {'id': '1', 'name': 'coke', 'price': '1.25'}
        expected = False

        # When
        actual = update_item_in_list(item_to_add, current_list)

        # Then
        self.assertEquals(actual, expected)


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
        self.assertEquals(actual, expected)

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
        self.assertEquals(actual, expected)


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
        self.assertEquals(expected, actual)

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
        self.assertEquals(expected, actual)


if __name__ == '__main__':
    unittest.main()
