from typing import Any, Hashable, Union
import os
from dotenv import load_dotenv

from .DbController import DbController
from .cli import clear, dicts_to_table, fmt_string, get_validated_input, list_to_table, print_palette, print_table, validated_input, order_status
from .file_system import load_csv_to_dict, load_json, load_list, save_json, save_list, log, save_dict_to_csv
load_dotenv()


# region := Utils
def sort_orders_by_status():
    orders = get_external_data('orders')
    for i in range(len(orders)):
        for j in range(len(orders) - 1):
            if orders[j]['status'] > orders[j + 1]['status']:
                orders[j], orders[j + 1] = orders[j + 1], orders[j]
    
    return orders


def sort_list_by_value(lst: str = 'orders', key: str = 'id'):
    if key == 'status':
        return sort_orders_by_status()

    orders = get_external_data(lst)
    for i in range(len(orders)):
        for j in range(len(orders) - 1):
            if orders[j][key] > orders[j + 1][key]:
                orders[j], orders[j + 1] = orders[j + 1], orders[j]
    return orders


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
        elif data_source['type'] == 'db':
            host = os.environ.get("mysql_host")
            user = os.environ.get("mysql_user")
            password = os.environ.get("mysql_pass")
            database = os.environ.get("mysql_db")
            
            data_source['connector'] = DbController(
                host, user, password, database)  # type:ignore  
            print(data_source['connector'])
            data_source['data'] = data_source['connector'].get_all_rows(
                    data_source['name'])
            try:
                pass
            except:
                pass


def refresh_connections():
    global external_data
    for data_source in external_data:
        source = external_data[data_source]
        if source['type'] == 'db':
            source['data'] = source['connector'].get_all_rows(source['name'])


def close_connections():
    for data_source in external_data:
        if data_source['type'] == 'db':
            data_source['connector'].close()


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


def summerise_list(lst: list) -> list[str]:
    res = []
    for i in range(len(lst)):
        count = 0
        for j in range(len(lst)):
            if lst[i] == lst[j]:
                count += 1
        res.append(f"{count}x {lst[i]}")

    res = list(set(res))
    res.sort()
    return res


def get_dict_by_key(*, source: list[Any], where: Hashable, equals: Any) -> Any:
    for dtn in source:
        if dtn[where] == equals:
            return dtn
    return False


def get_value_from_key(*, source: list[Any], get: Hashable, where: Hashable, equals: Any) -> Any:
    for dtn in source:
        if dtn[where] == equals:
            return dtn[get]
    return False


def patch_value_from_key(*, source, patch, to, where, equals) -> Any:
    for dtn in source:
        if dtn[where] == equals and patch in dtn.keys():
            dtn[patch] = to
            return dtn

    return False
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


def delete_item_in_list(id: Union[int, str], data: list[dict[Any, Any]]) -> Union[list[dict[Any, Any]], bool]:
    for i in range(len(data) - 1, -1, -1):
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
    save_external_data(external_data) #type: ignore
    log('debug', f'Menu {menu_name} loaded')
    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.', fg='Blue'))
    sort_orders_by_status()

    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    print_table(menu['title'], menu['items'])

    if (menu_option := validated_input('Please Select An Option.\n', int, fg='Green', min_value=0, max_value=len(menu['handlers'])-1))[0] == 0:
        log('debug', menu_option[1])
        input(menu_option[1])
        return

    # Call the function associated with the selected menu item
    menu['handlers'][menu_option[1]]()


def print_data_view(key: str) -> None: # type: ignore
    data = get_external_data(key)
    # Get a list of the current IDs to ensure the user selects one that actually exists -> passed to is_present
    current_ids = [-1] + [item['id'] for item in data]
    if key == 'orders':
        is_looping = True
        
        cntr = get_external_data(key, 'connector') #type: DbController
        data = cntr.get_joins(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS Courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status']
        ) 
        
        while is_looping:
            clear()
            dicts_to_table(data, paginate=True)  # type: ignore
            index = get_validated_input(
                'Please Select An Id To View (-1 To Sort): ', int, fg='Blue', cancel_on='0', is_present=current_ids)
            if index == False:
                is_looping = False
                continue

            if index == -1:
                clear()
                dicts_to_table(data, paginate=True)  # type: ignore
                sort_on_keys = list(data[0].keys())  # type: ignore
                list_to_table(sort_on_keys, 'Available Sorts', enumerate=True)
                sort_key = get_validated_input(
                    'How Would You Like To Sort By [id]? ', int, fg='Blue', min_value=1, max_value=len(sort_on_keys), cancel_on=0)
                data = cntr.get_joins(
                    fields=['o.id', 'o.name', 'o.address',
                            'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
                    source='orders o',
                    targets=['couriers courier', 'status s'],
                    conditions=['courier.id = o.courier', 's.id = o.status'],
                    order=f'ORDER BY {sort_key}'
                )
                continue
            
            for order in data:
                if order['id'] == index: #type: ignore
                    clear()
                    show_order_detail_menu(order)
    else:
        is_looping = True
        while is_looping:
            clear()
            dicts_to_table(data, paginate=True)
            index = get_validated_input(
                'Please Select 1 To Sort: ', int, fg='Blue', cancel_on='0', is_present=[1])

            if index == False:
                is_looping = False
                continue

            if index == 1:
                clear()
                sort_on_keys = [key for key in data[0]]
                list_to_table(sort_on_keys, 'Available Sorts', enumerate=True)
                sort_key = get_validated_input(
                    'How Would You Like To Sort By [id]? ', int, fg='Blue', min_value=1, max_value=len(sort_on_keys), cancel_on=0)
                sort_list_by_value(key, sort_on_keys[sort_key - 1])
                continue


def show_add_item_menu(get_key: str) -> None:
    data = get_external_data(get_key)
    # Use the first element in the list to establish the key structure of the data
    items = data[0].items()
    # Get a list of current names to ensure that no duplicates are passed -> passed to unique
    current_names = [item['name'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        new_dict = {}
        id = max([item['id'] for item in data]) + 1
        new_dict['id'] = id

        for key, value in items:
            if key != 'id' and key != 'items':
                if key == 'name':
                    value = get_validated_input(
                        f'Please Enter {key.replace("_"," ").title()}: ', type(value), fg='Blue', min_length=1, unique=current_names, cancel_on='0')
                else:
                    value = get_validated_input(
                        f'Please Enter {key.replace("_"," ").title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')

                if not value:
                    return

                new_dict[key] = value

        successful = add_item_to_list(new_dict, data, 'name')
        if get_external_data(get_key, 'type') == 'db':
            get_external_data(get_key, 'connector').insert(get_key, new_dict)
            refresh_connections()

        clear()
        sort_orders_by_status()
        dicts_to_table(data)

        if successful:
            if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
                is_looping = False


def show_update_item_menu(get_key: str) -> None:
    data = get_external_data(get_key)
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
        if get_external_data(get_key, 'type') == 'db':
            get_external_data(get_key, 'connector').update(
                get_key, id, new_dict)
            refresh_connections()
        clear()
        sort_orders_by_status()
        dicts_to_table(data)

        if successful:
            if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
                is_looping = False


def show_delete_item_menu(get_key: str) -> None:
    data = get_external_data(get_key)
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
        if get_external_data(get_key, 'type') == 'db':
            get_external_data(get_key, 'connector').delete(get_key, item_id)
            refresh_connections()

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
    display_data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status']
    )
    
    items = display_data[0].items()

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(display_data)
        new_dict = {}
        for key, value in items:
            key = key.lower()
            if key != 'id':
                if key == 'courier' or key == 'status':
                    continue
                    
                elif key == 'items':
                    new_value = select_order_items()

                else:
                    new_value = get_validated_input(
                        f'Please Enter {key.title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')

                if new_value == False:
                    return

                new_dict[key] = new_value

            clear()
            dicts_to_table(display_data)
            print(fmt_string('\nCreating New Order...', fg='Cyan'))
            dicts_to_table([new_dict], headers=list(display_data[0].keys())[1:-2])
        
        clear()
        dicts_to_table(display_data)
        print(fmt_string('\nOrder Complete!', fg='Green'))
        dicts_to_table([new_dict], headers=list(display_data[0].keys())[1:-2])
        
        if input(fmt_string('Does This Look Correct?[y/n]\n', fg='Green')).lower() == 'n':
            continue
        
        DbController.insert('orders',new_dict)    
        
        clear()
        sort_orders_by_status()
        
        display_data = DbController.get_joins(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status']
        )
        
        dicts_to_table(display_data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_order_detail_menu(order) -> None:
    con = get_external_data('orders','connector') #type: DbController
    for k,v in order.items():
        if k == 'status':
            col = con.get_all_rows_where('status', 'code', v)[0]['style'] 
            print(fmt_string(f'{str(k).title()}: ',fg='Blue'), fmt_string(f'{str(v).title()}\n', fg=col))
        else:        
            print(fmt_string(f'{str(k).title()}: ',fg='Blue'), f'{str(v).title()}\n')
       
    
    items = con.get_all_rows_where('basket', 'order_id', order['id'])
    items = con.get_joins_where(
        fields = ['b.quantity AS "#x"','p.name', 'b.quantity * p.price AS "Sub Total"'],
        source = 'orders o',
        targets=['basket b', 'products p'],
        conditions=[f'b.order_id = {order["id"]}','b.item = p.id'],
        where= f'o.id = {order["id"]}',
        type='INNER'
    )

    if len(items) > 0:  # type: ignore
        dicts_to_table(items)  # type: ignore
    else:
        print(fmt_string('Order: ', fg='Blue'), fmt_string('Basket Is Empty', fg='Red'))

    input(fmt_string('\nPress ENTER To Continue', fg='Green'))


def show_update_status_menu() -> None:
    data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status']
    )
    
    status_list = DbController.get_all_rows('status')
    
    current_ids = [order['id'] for order in data]
    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        index = get_validated_input(
            'Please Select An Id To Update: ', int, fg='Blue', cancel_on='0', is_present=current_ids)

        if not index:
            is_looping = False
            continue

        status_list = DbController.get_all_rows('status')
        current_row = DbController.get_all_rows_where('orders', 'id', index)[0]
        
        clear()
        dicts_to_table(data)
        print(fmt_string(f'\nUpdating Order {index}...', fg='Cyan'))
        
        dicts_to_table(status_list)
        status_index = get_validated_input(
            f'Please Select A New Status: ', int, fg='Blue',
            min_length=0, max_value=len(status_list), min_value=1, cancel_on='0')

        if not status_index:
            continue
        
        current_row['status'] = status_index
        
        DbController.update('orders', index, current_row )

        clear()
        sort_orders_by_status()
        dicts_to_table(data)

        if input(fmt_string('Status SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False
            continue


def show_update_order_menu() -> None:
    data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status']
    )

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

        clear()
        
        order = DbController.get_joins_where(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status'],
            where=f'o.id = {id}'
        )
        
        dicts_to_table(order)


        for key, value in items:
            if key != 'id':
                if key == 'items':
                    pass

                elif key == 'status':
                    status_list = DbController.get_all_rows('status')
                    status_ids = [status['id'] for status in status_list]

                    clear()
                    dicts_to_table(order)
                    dicts_to_table(status_list)

                    status_index = get_validated_input(
                        f'Please Select {key.title()}: ', int, fg='Blue',
                        is_present=status_ids, min_value=1, cancel_on='0', cancel_text='SKIP')

                    value = status_index

                    if not status_index:
                        value = order[0]['status']

                elif key == 'courier':
                    courier_list = DbController.get_all_rows('couriers')
                    courier_ids= [courier['id'] for courier in courier_list]

                    clear()
                    dicts_to_table(order)
                    dicts_to_table(courier_list)
                    value = get_validated_input(
                        f'Please Select {key.title()}: ', int, fg='Blue', is_present=courier_ids, cancel_on='0', cancel_text='SKIP')

                    if not value:
                        value = order[0]['courier']

                else:
                    value = get_validated_input(
                        f'Please Enter New {key.title()}: ', type(value), fg='Blue', min_length=0, cancel_on='', cancel_text='SKIP')

                    if not value:
                        value = order[0][key]

                new_dict[key] = value

        DbController.update('orders', id, new_dict)

        clear()
        sort_orders_by_status()
        dicts_to_table(data)


        if input(fmt_string('Item SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_delete_order_menu() -> None:
    data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status']
    )
    
    current_ids = [item['id'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)

        id = get_validated_input('Please Enter An ID To Delete: ', int,
                                 fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')

        if not id:
            return

        DbController.delete('orders', id)
        
        clear()
        sort_orders_by_status()
        dicts_to_table(data)


        if input(fmt_string('Item SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def select_order_items(current_items: list[int] = []) -> list[int]:
    # While -> Print / Select Catagorys
    result = []
    cat_map = get_external_data('catagory_mapping')
    is_in_menu = True
    while is_in_menu:
        clear()
        menus = [item for item in cat_map]
        list_to_table(menus, 'Catagories', enumerate=True)
        option = get_validated_input(
            'Please Select A Catagory: ', int, fg='Blue', min_length=1, max_value=len(menus), cancel_on=0)

        if not option:
            is_in_menu = False
            continue

        is_in_cat = True
        while is_in_cat:
            clear()
            sub_menu = menus[option - 1]
            indexs = cat_map[sub_menu]
            products_list = get_external_data('products')

            items = [get_value_from_key(
                source=products_list, get='name', where='id', equals=index) for index in indexs]
            list_to_table(items, sub_menu.title(), enumerate=True)

            cat_option = get_validated_input(
                'Please Select A Item: ', int, fg='Blue', min_length=1, max_value=len(items), cancel_on=0)

            if not cat_option:
                is_in_cat = False
                continue

            item_index = get_value_from_key(
                source=products_list, get='id', where='name', equals=items[cat_option - 1])

            result.append(item_index)

    return result + current_items
# endregion := View


# region := TODO

# TODO: Fix Sorting On Order Functions!

# TODO: Add Select Order Items Functionality For DB's

# endregion := TODO


# region := Setup
external_data = load_json('./data/config.json')

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
            show_add_order_menu,
            show_update_status_menu,
            show_update_order_menu,
            show_delete_order_menu
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
    load_external_data(external_data)
    while menu_state:
        show_menu(menu_state)
        save_external_data(external_data)
    close_connections()
# endregion :=Setup
