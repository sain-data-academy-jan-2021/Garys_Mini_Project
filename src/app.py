from typing import Any, Union
from src.cli import clear, dicts_to_table, fmt_string, get_validated_input, list_to_table, print_palette, print_table, validated_input, order_status
from src.file_system import load_csv_to_dict, load_json, load_list, save_json, save_list, log, save_dict_to_csv

# region := Utils
def sort_orders_by_status():
    orders = get_external_data('orders')
    for i in range(len(orders)):
        for j in range(len(orders) - 1):
            status_index1 = list(order_status.keys()).index(
                orders[j]['status'])
            status_index2 = list(order_status.keys()).index(
                orders[j + 1]['status'])
            if status_index1 > status_index2:
                orders[j], orders[j + 1] = orders[j + 1], orders[j]


def not_implemented():
    input(fmt_string('TODO: Feature Not Yet Implemented', fg='White', bg='Red'))


def load_external_data(data: dict[str, Any]) -> None:
    for data_source in data.values():
        if 'location' in data_source:
            if 'type' not in data_source:
                load_list(data_source['location'], data_source['data'])
            else:
                if data_source['type'] == 'json':
                    data_source['data'] = load_json(data_source['location'])

                elif data_source['type'] == 'csv':
                    data_source['data'] = load_csv_to_dict(
                        data_source['location'])


def save_external_data(data: dict[str, Any]) -> None:
    for data_source in data.values():
        if 'location' in data_source:
            if 'type' not in data_source:
                save_list(data_source['location'], data_source['data'])

            else:
                if data_source['type'] == 'json':
                    save_json(data_source['location'], data_source['data'])

                elif data_source['type'] == 'csv':
                    save_dict_to_csv(
                        data_source['location'], data_source['data'])


def get_external_data(key: str, attr: str = 'data') -> Any:
    global external_data
    return external_data[key][attr]
# endregion := Utils


# region := Data
def add_item_to_list(item: dict[Any, Any], data: list[dict[Any, Any]], unique_key: str) -> Union[list[dict[Any, Any]], bool]:
    for dtn in data:
        if item[unique_key] == dtn[unique_key]:
            return False

    data.append(item)
    return data


def update_item_in_list(item: dict[Any, Any], data: list[dict[Any, Any]]) -> Union[list[dict[Any, Any]], bool]:
    for i, dtn in enumerate(data):
        if dtn['id'] == item['id']:
            data[i] = item
            return data

    return False


def delete_item_in_list(id: str, data: list[dict[Any, Any]]) -> Union[list[dict[Any, Any]], bool]:
    for i in range(len(data) - 1, 0, -1):
        if data[i]['id'] == id:
            del data[i]
            return data

    return False


def search_items_in_list(term: str, data: list[dict[Any, Any]]) -> list[dict[Any, Any]]:
    results = []

    for dtn in data:
        for value in dtn.values():
            if term in str(value):
                results.append(dtn)

    return results
# endregion := Data


# region := View
def show_menu(menu_name: str) -> None:
    # Set the global menu_state to the selected menu to allow us to backtrack when returning
    global menu_state
    menu_state = menu_name
    save_external_data(external_data)
    log('debug', f'Menu {menu_name} loaded')

    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.', fg='Blue'))

    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    print_table(menu['title'], menu['items'])

    if (menu_option := validated_input('Please Select An Option.\n', int, fg='Green', min_value=0, max_value=len(menu['handlers'])-1))[0] == 0:
        log('debug', menu_option[1])
        input(menu_option[1])
        return

    # Call the function associated with the selected menu item
    menu['handlers'][menu_option[1]]()


def print_data_view(key: str) -> None:
    data = get_external_data(key)

    clear()
    dicts_to_table(data)
    input(fmt_string('Press ENTER To Continue', fg='Green'))


def show_add_item_menu(key: str) -> None:
    data = get_external_data(key)
    items = data[0].items()
    current_names = [item['name'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        new_dict = {}
        id = int(data[-1]['id']) + 1
        new_dict['id'] = id

        for key, value in items:
            if key != 'id' and key != 'items':
                if key == 'name':
                    value = get_validated_input(
                        f'Please Enter {key.title()}: ', type(value), fg='Blue', min_length=1, unique=current_names, cancel_on='0')
                else:
                    value = get_validated_input(
                        f'Please Enter {key.title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')

                if not value:
                    return

                new_dict[key] = value

        successful = add_item_to_list(new_dict, data, 'name')

        clear()
        dicts_to_table(data)
        sort_orders_by_status()

        if successful:
            if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
                is_looping = False


def show_update_item_menu(key: str) -> None:
    data = get_external_data(key)
    items = data[0].items()
    current_ids = [item['id'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)

        new_dict = {}
        id = get_validated_input('Please Enter An ID To Edit: ', int,
                                 fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')

        if not id:
            return

        new_dict['id'] = id

        for key, value in items:
            if key != 'id' and key != 'items':
                value = get_validated_input(
                    f'Please Enter New {key.title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')

                if not value:
                    return

                new_dict[key] = value

        successful = update_item_in_list(new_dict, data)

        clear()
        sort_orders_by_status()
        dicts_to_table(data)

        if successful:
            if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
                is_looping = False


def show_delete_item_menu(key: str) -> None:
    data = get_external_data(key)
    current_ids = [item['id'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        item_id = get_validated_input(
            f'Please Enter An ID To Delete: ', int, fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')

        if not item_id:
            return

        successful = delete_item_in_list(item_id, data)

        clear()
        dicts_to_table(data)

        if successful:
            if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
                is_looping = False


def show_search_menu(key: str) -> None:
    data = get_external_data(key)
    clear()
    term = get_validated_input(
        'Please Enter A Search Term: ', str, fg='Blue', cancel_on='0')

    if not term:
        return

    results = search_items_in_list(term, data)

    if len(results) == 0:
        input(fmt_string(
            f'\nNo Results Found For {term}!', fg='White', bg='Red'))
        return

    print(f'\nResults Found: {len(results)}\n')
    dicts_to_table(results)

    action = get_validated_input(fmt_string('What Would You Like To Do? (a)dd, (u)pdate, or (d)elete: ',
                                            fg='Green'), str, is_present=['a', 'u', 'd'], cancel_on='0')

    if not action:
        return

    not_implemented()


def show_add_order_menu() -> None:
    data = get_external_data('orders')
    items = data[0].items()

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        new_dict = {}
        id = int(data[-1]['id']) + 1
        new_dict['id'] = id

        for key, value in items:
            if key != 'id':
                if key == 'courier':
                    new_value = -1
                    # courier_ids = [str(courier['id'])
                    #                for courier in get_external_data('couriers')]
                    # clear()
                    # dicts_to_table(get_external_data('couriers'))
                    
                    # new_value = get_validated_input(
                    #     f'Please Select {key.title()}: ', type(value), fg='Blue', is_present=courier_ids, cancel_on='0')

                elif key == 'status':
                    new_value = 'pending'
                    # status_list = list(order_status.keys())
                    
                    # clear()
                    # list_to_table(status_list, 'Status List', enumerate=True)
                    
                    # new_value = status_list[get_validated_input(
                    #     f'Please Select {key.title()}: ', int, fg='Blue', 
                    #     min_length=0, max_value=len(status_list),min_value=1, cancel_on='0') - 1]
                
                elif key == 'items':
                    new_value = []
                
                else:
                    new_value = get_validated_input(
                        f'Please Enter {key.title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')
                    

                if new_value == False:
                    return

                new_dict[key] = new_value
            
            # Random crap to show order as it's being built    
            clear()
            dicts_to_table(data) 
            print('Creating New Order...\n')      
            for k, v in new_dict.items():
                print(fmt_string(k.title(),fg='Cyan'),': ',fmt_string(str(v).title(), fg='White'))
            print()
            
        successful = add_item_to_list(new_dict, data, 'name')

        clear()
        sort_orders_by_status()
        dicts_to_table(data)
    
        if successful:
            if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
                is_looping = False
# endregion := View


#region := TODO
def show_order_detail_menu(order_id: int) -> None:
    not_implemented()
   
    
def show_update_status_menu() -> None:
    not_implemented()
    

def show_update_order_menu() -> None:
    not_implemented()
    

def show_delete_order_menu() -> None:
    not_implemented()
    
#endregion := TODO


#region := Setup
external_data = load_json('./data/config.json')
load_external_data(external_data)

menus = {
    'main_menu': {
        'title': 'Main Menu',
        'items': ['[0] Exit',
                  '[1] Product Maintainance',
                  '[2] Courier Maintainance',
                  '[3] Order Maintainance',
                  'Separator',
                  '[4] System Maintainance'
                  ],
        'handlers': [exit,
                     lambda: show_menu('product_menu'),
                     lambda: show_menu('courier_menu'),
                     lambda: show_menu('orders'),
                     lambda: show_menu('system_maintainance_menu'),
                     ]
    },
    'product_menu': {
        'title': 'Product Maintainance',
        'items': ['[0] Return To Main Menu',
                  '[1] Show All Products',
                  '[2] Create New Product',
                  '[3] Update Product',
                  '[4] Delete Product',
                  '[5] Search'],
        'handlers': [lambda: show_menu('main_menu'),
                     lambda: print_data_view('products'),
                     lambda: show_add_item_menu('products'),
                     lambda: show_update_item_menu('products'),
                     lambda: show_delete_item_menu('products'),
                     lambda: show_search_menu('products')
                     ]
    },
    'courier_menu': {
        'title': 'Courier Maintainance',
        'items': ['[0] Return To Main Menu',
                  '[1] Show All Couriers',
                  '[2] Create New Courier',
                  '[3] Update Courier',
                  '[4] Delete Courier',
                  '[5] Search'],
        'handlers': [lambda: show_menu('main_menu'),
                     lambda: print_data_view('couriers'),
                     lambda: show_add_item_menu('couriers'),
                     lambda: show_update_item_menu('couriers'),
                     lambda: show_delete_item_menu('couriers'),
                     lambda: show_search_menu('couriers')
                     ]
    },
    'orders': {
        'title': 'Manage Orders',
        'items': [
            '[0] Return To Main Menu',
            '[1] View Current Orders',
            '[2] Create New Order',
            '[3] Update Status',
            '[4] Update Order',
            '[5] Delete Order'
        ],
        'handlers': [
            lambda: show_menu('main_menu'),
            lambda: print_data_view('orders'),
            lambda: show_add_order_menu(),
            not_implemented,
            not_implemented,
            not_implemented,
            not_implemented
        ]
    },
    'system_maintainance_menu': {
        'title': 'System Maintainance',
        'items': [
            '[0] Return To Main Menu',
            '[1] Update Menu Grouping'
        ],
        'handlers': [
            lambda: show_menu('main_menu'),
            not_implemented
        ]
    }
}

# Start Loop
menu_state = 'main_menu'

if __name__ == '__main__':
    while menu_state:
        show_menu(menu_state)
        save_external_data(external_data)

#endregion :=Setup