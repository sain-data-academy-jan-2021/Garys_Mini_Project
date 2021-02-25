from datetime import datetime
import os
from typing import Any
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import textwrap

from .DbController import DbController
from .cli import clear, dicts_to_table, fmt_string, get_validated_input, list_to_table, validated_input, dict_builder
from .file_system import LOG_LEVELS, log
load_dotenv()


def get_order_data(sort: str = 'o.status') -> list[dict[Any, Any]]:
    return DbController.instance().get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS Courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status'],
        order=f'ORDER BY {sort}'
    )


def get_cats(data: list[dict[Any, Any]], action: str = 'join') -> list[dict[Any, Any]]:
    cats = DbController.instance().get_all_rows('catagories', '*')
    for row in data:
        if 'catagory' in row:
            if action == 'join':
                for cat in cats:
                    if row['catagory'] == cat['id']:
                        row['catagory'] = cat['name']
            elif action == 'delete':
                del row['catagory']

    return data


#region := App
def show_menu(menu_name: str) -> None:
    # Set the global menu_state to the selected menu to allow us to backtrack when returning
    global menu_state
    menu_state = menu_name
    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.\n', fg='Blue'))
    log('debug', f'Menu {menu_name} loaded')
    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    #print_table(menu['title'], menu['items'])
    list_to_table(menu['items'], menu['title'])

    if (menu_option := validated_input('\nPlease Select An Option.\n', int, fg='Green', min_value=0, max_value=len(menu['handlers'])-1))[0] == 0:
        input(menu_option[1])
        return

    # Call the function associated with the selected menu item
    menu['handlers'][menu_option[1]]()


def print_data_view(key: str) -> None:
    data = get_cats(DbController.instance().get_all_rows(key, '*'))

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
            # Get a list of the current column names to be used in a sort order
            sort_on_keys = [key for key in data[0]]
            list_to_table(sort_on_keys, 'Available Sorts', enumerate=True)
            sort_key = get_validated_input(
                'How Would You Like To Sort By [id]? ', int, fg='Blue', min_value=1, max_value=len(sort_on_keys), cancel_on=0)
            # Refresh data with selected sort order
            data = DbController.instance().get_all_rows(
                key, '*', order=f'ORDER BY {sort_key}')
            continue


def show_add_item_menu(get_key: str) -> None:
    data = get_cats(DbController.instance().get_all_rows(
        get_key, '*'), action='delete')

    current_names = [item['name'] for item in data]

    schema = {k.lower(): type(v) for (k, v) in data[0].items()}
    validation = {
        'all': {'min_length': 1, 'cancel_on': '0', 'fg': 'Blue'},
        'name': {'unique': current_names}
    }

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)

        new_dict = dict_builder(
            schema, ['id', 'basket'], validation=validation)
        if not new_dict:
            return

        DbController.instance().insert(get_key, new_dict)

        clear()
        data = get_cats(DbController.instance().get_all_rows(
            get_key, '*'), action='delete')
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_update_item_menu(get_key: str) -> None:
    data = get_cats(DbController.instance().get_all_rows(
        get_key, '*'), action='delete')

    current_ids = [item['id'] for item in data]

    schema = {k.lower(): type(v) for (k, v) in data[0].items()}
    validation = {'all': {'min_length': 1, 'cancel_on': '0', 'fg': 'Blue'}}

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)

        id = get_validated_input('Please Enter An ID To Edit: ', int,
                                 fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')
        if not id:
            return

        new_dict = dict_builder(schema, ['id', 'items'], validation=validation)
        if not new_dict:
            return

        DbController.instance().update(get_key, id, new_dict)
        clear()
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_delete_item_menu(get_key: str) -> None:
    data = get_cats(DbController.instance().get_all_rows(
        get_key, '*'), action='delete')

    current_ids = [item['id'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        item_id = get_validated_input(
            f'Please Enter An ID To Delete: ', int, fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')
        if not item_id:
            return

        DbController.instance().delete(get_key, item_id)

        clear()
        data = DbController.instance().get_all_rows(get_key, '*')
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def search_table(table: str):
    clear()
    term = get_validated_input('Please Enter A Search Term: ', fg='Blue')

    if table == 'orders':
        data = DbController.instance().search_joined_table(
            table='orders o',
            term=term,
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS Courier', 's.code AS status'],
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status']
        )
    else:
        data = DbController.instance().search_table(table, term)

    if len(data) > 0:
        dicts_to_table(data)
    else:
        print(fmt_string('No Results Found', fg='White', bg='Red'))
    input(fmt_string('Press Enter To Continue', fg='Green'))


def print_order_view():
    is_looping = True
    data = get_order_data()

    # Get ID's of current orders to ensure that a valid one is selected
    current_ids = [item['id']
                   for item in DbController.instance().get_column('orders', 'id')]

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
            dicts_to_table(data, paginate=False)
            # Get a list of the current coloum names to be used in a sort order
            sort_on_keys = list(data[0].keys())
            list_to_table(sort_on_keys, 'Available Sorts', enumerate=True)
            sort_key = get_validated_input(
                'What Would You Like To Sort By [id]? ', int, fg='Blue', min_value=1, max_value=len(sort_on_keys), cancel_on=0)
            # Status sorts on id not named string so set this if status is selected
            data = get_order_data(
                sort_key if sort_key != 7 else 'o.status')
            continue

        for order in data:
            if order['id'] == index:
                clear()
                show_order_detail_menu(order)


def show_order_detail_menu(order) -> None:
    # Use the data recived in view_order to print -> use the `status` tables style value to colour by status
    for k, v in order.items():
        if k == 'status':
            col = DbController.instance().get_rows_where(
                'status', '*', 'code', v)[0]['style']
            print(fmt_string(f'{str(k).title()}: ', fg='Blue'),
                  fmt_string(f'{str(v).title()}\n', fg=col))
        else:
            print(fmt_string(f'{str(k).title()}: ',
                             fg='Blue'), f'{str(v).title()}\n')

    # Get the orders current basket from the `basket` table and add a total price per item on
    items = DbController.instance().get_joins_where(
        fields=['b.quantity AS "#x"', 'p.name',
                'b.quantity * p.price AS "Sub Total"'],
        source='orders o',
        targets=['basket b', 'products p'],
        conditions=[f'b.order_id = {order["id"]}', 'b.item = p.id'],
        where=f'o.id = {order["id"]}',
        type='INNER'
    )

    if len(items) > 0:
        dicts_to_table(items)
    else:
        print(fmt_string('Order: ', fg='Blue'),
              fmt_string('Basket Is Empty', fg='Red'))

    input(fmt_string('\nPress ENTER To Continue', fg='Green'))


def show_add_order_menu() -> None:
    display_data = get_order_data()

    schema = {k.lower(): type(v) for (k, v) in display_data[0].items()}
    validation = {'all': {'min_length': 1, 'cancel_on': '0', 'fg': 'Blue'}}

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(display_data)

        new_dict = dict_builder(
            schema, ['id', 'courier', 'status'], validation)
        if not new_dict:
            return

        clear()
        dicts_to_table(display_data)
        print(fmt_string('\nOrder Complete!', fg='Green'))

        dicts_to_table([new_dict], headers=list(display_data[0].keys())[1:-2])

        if input(fmt_string('Does This Look Correct?[y/n]\n', fg='Green')).lower() == 'n':
            continue

        DbController.instance().insert('orders', new_dict)

        clear()
        display_data = get_order_data()
        dicts_to_table(display_data)

        if input(fmt_string('Item SuccessFully Added. Would You Like To Add Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_update_status_menu() -> None:
    data = get_order_data()
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

        status_list = DbController.instance().get_all_rows('status', 'id, code')
        current_row = DbController.instance().get_rows_where(
            'orders', '*', 'id', index)[0]

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
        DbController.instance().update('orders', index, current_row)
        data = get_order_data()

        clear()
        dicts_to_table(data)

        if input(fmt_string('Status SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False
            continue


def show_update_order_menu() -> None:
    data = get_order_data()
    current_ids = [item['id'] for item in data]
    status_list = DbController.instance().get_all_rows('status', '*')
    status_ids = [status['id'] for status in status_list]
    courier_list = DbController.instance().get_all_rows('couriers', '*')
    courier_ids = [courier['id'] for courier in courier_list]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)
        id = get_validated_input('Please Enter An ID To Edit: ', int,
                                 fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')
        if not id:
            return

        order = DbController.instance().get_joins_where(
            fields=['o.id', 'o.name', 'o.address',
                    'o.area', 'o.phone', 'courier.name AS courier', 's.code AS status'],
            source='orders o',
            targets=['couriers courier', 'status s'],
            conditions=['courier.id = o.courier', 's.id = o.status'],
            where=f'o.id = {id}',
            order='ORDER BY o.status'
        )

        clear()
        dicts_to_table(order)

        schema = {k.lower(): type(v) for (k, v) in data[0].items()}
        schema['courier'] = int
        schema['status'] = int
        validation = {
            'all': {'min_length': 0, 'cancel_on': '', 'cancel_text': 'SKIP', 'fg': 'Blue'},
            'status': {'is_present': status_ids, 'cancel_on': '0'},
            'courier': {'is_present': courier_ids, 'cancel_on': '0'}
        }
        on_key = {
            'status': [clear, lambda: dicts_to_table(order), lambda: dicts_to_table(status_list)],
            'courier': [clear, lambda: dicts_to_table(order), lambda: dicts_to_table(courier_list)]
        }
        
        new_dict = dict_builder(
            schema, ['id'], validation, on_key=on_key, on_cancel='skip')
        if not new_dict:
            return
        
        DbController.instance().update('orders', id, new_dict)
        select_order_items(id)

        clear()
        data = get_order_data()
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def show_delete_order_menu() -> None:
    data = get_order_data()

    current_ids = [item['id'] for item in data]

    is_looping = True
    while is_looping:
        clear()
        dicts_to_table(data)

        id = get_validated_input('Please Enter An ID To Delete: ', int,
                                 fg='Blue', min_length=1, is_present=current_ids, cancel_on='0')

        if not id:
            return

        DbController.instance().delete('orders', id)

        data = get_order_data()

        clear()
        dicts_to_table(data)

        if input(fmt_string('Item SuccessFully Updated. Would You Like To Update Another?[y/n]\n', fg='Green')) == 'n':
            is_looping = False


def select_order_items(order_id) -> None:
    current_basket = list(DbController.instance().get_joins_where(
        source='basket b',
        fields=['p.id', 'p.name', 'b.quantity'],
        targets=['products p'],
        conditions=['b.item = p.id'],
        where=f'b.order_id = {order_id}'
    ))

    current_rows = DbController.instance().get_rows_where(
        'basket', '*', 'order_id', order_id)
    current_ids = [item['item'] for item in current_rows]

    catagories = DbController.instance().get_all_rows('catagories', '*')
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

            # Reconcile duplicate records -> only affects locally
            if len(current_basket) > 0:
                for i in range(len(current_basket) - 1):
                    for j in range(i+1, len(current_basket)):
                        if current_basket[i]['id'] == current_basket[j]['id']:
                            current_basket[i]['quantity'] += current_basket[j]['quantity']
                            del current_basket[j]

                    if current_basket[i]['quantity'] <= 0:
                        del current_basket[i]

                dicts_to_table(current_basket)

            products = DbController.instance().get_rows_where(
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

            # reconcile updates to additions -> would affect table
            for i in range(len(to_insert) - 1):
                for j in range(i+1, len(to_insert)):
                    if to_insert[i]['item'] == to_insert[j]['item']:
                        to_insert[i]['quantity'] += to_insert[j]['quantity']
                        del to_insert[j]

                if to_insert[i]['quantity'] <= 0:
                    del to_insert[i]

    for record in to_update:
        DbController.instance().update_where('basket', ['order_id', 'item'], [
            order_id, record['item']], record)

    for record in to_delete:
        DbController.instance().delete_where('basket', ['order_id', 'item'], [
            order_id, record['item']])

    for record in to_insert:
        DbController.instance().insert('basket', record)


def update_catagory_mapping():
    is_in_cat = True
    while is_in_cat:
        cats = DbController.instance().get_all_rows('catagories', '*')
        cat_ids = [item['id'] for item in cats]
        clear()
        dicts_to_table(cats)

        selected_catagory = get_validated_input(
            'Please Select A Catagory To Update: ', int, fg='Blue', is_present=cat_ids, cancel_on='0')

        if not selected_catagory:
            is_in_cat = False
            continue

        is_editing = True
        while is_editing:
            data = DbController.instance().get_rows_where(
                'products', 'name, id', 'catagory', selected_catagory)
            product_ids = [
                item['id'] for item in DbController.instance().get_all_rows('products', 'id')]
            list_names = ['*' + item['name'] for item in data]
            list_ids = [item['id'] for item in data]

            clear()
            list_to_table(list_names, "Current Menu", max_length=3)

            dicts_to_table(get_cats(DbController.instance().get_all_rows('products', '*')),
                           paginate=True,
                           page_length=10,
                           on_clear=lambda: list_to_table(list_names, "Current Menu", max_length=3))

            selected_item = get_validated_input(
                'Please Select An Item To Add: ', int, fg='Blue', is_present=product_ids, cancel_on='0', cancel_text='GO BACK')

            if not selected_item:
                is_editing = False
                continue

            if selected_catagory == 9 and selected_item in list_ids:
                input(fmt_string(
                    'That Item Is Already In This Menu, But You Can Not Remove From The Default Menu', fg='White', bg='Red'))
                continue

            elif selected_item in list_ids:
                if input(fmt_string('That Item Is Already In This Menu. Would You Like To Remove It [y/n]? \n', fg='White', bg='Red')) == 'y':
                    DbController.instance().update(
                        'products', selected_item, {'catagory': 9})

            else:
                DbController.instance().update('products', selected_item,
                                               {'catagory': selected_catagory})
#endregion := App


# region :=Reports
def view_logs():
    clear()
    list_to_table([item for item in reversed(LOG_LEVELS.keys())],
                  'Levels', enumerate=True)
    log_level = get_validated_input(
        'Please Select A Log Level: \n', int, fg='Blue', is_present=[1, 2, 3, 4, 5])

    data = []
    try:
        with open('./data/log.log', 'r') as log_file:
            data = log_file.readlines()

    except Exception as err:
        log('critical', str(err))

    rows = []
    for row in data:
        temp_row = {}
        temp_split = row.split(' @ ')
        t = datetime.strptime(temp_split[0], '%Y-%m-%d %H:%M:%S.%f')
        temp_row['time'] = t.strftime('%Y-%m-%d %H:%M')
        temp_rest = temp_split[1]
        rest_split = temp_rest.split(': ')
        temp_row['type'] = rest_split[0].lower()
        msg = rest_split[1].strip()

        max_length = int(os.get_terminal_size().columns * 0.65)
        wrapper = textwrap.TextWrapper(width=max_length)
        wrapped = '\n'.join(wrapper.wrap(msg))
        temp_row['message'] = wrapped

        if LOG_LEVELS[temp_row['type']] >= log_level:
            rows.append(temp_row)

    dicts_to_table(rows, enumerated=True)
    input()


def view_procs():
    clear()
    views = DbController.instance().get_available_procs()
    list_to_table(views, 'Views', enumerate=True)
    action = get_validated_input('Select A Item To Preview: ', int,
                                 fg='Green', min_value=1, max_value=len(views), cancel_on='0')

    if not action:
        return

    dicts_to_table(DbController.instance().call_proc(
        views[action-1].replace(' ', '_')))

    input(fmt_string('Press Enter To Continue', fg='Green'))


def get_summary_by_status():
    sum = DbController.instance().call_proc('get_order_status_summary')
    labels = [item['status'] for item in sum]
    total = 0
    for item in sum:
        total += item['count']
    sizes = [item['count']/total for item in sum]
    _, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',  # type: ignore
            shadow=True, startangle=90)
    ax1.axis('equal')  # type: ignore
    plt.show()


def get_unassigned_orders():
    clear()
    print(fmt_string('Viewing: UNASSIGNED ORDERS', fg='Cyan'))
    data = DbController.instance().call_proc('get_unassigned_orders')
    if len(data) > 0:
        dicts_to_table(data)
        input(fmt_string('Press ENTER To Continue', fg='Green'))


def get_order_totals():
    data = DbController.instance().call_proc('get_order_totals')
    clear()
    print(fmt_string('Viewing: TOTALS BY ORDER', fg='Cyan'))
    dicts_to_table(data)
    input(fmt_string('Press ENTER To Continue', fg='Green'))


def get_free_couriers():
    clear()
    print(fmt_string('Viewing: FREE COURIERS', fg='Cyan'))
    data = DbController.instance().call_proc('get_unassigned_couriers')
    if len(data) > 0:
        dicts_to_table(data)
    input(fmt_string('Press ENTER To Continue', fg='Green'))
# endregion :=Reports


# region := Setup
menus = {
    'main_menu': {
        'title': 'Main Menu',
        'items': ['[0] ❌ Exit',
                  'Separator',
                  '[1] 🧇 Product Maintainance',
                  '[2] 🚚 Courier Maintainance',
                  '[3] 📋 Order Maintainance',
                  '[4] 📊 Reporting',
                  'Separator',
                  '[5] ⚙ System Maintainance'
                  ],
        'handlers': [exit,
                     lambda: show_menu('product_menu'),
                     lambda: show_menu('courier_menu'),
                     lambda: show_menu('orders'),
                     lambda: show_menu('reports'),
                     lambda: show_menu('system_maintainance_menu')
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
            print_order_view,
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
            '[1] Update Menu Grouping',
            '[2] View System Logs',
            '[3] Show Available Views'
        ],
        'handlers': [
            lambda: show_menu('main_menu'),
            update_catagory_mapping,
            view_logs,
            view_procs
        ]
    },
    'reports': {
        'title': 'reports',
        'items': [
            '[0] ⏪ Return To Main Menu',
            'Separator',
            '[1] Status Summary',
            '[2] Order Totals',
            '[3] Unassigned Orders',
            '[4] View Free Couriers'
        ],
        'handlers': [
            lambda: show_menu('main_menu'),
            get_summary_by_status,
            get_order_totals,
            get_unassigned_orders,
            get_free_couriers
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
    
    # If you can't connect to the DB, log, inform user and close the app
    if not DbController.instance().connection:
        log('critical', 'No Connection To Source Could Be Established')
        print(host,user, password, database)
        print(
            f'\u001b[37;1m\u001b[41;1mNo Connection To Source Could Be Established. Please Review Config\u001b[0m')
        input()
    while menu_state:
        show_menu(menu_state)

    DbController.instance().close()
# endregion :=Setup


# pytest --cov-config=.coveragerc --cov-report term:skip-covered --cov=.
