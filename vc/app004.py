import datetime
import os
from pathlib import Path
from typing import Any
from modules.utils import *

base_path = Path(__file__).parent


# region := Utils
colors = {
    'Black': 30,
    'Red': 31,
    'Green': 32,
    'Yellow': 33,
    'Blue': 34,
    'Magenta': 35,
    'Cyan': 36,
    'White': 37,
    'Unset': 0

}

def fmt_string(msg: str, fg: str ='White', bg: str ='Unset') -> str:
    return f'\u001b[{colors[fg]};1m\u001b[{colors[bg]+10};1m{msg}\u001b[0m'


def print_palette(col: str) -> None:

    if col == 'All':
        for fg_col in colors:
            line = ''

            for bg_col in colors:
                line += fmt_string(f'[{fg_col}][{bg_col}]',
                                   fg=fg_col, bg=bg_col)

            print(line)

    else:
        for fg_col in colors:
            print(fmt_string(f'[{fg_col}]', fg=fg_col, bg=col))


def print_outline(width: int) -> None:
    print(f"    +{'=' * (width + 8)}+")


def print_row(row: str, width: int) -> None:
    print(
        f"    |{row}{' ' * (width - len(row) + 7)} |")


def print_rows(rows: list[Any], width: int) -> None:
    for row in rows:
        print_row(row, width)

    print_outline(width)


def print_title(name: str, width: int) -> None:
    print_outline(width)
    print_row(name.upper(), width)
    print_outline(width)


def get_width(rows: list[Any]) -> int:
    # Get the len of the longest string in a given table to calculate the needed width of the table
    if len(rows) != 0:
        return max(len(row) for row in rows)

    else:
        return 10


def print_table(name: str, rows: list[Any]) -> None:
    print()
    width = get_width(rows)
    width = width if len(name) < width else len(name)
    print_title(name, width)
    print_rows(rows, width)
    print()


def clear() -> None:
    print('\n' * 1000)
    os.system('clear')


def get_absolute_path(filepath: str) -> Path:
    global base_path
    return (base_path / filepath).resolve()


def log(type: str, msg: str , logfile: str ='../data/log.log') -> None:

    try:
        with open(get_absolute_path(logfile), 'a') as file:
            file.write(
                f'{datetime.datetime.now()} @ {type.upper()}: {msg}' + '\n')

    except Exception as err:
        print(f'CRITICAL - Unable to create log: {str(err)}')
        input()


def load_list(filename: str, lst: list[Any]) -> None:
    try:
        with open(get_absolute_path(filename), 'r') as file:
            for item in file.readlines():
                item = item.strip()
                lst.append(item)

            log('info', f'{filename} successfully loaded')

    except Exception as err:
        log('error', f'Failed to load data - {str(err)}')


def save_list(filename: str, lst: list[Any], mode: str ='w') -> None:
    try:
        with open(get_absolute_path(filename), mode) as file:
            for item in lst:
                file.write(item + '\n')

            log('info', f'data successfully saved to {filename}')

    except Exception as err:
        log('error', f'Failed to save data - {str(err)}')


def load_external_data(data: dict[str, Any]) -> None:
    for data_source in data.values():
        load_list(data_source['location'], data_source['data'])


def save_external_data(data: dict[str, Any]) -> None:
    for data_source in data.values():
        save_list(data_source['location'], data_source['data'])


def get_external_data(key: str, attr: str='data') -> Any:
    global external_data
    return external_data[key][attr]


def validated_input(prompt: str, *types: type, **options: Any) -> tuple[int, Any]:

    if 'fg' in options:
        value = input(fmt_string(prompt, fg=options['fg'])).lower()

    elif 'bg' in options:
        value = input(fmt_string(prompt, fg=options['bg'])).lower()

    elif 'fg' in options and 'bg' in options:
        value = input(fmt_string(
            prompt, fg=options['fg'], bg=options['bg'])).lower()

    else:
        value = input(fmt_string(prompt)).lower()

    if int in types:
        try:
            result = int(value)

            if 'max_value' in options:
                if result > options['max_value']:
                    return 0, fmt_string(f'Input [{result}] was greater than than allowed value [{options["max_value"]}]', fg='White', bg='Red')

            return 1, result

        except ValueError:
            if str not in types:
                return 0, fmt_string(f'Input type [{str(type(value))}] is not one of the valid input type {str(types)}', fg='White', bg='Red')

    if 'min_length' in options:
        if len(value) < options['min_length']:
            return 0, fmt_string(f'Length of input [{len(value)}] is less than the required length [{options["min_length"]}]', fg='White', bg='Red')

    if 'max_length' in options:
        if len(value) > options['max_length']:
            return 0, fmt_string(f'Length of input [{len(value)}] is greater than the maximum [{options["max_length"]}]', fg='White', bg='Red')

    if 'unique' in options:
        if value in options['unique']:
            return 0, fmt_string(f'Input value {value} is already present in object', fg='White', bg='Red')

    if 'is_present' in options:
        if value not in options['is_present']:
            return 0, fmt_string(f'Input value {value} can not be found in object', fg='White', bg='Red')

    return 1, value

# endregion

# region := App


def show_menu(menu_name: str) -> None:
    # Set the global menu_state to the selected menu to allow us to backtrack when returning
    global menu_state
    menu_state = menu_name

    log('debug', f'Menu {menu_name} loaded')

    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.', fg='Blue'))

    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    print_table(menu['title'], menu['items'])

    if (menu_option := validated_input('Please Select An Option.\n', int, fg='Green', max_value=len(menu['handlers'])-1))[0] == 0:
        log('debug', menu_option[1])
        input(menu_option[1])
        return

    # Call the function associated with the selected menu item
    menu['handlers'][menu_option[1]]()


def print_list(lst: list[Any], title: str ='All Items') -> None:
    # Wrapper for print_table, to allow us to print the each items index number beside its name
    print_table(
        title, [f'[{i+1}] {name.title()}' for i, name in enumerate(lst)])


def print_list_view(key: str) -> None:
    # Wrapper for print_list to allow it to be used as it's own menu 'page'
    lst = get_external_data(key)
    log('debug', f'Menu print_list_view loaded')

    clear()
    print_list(lst, f'All {key}')

    input(fmt_string('Press "ENTER" to return to the previous menu', fg='Green'))


def create_list_item(key: str) -> None:
    lst = get_external_data(key)

    is_looping = True

    # Loop until the user decides otherwise, to provide us to add multiple items or reset after invalid input
    while is_looping:
        log('info', f'Attempting to create new item')

        clear()
        print_list(lst)
        print(fmt_string('Enter 0 to return to the previous menu!', fg='Green'))
        
        res, value = validated_input(
            'Item Name:\t', str, fg='Blue', min_length=1, unique=lst)

        if res == 0:
            if (_ := input(f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                log('debug', value)
                is_looping = False
            continue

        # Cancel Condition
        if value == '0':
            return

        lst.append(value)
        log('info', f'New item added - {value}')

        clear()
        print_list(lst)

        if (_ := input(fmt_string('New Item Successfully Added.\nWould you like to add another? [y/n]', fg='Green')).lower()) == 'n':
            is_looping = False

    save_external_data(external_data)


def update_list_item(key: str, idx: Any=None) -> None:
    lst = get_external_data(key)

    is_looping = True

    # Loop until the user decides otherwise, to provide us to update multiple items or reset after invalid input
    while is_looping:
        index = None
        log('info', f'Attempting to update item')

        clear()
        print_list(lst)
        print(fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        # If the caller has not provided an index then get this as input from the user
        if idx == None:
            
            res, old_value = validated_input(
                'Which item would you like to update?[ID/Name]: ', int, str, fg='Blue', max_value=len(lst), min_length=1, is_present=lst)

            if res == 0:
                if (_ := input(f'{old_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                    log('debug', old_value)
                    is_looping = False
                continue

            # Cancel condition
            if old_value == '0':
                return

            # If the user entered a string name, get the index based on that
            if type(old_value) == str:
                index = lst.index(old_value)

            else:
                index = old_value - 1

        # Caller has provided index so set it
        else:
            index = idx

        # Get the new value
        res, new_value = validated_input(
            'What is the new value?:\t', str, fg='Blue', unique=lst)
        
        if res == 0:
            if (_ := input(f'{new_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                log('debug', new_value)
                is_looping = False
            continue

        # Finally update the value and check for reset or return
        log('info', f'{lst[index]} updated - new value = {new_value}')
        lst[index] = new_value

        clear()
        print_list(lst)

        if(_ := input(fmt_string('New Item Successfully Updated.\nWould you like to add another? [y/n]', fg='Green')).lower()) == 'n':
            is_looping = False

        idx = None

    save_external_data(external_data)


def delete_list_item(key: str, idx: Any=None) -> None:
    lst = get_external_data(key)

    is_looping = True
    # Loop until the user decides otherwise, to provide us to update multiple items or reset after invalid input
    while is_looping:
        index = None
        log('info', f'Attempting to delete item')

        clear()
        print_list(lst)
        print(fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        # If the caller doen't provide an item index, get it from user input
        if idx == None:
            
            res, item_name = validated_input(
                'Which item would you like to delete?[ID/Name]: ', int, str, fg='Blue', max_value=len(lst), min_length=1, is_present=lst)

            if res == 0:
                if (_ := input(f'{item_name}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                    log('debug', item_name)
                    is_looping = False
                continue

            # Cancel condition
            if item_name == 0:
                return

            if type(item_name) == str:
                index = lst.index(item_name)
            else:
                index = item_name - 1

        # Caller has provided index so set it
        else:
            index = idx

        # Finally delete the item from the list
        log('info', f'{lst[index]} successfully deleted')
        del lst[index]

        clear()
        print_list(lst)

        if(_ := input(fmt_string(f'Item Successfully Deleted.\nWould you like to delete another? [y/n]', fg='Green')).lower()) == 'n':
            is_looping = False

        idx = None

    save_external_data(external_data)


def search(term: str, lists: list[Any]) -> list[dict[str, Any]]:
    results = []

    # Create a dictionary for each list passed to store the results from each
    for lst in lists:
        dtn = {
            'title': lst,
            # Reference to actual list object to allow future function calls
            'list': external_data[lst]['data']
        }

        items = []

        # Loop through list, if a match is found add it to the items list. Note an empty string returns all items
        for item in external_data[lst]['data']:
            if term in item:
                items.append(item)

            dtn['items'] = items

        results.append(dtn)
    return results


def search_list(lst: list[Any]) -> None:
    clear()
    action_options = ['u', 'd', 'v', '0']

    search_term = input(fmt_string(
        'please enter a seach term.', fg='Blue')).lower()

    is_looping = True
    while is_looping:

        results = search(search_term, lst)

        clear()
        count = 0  # To display number of results found to user

        # Loop through the results removing any lists thats didn't not contain a match
        # This is enumerated to allow us access to the list index and revesed to deal with shifting after a del
        for i, dtn in reversed(list(enumerate(results))):
            items = dtn['items']
            count += len(items)

            if len(items) < 1:
                del results[i]

        # Display the results to the user in a more readable form - 1 table per list supplied with ID number
        for i, dtn in enumerate(results):
            print_list(dtn['items'], title=f'[{i+1}] {dtn["title"]}')

        print(
            f'\nResults Found: {fmt_string(str(count),fg="Green" if count > 0 else "Red" )}')

        if count < 1:
            input(fmt_string('Press "ENTER" to return to the previous menu', fg='Green'))
            print(results)
            return

        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        # If only one table contained a match set the table to access as the first one in the list, to prevent unneccasary input
        if len(results) != 1:
            res, list_option = validated_input(
                'Which Table Would You Like To Access[ID]: ', int, fg='Blue', max_value=len(results))
            if res == 0:
                if (_ := input(f'{list_option}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                    log('debug', list_option)
                    is_looping = False
                continue

            # Cancel condition
            if list_option == 0:
                return

            list_index = list_option - 1

        else:
            list_index = 0

        # list that contains results as strings
        working_result_list = results[list_index]['items']
        # reference to the actual list object
        working_list = results[list_index]['list']
        
        res, item_option = validated_input(
            'Which Item Would You Like To Access[ID]: ', int, fg='Blue', max_value=len(working_result_list))

        if res == 0:
            if (_ := input(f'{item_option}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                log('debug', item_option)
                is_looping = False
            continue

        # Cancel condition
        if item_option == 0:
            return

        item_index = item_option - 1
        
        res, action_option = validated_input(
            'Which Would You Like To Do?[(u)pdate, (d)elete, (v)iew]: ', str, fg='Blue', min_length=1, max_length=1, is_present=action_options)

        if res == 0:
            if (_ := input(f'{action_option}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}').lower()) == 'n':
                log('debug', action_option)
                is_looping = False
            continue

        # Cancel condition
        if action_option == 0:
            return

        # Call relevent function based on option selected
        # results index likely is not list index, i.e. result index 4 may be list index 10 etc. so get actual index using .index()
        working_list_index = working_list.index(
            working_result_list[item_index])
        working_list_key = results[list_index]['title']

        if action_option == 'u':
            update_list_item(working_list_key, idx=working_list_index)

        elif action_option == 'd':
            delete_list_item(working_list_key, idx=working_list_index)

        elif action_option == '0':
            return

        else:
            print_list_view(working_list_key)


external_data = {
    'products': {
        'data': [],
        'location': '../data/products.txt'
    },
    'couriers': {
        'data': [],
        'location': '../data/couriers.txt'
    }
}

menus = {
    'main_menu': {
        'title': 'Main Menu',
        'items': ['[0] Exit',
                  '[1] Product Maintainance',
                  '[2] Courier Maintainance',
                  '[3] Search'
                  ],
        'handlers': [exit,
                     lambda: show_menu('product_menu'),
                     lambda: show_menu('courier_menu'),
                     lambda: search_list([lst for lst in external_data])
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
                     lambda: print_list_view('products'),
                     lambda: create_list_item('products'),
                     lambda: update_list_item('products'),
                     lambda: delete_list_item('products'),
                     lambda: search_list(['products'])
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
                     lambda: print_list_view('couriers'),
                     lambda: create_list_item('couriers'),
                     lambda: update_list_item('couriers'),
                     lambda: delete_list_item('couriers'),
                     lambda: search_list(['couriers'])
                     ]
    }
}


# Start Loop
menu_state = 'main_menu'

load_external_data(external_data)

while menu_state:
    show_menu(menu_state)
    save_external_data(external_data)

# endregion App
