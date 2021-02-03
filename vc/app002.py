import os
import datetime

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


def log(type, msg, logfile='../data/log.txt'):
    
    try:
        with open(logfile, 'a') as file:
            file.write(
                f'{datetime.datetime.now()} @ {type.upper()}: {msg}' + '\n')
        
    except Exception as err:
        print(f'CRITICAL - Unable to create log: {str(err)}')
    
    
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
    width = get_width(rows)
    width = width if len(name) < width else len(name)
    print_title(name, width)
    print_rows(rows, width)


def clear():
    os.system('clear')


def load_list(filename, lst):
    try:
        with open(filename, 'r') as file:
            for item in file.readlines():
                item = item.strip()
                lst.append(item)
        log('info', f'{filename} successfully loaded')
    except Exception as err:
        log('error', f'Failed to load data - {str(err)}')


def save_list(filename, lst, mode='w'):
    try:
        with open(filename, mode) as file:
            for item in lst:
                file.write(item + '\n')
        log('info', f'data successfully saved to {filename}')
    except Exception as err:
        log('error', f'Failed to save data - {str(err)}')
        


# endregion

# region := App

# Data
products = []
couriers = []


def show_menu(menu_name):
    global menu_state
    menu_state = menu_name

    log('info', f'Menu {menu_name} loaded')

    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.', fg='Blue'))

    menu = menus[menu_name]
    print_table(menu['title'], menu['items'])

    try:
        menu_option = int(
            input(fmt_string('Please Select An Option.\n', fg='Green')))
        if menu_option > len(menu['handlers']):
            raise ValueError

    except ValueError as err:
        input(fmt_string(
            'That option was not recognised. Press "ENTER" key to try again', fg='White', bg='Red'))

        log('warning', f'Option not recognised - {str(err)}')
        return

    menu['handlers'][menu_option]()


def print_list(lst, title='All Items'):
    print_table(title, [
                f'[{i+1}] {name.title()}' for i, name in enumerate(lst)])


def print_list_view(lst):
    log('info', f'Menu print_list_view loaded')
    
    clear()
    print_list(lst)

    input(fmt_string('Press "ENTER" to return to the previous menu', fg='Green'))


def create_list_item(lst):
    is_looping = True

    while is_looping:
        log('info', f'Attempting to  create new item')
        
        clear()
        print_list(lst)
        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        item_name = input(fmt_string(
            'Item Name:\t', fg='Blue')).lower()

        if item_name == '0':
            return

        if len(item_name) == 0:
            res = input(fmt_string(
                'You Must Enter A Value\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

            log('warning', f'Option not recognised - {item_name}')

            if res == 'n':
                is_looping = False

            continue

        if item_name in lst:
            res = input(fmt_string(
                'That Item Already Exists.\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

            log('warning', f'Duplicate item - {item_name}')

            if res == 'n':
                is_looping = False

        else:
            lst.append(item_name)
            clear()
            print_list(lst)
            
            res = input(fmt_string(
                'New Item Successfully Added.\nWould you like to add another? [y/n]', fg='Green')).lower()
            
            log('info', f'New item added - {item_name}')

            if res == 'n':
                is_looping = False

    save_list('../data/products.txt', products)
    save_list('../data/couriers.txt', couriers)


def update_list_item(lst):
    is_looping = True

    while is_looping:
        log('info', f'Attempting to update item')
        
        clear()
        print_list(lst)
        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        old_value = input(
            fmt_string('Which item would you like to update?[ID/Name]: ', fg='Blue')).lower()

        if len(old_value) == 0:
            res = input(fmt_string(
                'You Must Enter An ID or Value\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()
            
            log('warning', f'No option selected')

            if res == 'n':
                is_looping = False

            continue

        if old_value == '0':
            return

        try:
            index = int(old_value) - 1

            if index >= len(lst):
                raise IndexError

        except (ValueError, IndexError) as err:

            if old_value not in lst:
                res = input(fmt_string(
                    'That Item can\'t be found!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()
                
                log('warning', f'Item does not exist - {old_value}')

                if res == 'n':
                    is_looping = False
                continue

            index = lst.index(old_value)

        new_value = input(
            fmt_string('What is the new value?:\t', fg='Blue')).lower()

        lst[index] = new_value
        
        clear()
        print_list(lst)

        res = input(fmt_string(
            'Item Successfully Updated.\nWould you like to update another? [y/n]', fg='Green')).lower()
        
        log('info', f'{old_value} updated - new value = {new_value}')

        if res == 'n':
            is_looping = False

    save_list('../data/products.txt', products)
    save_list('../data/couriers.txt', couriers)


def delete_list_item(lst):
    is_looping = True

    while is_looping:
        log('info', f'Attempting to delete item')
        
        clear()
        print_list(lst)
        print(
            fmt_string('Enter 0 to return to the previous menu!', fg='Green'))

        item_name = input(fmt_string(
            'Which item would you like to delete?[ID/Name]: ', fg='Blue')).lower()

        if len(item_name) == 0:
            res = input(fmt_string(
                'You Must Enter An ID or Value\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()
            
            log('warning', f'No option selected')

            if res == 'n':
                is_looping = False

            continue

        if item_name == '0':
            return

        try:
            index = int(item_name) - 1

            if index >= len(lst):
                raise IndexError

        except (ValueError, IndexError):
            if item_name not in lst:
                res = input(fmt_string(
                    'That item can\'t be found!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()
                
                log('warning', f'Item does not exist - {item_name}')

                if res == 'n':
                    is_looping = False
                continue

            index = lst.index(item_name)

        del lst[index]
        
        clear()
        print_list(lst)

        res = input(fmt_string(
            'Item Successfully Deleted.\nWould you like to delete another? [y/n]', fg='Green')).lower()
        
        log('info', f'{item_name} successfully deleted')

        if res == 'n':
            is_looping = False

    save_list('../data/products.txt', products)
    save_list('../data/couriers.txt', couriers)


menus = {
    'main_menu': {
        'title': 'Main Menu',
        'items': ['[0] Exit',
                  '[1] Product Maintainance',
                  '[2] Courier Maintainance'],
        'handlers': [exit,
                     lambda: show_menu('product_menu'),
                     lambda: show_menu('courier_menu')]
    },
    'product_menu': {
        'title': 'Product Maintainance',
        'items': ['[0] Return To Main Menu',
                  '[1] Show All Products',
                  '[2] Create New Product',
                  '[3] Update Product',
                  '[4] Delete Product'],
        'handlers': [lambda: show_menu('main_menu'),
                     lambda: print_list_view(products),
                     lambda: create_list_item(products),
                     lambda: update_list_item(products),
                     lambda: delete_list_item(products)]
    },
    'courier_menu': {
        'title': 'Courier Maintainance',
        'items': ['[0] Return To Main Menu',
                  '[1] Show All Couriers',
                  '[2] Create New Courier',
                  '[3] Update Courier',
                  '[4] Delete Courier'],
        'handlers': [lambda: show_menu('main_menu'),
                     lambda: print_list_view(couriers),
                     lambda: create_list_item(couriers),
                     lambda: update_list_item(couriers),
                     lambda: delete_list_item(couriers)]
    }
}


# Start Loop
menu_state = 'main_menu'

load_list('../data/products.txt', products)
load_list('../data/couriers.txt', couriers)

while menu_state:
    show_menu(menu_state)

else:
    save_list('../data/products.txt', products)
    save_list('../data/couriers.txt', couriers)

# endregion App
