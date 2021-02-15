import os
from dotenv import load_dotenv
from pymysql import NULL

from .DbController import DbController
from .cli import clear, dicts_to_table, fmt_string, get_validated_input, list_to_table, validated_input
from .file_system import log
load_dotenv()


def not_implemented():
    input(fmt_string('Feature Not Yet Implemented', fg='White', bg='Red'))


def show_menu(menu_name: str) -> None:
    # Set the global menu_state to the selected menu to allow us to backtrack when returning
    global menu_state
    menu_state = menu_name
    log('debug', f'Menu {menu_name} loaded')
    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.\n', fg='Blue'))

    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    #print_table(menu['title'], menu['items'])
    list_to_table(menu['items'], menu['title'])

    if (menu_option := validated_input('\nPlease Select An Option.\n', int, fg='Green', min_value=0, max_value=len(menu['handlers'])-1))[0] == 0:
        log('debug', menu_option[1])
        input(menu_option[1])
        return

    # Call the function associated with the selected menu item
    menu['handlers'][menu_option[1]]()


def print_data_view(key: str) -> None:  # type: ignore
    if key == 'orders':
        is_looping = True
        data = DbController.get_joins(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS Courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status'],
            order='ORDER BY o.status'
        )

        current_ids = [item['id']
                       for item in DbController.get_column(key, 'id')]

        while is_looping:
            clear()
            dicts_to_table(data, paginate=True)
            index = get_validated_input(
                'Please Select An Id To View (-1 To Sort): ', int, fg='Blue', cancel_on='0', is_present=current_ids + [-1])
            if index == False:
                is_looping = False
                continue

            if index == -1:
                clear()
                dicts_to_table(data, paginate=True)
                sort_on_keys = list(data[0].keys())
                list_to_table(sort_on_keys, 'Available Sorts', enumerate=True)
                sort_key = get_validated_input(
                    'How Would You Like To Sort By [id]? ', int, fg='Blue', min_value=1, max_value=len(sort_on_keys), cancel_on=0)
                data = DbController.get_joins(
                    fields=['o.id', 'o.name', 'o.address',
                            'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
                    source='orders o',
                    targets=['couriers courier', 'status s'],
                    conditions=['courier.id = o.courier', 's.id = o.status'],
                    order=f'ORDER BY {sort_key}'
                )
                continue

            for order in data:
                if order['id'] == index:
                    clear()
                    show_order_detail_menu(order)
    else:
        data = DbController.get_all_rows(key)
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
                data = DbController.get_all_rows(key, order=f'ORDER BY {sort_key}')
                continue


def show_add_item_menu(get_key: str) -> None:
    data = DbController.get_all_rows(get_key)
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
            if key != 'id' and key != 'basket':
                if key == 'name':
                    value = get_validated_input(
                        f'Please Enter {key.replace("_"," ").title()}: ', type(value), fg='Blue', min_length=1, unique=current_names, cancel_on='0')
                else:
                    value = get_validated_input(
                        f'Please Enter {key.replace("_"," ").title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')

                if not value:
                    return

                new_dict[key] = value

        DbController.insert(get_key, new_dict)

        clear()
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_update_item_menu(get_key: str) -> None:
    data = DbController.get_all_rows(get_key)
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

        DbController.update(get_key, id, new_dict)
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_delete_item_menu(get_key: str) -> None:
    data = DbController.get_all_rows(get_key)
    current_ids = [item['id'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        item_id = get_validated_input(
            f'Please Enter An ID To Delete: ', int, fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')

        if not item_id:
            return

        DbController.delete(get_key, item_id)

        clear()
        data = DbController.get_all_rows(get_key)
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_add_order_menu() -> None:
    display_data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status'],
        order='ORDER BY o.status'
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

                elif key == 'basket':
                    new_value = NULL

                else:
                    new_value = get_validated_input(
                        f'Please Enter {key.title()}: ', type(value), fg='Blue', min_length=1, cancel_on='0')

                if new_value == False:
                    return

                new_dict[key] = new_value

            clear()
            dicts_to_table(display_data)
            print(fmt_string('\nCreating New Order...', fg='Cyan'))
            dicts_to_table([new_dict], headers=list(
                display_data[0].keys())[1:-2])

        clear()
        dicts_to_table(display_data)
        print(fmt_string('\nOrder Complete!', fg='Green'))
        dicts_to_table([new_dict], headers=list(display_data[0].keys())[1:-2])

        if input(fmt_string('Does This Look Correct?[y/n]\n', fg='Green')).lower() == 'n':
            continue

        DbController.insert('orders', new_dict)

        clear()

        display_data = DbController.get_joins(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status'],
            order='ORDER BY o.status'
        )

        dicts_to_table(display_data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_order_detail_menu(order) -> None:
    for k, v in order.items():
        if k == 'status':
            col = DbController.get_all_rows_where(
                'status', 'code', v)[0]['style']
            print(fmt_string(f'{str(k).title()}: ', fg='Blue'),
                  fmt_string(f'{str(v).title()}\n', fg=col))
        else:
            print(fmt_string(f'{str(k).title()}: ',
                             fg='Blue'), f'{str(v).title()}\n')

    items = DbController.get_all_rows_where('basket', 'order_id', order['id'])
    items = DbController.get_joins_where(
        fields=['b.quantity AS "#x"', 'p.name',
                'b.quantity * p.price AS "Sub Total"'],
        source='orders o',
        targets=['basket b', 'products p'],
        conditions=[f'b.order_id = {order["id"]}', 'b.item = p.id'],
        where=f'o.id = {order["id"]}',
        type='INNER'
    )

    if len(items) > 0:  # type: ignore
        dicts_to_table(items)  # type: ignore
    else:
        print(fmt_string('Order: ', fg='Blue'),
              fmt_string('Basket Is Empty', fg='Red'))

    input(fmt_string('\nPress ENTER To Continue', fg='Green'))


def show_update_status_menu() -> None:
    data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status'],
        order='ORDER BY o.status'
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

        DbController.update('orders', index, current_row)

        data = DbController.get_joins(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status'],
            order='ORDER BY o.status'
        )
        
        clear()
        dicts_to_table(data)

        if input(fmt_string('Status SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False
            continue


def show_update_order_menu() -> None:
    data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status', 'basket'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status'],
        order='ORDER BY o.status'
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
            where=f'o.id = {id}',
            order='ORDER BY o.status'
        )

        dicts_to_table(order)

        for key, value in items:
            if key != 'id':
                if key == 'basket':
                    select_order_items(id)

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
                        value = DbController.get_rows_where(
                            'orders', 'status', 'id', id)[0]['status']

                elif key == 'courier':
                    courier_list = DbController.get_all_rows('couriers')
                    courier_ids = [courier['id'] for courier in courier_list]

                    clear()
                    dicts_to_table(order)
                    dicts_to_table(courier_list)
                    value = get_validated_input(
                        f'Please Select {key.title()}: ', int, fg='Blue', is_present=courier_ids, cancel_on='0', cancel_text='SKIP')

                    if not value:
                        value = DbController.get_rows_where(
                            'orders', 'courier', 'id', id)[0]['courier']

                else:
                    value = get_validated_input(
                        f'Please Enter New {key.title()}: ', type(value), fg='Blue', min_length=0, cancel_on='', cancel_text='SKIP')

                    if not value:
                        value = order[0][key]

                new_dict[key] = value

        DbController.update('orders', id, new_dict)

        clear()
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_delete_order_menu() -> None:
    data = DbController.get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status'],
        order='ORDER BY o.status'
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

        data = DbController.get_joins(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status'],
            order='ORDER BY o.status'
        )
        
        clear()
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def select_order_items(order_id) -> None:
    current_basket = list(DbController.get_joins_where(
        source='basket b',
        fields=['p.id', 'p.name', 'b.quantity'],
        targets=['products p'],
        conditions=['b.item = p.id'],
        where=f'b.order_id = {order_id}'
    ))

    current_rows = DbController.get_all_rows_where(
        'basket', 'order_id', order_id)
    current_ids = [item['item'] for item in current_rows]

    catagories = DbController.get_all_rows('catagories')
    catagory_ids = [cat['id'] for cat in catagories]

    to_update = []
    to_insert = []
    to_delete = []

    is_in_cat = True
    while is_in_cat:
        clear()
        if len(current_basket) > 0:
            dicts_to_table(current_basket)
        print(fmt_string(
            f'Updating Basket For Order {order_id}...', fg='Cyan'))
        dicts_to_table(catagories)

        catagory = get_validated_input('Please Select A Catagory: ', int,
                                       fg='Blue', is_present=catagory_ids, cancel_on='0', cancel_text='SKIP')

        if not catagory:
            is_in_cat = False
            continue

        is_in_product = True
        while(is_in_product):
            clear()
            if len(current_basket) > 0:
                dicts_to_table(current_basket)

            products = DbController.get_rows_where(
                'products', 'id, name', 'catagory', catagory)
            product_ids = [item['id'] for item in products]

            print(fmt_string(
                f'Updating Basket For Order {order_id}...', fg='Cyan'))
            dicts_to_table(products)

            product = get_validated_input(
                'Please Select An Item: ', int, fg='Blue', is_present=product_ids, cancel_on='0', cancel_text='GO BACK')

            if not product:
                is_in_product = False
                continue

            quantity = get_validated_input(
                'Please Enter A Quantity: ', int, fg='Blue', cancel_on='0', cancel_text='GO BACK')

            if product in current_ids:
                for item in current_rows:
                    if item['item'] == product:
                        if item['quantity'] + quantity <= 0:
                            to_delete.append(item)
                            current_rows.remove(item)

                            for row in current_basket:
                                print(row['id'], product)
                                if row['id'] == product:
                                    current_basket.remove(row)

                        else:
                            item['quantity'] += quantity
                            to_update.append(item)

                            for row in current_basket:
                                if row['id'] == product:
                                    row['quantity'] += quantity

            else:
                to_insert.append(
                    {'order_id': order_id, 'item': product, 'quantity': quantity})
                for row in products:
                    if row['id'] == product:
                        current_basket.append(
                            {'id': product, 'name': row['name'], 'quantity': quantity})

    for record in to_update:
        DbController.update_where('basket', ['order_id', 'item'], [
                                  order_id, record['item']], record)

    for record in to_delete:
        DbController.delete_where('basket', ['order_id', 'item'], [
                                  order_id, record['item']])

    for record in to_insert:
        DbController.insert('basket', record)


def search_table(table: str):
    clear()
    term = get_validated_input('Please Enter A Search Term: ', fg='Blue')
    data = DbController.search_table(table, term)
    if len(data) > 0:
        dicts_to_table(data)
    else:
        print(fmt_string('No Results Found', fg='White', bg='Red'))
    input(fmt_string('Press Enter To Continue', fg='Green'))

# region := Setup
menus = {
    'main_menu': {
        'title': 'Main Menu',
        'items': ['[0] ❌ Exit',
                  'Separator',
                  '[1] 🧇 Product Maintainance',
                  '[2] 🚚 Courier Maintainance',
                  '[3] 📋 Order Maintainance',
                  '[4] ⚙ System Maintainance'
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
        'items': ['[0] ⏪ Return To Main Menu',
                  'Separator',
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
                     lambda: search_table('products')
                     ]
    },
    'courier_menu': {
        'title': 'Courier Maintainance',
        'items': ['[0] ⏪ Return To Main Menu',
                  'Separator',
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
                     lambda: search_table('couriers')
                     ]
    },
    'orders': {
        'title': 'Manage Orders',
        'items': [
            '[0] ⏪ Return To Main Menu',
            'Separator',
            '[1] View Current Orders',
            '[2] Create New Order',
            '[3] Update Status',
            '[4] Update Order',
            '[5] Delete Order',
            '[6] Search'
        ],
        'handlers': [
            lambda: show_menu('main_menu'),
            lambda: print_data_view('orders'),
            show_add_order_menu,
            show_update_status_menu,
            show_update_order_menu,
            show_delete_order_menu,
            lambda: search_table('orders')
        ]
    },
    'system_maintainance_menu': {
        'title': 'System Maintainance',
        'items': [
            '[0] ⏪ Return To Main Menu',
            'Separator',
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
    host = os.environ.get("mysql_host")
    user = os.environ.get("mysql_user")
    password = os.environ.get("mysql_pass")
    database = os.environ.get("mysql_db")
    DbController(host, user, password, database)  # type: ignore
    while menu_state:
        show_menu(menu_state)
    DbController.close()
# endregion :=Setup
