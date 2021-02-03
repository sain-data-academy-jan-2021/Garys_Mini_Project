import os
import datetime
from pathlib import Path

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

def fmt_string(msg, fg='White', bg='Unset'):
    return f'\u001b[{colors[fg]};1m\u001b[{colors[bg]+10};1m{msg}\u001b[0m'


def print_palette(col):

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


def print_outline(width):
    print(f"    +{'=' * (width + 8)}+")


def print_row(row, width):
    print(
        f"    |{row}{' ' * (width - len(row) + 7)} |")


def print_rows(rows, width):
    for row in rows:
        print_row(row, width)

    print_outline(width)


def print_title(name, width):
    print_outline(width)
    print_row(name.upper(), width)
    print_outline(width)


def get_width(rows):
    # Get the len of the longest string in a given table to calculate the needed width of the table
    if len(rows) != 0:
        return max(len(row) for row in rows)

    else:
        return 10


def print_table(name, rows):
    print()
    width = get_width(rows)
    width = width if len(name) < width else len(name)
    print_title(name, width)
    print_rows(rows, width)
    print()


def clear():
    print('\n' * 1000)
    os.system('clear')


def get_absolute_path(filepath: str):
    global base_path
    return (base_path / filepath).resolve()


def log(type, msg, logfile='../data/log.log'):

    try:
        with open(get_absolute_path(logfile), 'a') as file:
            file.write(
                f'{datetime.datetime.now()} @ {type.upper()}: {msg}' + '\n')

    except Exception as err:
        print(f'CRITICAL - Unable to create log: {str(err)}')
        input()


def load_list(filename, lst):
    try:
        with open(get_absolute_path(filename), 'r') as file:
            for item in file.readlines():
                item = item.strip()
                lst.append(item)

            log('info', f'{filename} successfully loaded')

    except Exception as err:
        log('error', f'Failed to load data - {str(err)}')


def save_list(filename, lst, mode='w'):
    try:
        with open(get_absolute_path(filename), mode) as file:
            for item in lst:
                file.write(item + '\n')

            log('info', f'data successfully saved to {filename}')

    except Exception as err:
        log('error', f'Failed to save data - {str(err)}')


def load_external_data(data):
    for data_source in data.values():
        load_list(data_source['location'], data_source['data'])


def save_external_data(data):
    for data_source in data.values():
        save_list(data_source['location'], data_source['data'])


def get_external_data(key: str):
    global external_data
    return external_data[key]['data']

# endregion

# region := App

def show_menu(menu_name):
    # Set the global menu_state to the selected menu to allow us to backtrack when returning
    global menu_state
    menu_state = menu_name

    log('info', f'Menu {menu_name} loaded')

    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.', fg='Blue'))

    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    print_table(menu['title'], menu['items'])

    try:
        # Try to cast user input to an int. This will be used an a list index for the menus' handler value
        menu_option = int(
            input(fmt_string('Please Select An Option.\n', fg='Green')))

        # Throw the IndexError before we actual cause it
        if menu_option > len(menu['handlers']) - 1:
            raise IndexError

    except (ValueError, IndexError) as err:
        input(fmt_string(
            'That option was not recognised. Press "ENTER" key to try again', fg='White', bg='Red'))

        log('warning', f'Option not recognised - {str(err)}')
        return

    # Call the function associated with the selected menu item
    menu['handlers'][menu_option]()


def print_list(lst, title='All Items'):
    # Wrapper for print_table, to allow us to print the each items index number beside its name
    print_table(title, [
                f'[{i+1}] {name.title()}' for i, name in enumerate(lst)])


def print_list_view(key):
    lst = get_external_data(key)

    # Wrapper for print_list to allow it to be used as it's own menu 'page'
    log('info', f'Menu print_list_view loaded')

    clear()
    print_list(lst)

    input(fmt_string('Press "ENTER" to return to the previous menu', fg='Green'))


def create_list_item(key):
    lst = get_external_data(key)

    is_looping = True

    # Loop until the user decides otherwise, to provide us to add multiple items or reset after invalid input
    while is_looping:
        log('info', f'Attempting to  create new item')

        clear()
        print_list(lst)
        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        item_name = input(fmt_string(
            'Item Name:\t', fg='Blue')).lower()

        # Cancel condition
        if item_name == '0':
            return

        # Input handling, restart function loop if input is empty
        if len(item_name) == 0:
            res = input(fmt_string(
                'You Must Enter A Value\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

            log('warning', f'Option not recognised - {item_name}')

            if res == 'n':
                is_looping = False

            continue

        # Input handling, restart function loop if the new item already exists
        if item_name in lst:
            res = input(fmt_string(
                'That Item Already Exists.\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

            log('warning', f'Duplicate item - {item_name}')

            if res == 'n':
                is_looping = False

            continue

        lst.append(item_name)
        log('info', f'New item added - {item_name}')

        clear()
        print_list(lst)

        res = input(fmt_string(
            'New Item Successfully Added.\nWould you like to add another? [y/n]', fg='Green')).lower()

        if res == 'n':
            is_looping = False

    save_external_data(external_data)


def update_list_item(key, idx=None):
    lst = get_external_data(key)

    is_looping = True

    # Loop until the user decides otherwise, to provide us to update multiple items or reset after invalid input
    while is_looping:
        index = None
        log('info', f'Attempting to update item')

        clear()
        print_list(lst)
        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        # If the caller has not provided an index then get this as input from the user
        if idx == None:

            old_value = input(
                fmt_string('Which item would you like to update?[ID/Name]: ', fg='Blue')).lower()

            # Cancel condition
            if old_value == '0':
                return

            # Input handling, restart function loop if input is empty
            if len(old_value) == 0:
                res = input(fmt_string(
                    'You Must Enter An ID or Value\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                log('warning', f'No option selected')

                if res == 'n':
                    is_looping = False

                continue

            try:
                # Try to cast input to an int to be used as and index into the list
                index = int(old_value) - 1

                # Throw the IndexError before we actual cause it
                if index >= len(lst):
                    raise IndexError

            # If the input can't be cast to an int, then treat the input as a string to search the list
            except (ValueError, IndexError) as err:

                # Input handling, input doesn't work as either index or string so reset
                if old_value not in lst:
                    res = input(fmt_string(
                        'That Item can\'t be found!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                    log('warning', f'Item does not exist - {old_value}')

                    if res == 'n':
                        is_looping = False
                    continue

                # Is a match is found with the input as a string, get it's index
                index = lst.index(old_value)

        # Caller has provided index so set it
        else:
            index = idx

        # Get the new value
        new_value = input(
            fmt_string('What is the new value?:\t', fg='Blue')).lower()

        # If new value is already taken reset loop
        if new_value in lst:
            res = input(fmt_string(
                'That Item already exists!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

            log('warning', f'Item already exists - {new_value}')

            if res == 'n':
                is_looping = False
            continue

        # Finally update the value and check for reset or return
        lst[index] = new_value
        log('info', f'{lst[index]} updated - new value = {new_value}')

        clear()
        print_list(lst)

        res = input(fmt_string(
            'Item Successfully Updated.\nWould you like to update another? [y/n]', fg='Green')).lower()

        if res == 'n':
            is_looping = False
        
        idx = None

    save_external_data(external_data)
    

def delete_list_item(key, idx=None):
    lst = get_external_data(key)

    is_looping = True
    # Loop until the user decides otherwise, to provide us to update multiple items or reset after invalid input
    while is_looping:
        index = None
        log('info', f'Attempting to delete item')

        clear()
        print_list(lst)
        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        # If the caller doen't provide an item index, get it from user input
        if idx == None:

            item_name = input(fmt_string(
                'Which item would you like to delete?[ID/Name]: ', fg='Blue')).lower()

            # Input handling, restart function loop if input is empty
            if len(item_name) == 0:
                res = input(fmt_string(
                    'You Must Enter An ID or Value\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                log('warning', f'No option selected')

                if res == 'n':
                    is_looping = False

                continue

            # Cancel condition
            if item_name == '0':
                return

            # Try to cast input to an int to be used as and index into the list
            try:
                index = int(item_name) - 1

                # Throw the IndexError before we actual cause it
                if index >= len(lst):
                    raise IndexError

            # If the input can't be cast to an int, then treat the input as a string to search the list
            except (ValueError, IndexError):
                if item_name not in lst:
                    res = input(fmt_string(
                        'That item can\'t be found!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                    log('warning', f'Item does not exist - {item_name}')

                    if res == 'n':
                        is_looping = False
                    continue

                # Is a match is found with the input as a string, get it's index
                index = lst.index(item_name)

        # Caller has provided index so set it
        else:
            index = idx

        log('info', f'{lst[index]} successfully deleted')

        # Finally delete the item from the list
        del lst[index]

        clear()
        print_list(lst)

        res = input(fmt_string(
            'Item Successfully Deleted.\nWould you like to delete another? [y/n]', fg='Green')).lower()

        if res == 'n':
            is_looping = False
            
        idx = None

    save_external_data(external_data)


def search(term, lists: list):
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

# TODO: This is a bit of a mess, clean it up!
def search_list(lst: list):
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

        # Display the results to the user in a more readable form - 1 table per list supplied
        for i, dtn in enumerate(results):
            print_list(dtn['items'], title=f'[{i+1}] {dtn["title"]}')

        print(
            f'\nResults Found: {fmt_string(count,fg="Green" if count > 0 else "Red" )}')

        if count < 1:
            input(fmt_string('Press "ENTER" to return to the previous menu', fg='Green'))
            print(results)
            return

        try:
            print(
                fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

            # If only one table contained a match set the table to access as the first one in the list, to prevent unneccasary input
            if len(results) != 1:
                list_option = input(fmt_string(
                    'Which Table Would You Like To Access[ID]: ', fg='Blue')).lower()

            else:
                list_option = 1

            # Cancel condition
            if list_option == '0':
                return

            # Try to cast input to an int to be used as an index into the results list
            list_index = int(list_option) - 1

            # Throw the IndexError before we actual cause it
            if list_index > len(results):
                raise IndexError

            # list that contains results as strings
            working_result_list = results[list_index]['items']
            # reference to the actual list object
            working_list = results[list_index]['list']

            item_option = input(fmt_string(
                'Which Item Would You Like To Access[ID]: ', fg='Blue')).lower()

            # Cancel condition
            if item_option == '0':
                return

            # Try to cast input to an int to be used as an index into the results list
            item_index = int(item_option) - 1

            # Throw the IndexError before we actual cause it
            if item_index > len(working_result_list):
                raise IndexError

            action_option = input(fmt_string(
                'Which Would You Like To Do?[(u)pdate, (d)elete, (v)iew]: ', fg='Blue')).lower()

            # Restrict input to only valid options
            if action_option not in action_options:
                raise ValueError

        except (ValueError, IndexError) as err:
            res = input(fmt_string(
                'Oops, That Wasn\'t A Valid Option!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

            if res == 'n':
                is_looping = False
            continue

        # Call relevent function based on option selected
        # results index likely is not list index, i.e. result index 4 may be list index 10 etc. so get actual index using .index()

        working_list_index = working_list.index(working_result_list[item_index])
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
