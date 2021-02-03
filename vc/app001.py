import os

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
    width = get_width(rows)
    width = width if len(name) < width else len(name)
    print_title(name, width)
    print_rows(rows, width)


def clear():
    os.system('clear')

# endregion


# region := App
# Menu structures as a list of options, with element 1 acting as the title
main_menu = ['Main Menu', '[1] Product Maintainance', '[0] Exit']

products_menu = ['Product Maintainance',
                 '[1] Show All Products', '[2] Create New Product',
                 '[3] Update Product', '[4] Delete Product', '[0] Return To Main Menu']

# Data
products = ['coke', 'coke zero', 'fanta', 'water', 'coffee', 'tea', 'milk', 'orange juice',
            'salad', 'wrap', 'cheese sandwich', 'tuna sandwich', 'quiche', 'burger', 'sushi', 'curry', ]


# Funtion to print a list of all products, capitalized with element number
def print_products_list():
    print_table('Product List', [
                f'[{i+1}] {name.title()}' for i, name in enumerate(products)])


# Functions to show menus to avoid excess branching
def show_product_menu():
    clear()
    print_table(products_menu[0], products_menu[1:])

    menu_option = input(fmt_string('Please Select An Option.\n', fg='Green'))

    # Return to main menu
    if menu_option == '0':
        show_main_main()

    # View all products
    elif menu_option == '1':
        clear()
        print_products_list()
        input(fmt_string('Press "ENTER" to return to the previous menu', fg='Green'))
        show_product_menu()

    # Add new product
    elif menu_option == '2':
        is_looping = True

        while is_looping:
            clear()
            print_products_list()
            product_name = input(fmt_string(
                'Product Name:\t', fg='Blue')).lower()

            if len(product_name) == 0:
                res = input(fmt_string(
                    'You Must Enter A Name\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                if res == 'n':
                    is_looping = False

                continue

            if product_name in products:
                res = input(fmt_string(
                    'That Product Already Exists.\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                if res == 'n':
                    is_looping = False

            else:
                products.append(product_name)
                res = input(fmt_string(
                    'New Product Successfully Added.\nWould you like to add another? [y/n]', fg='Green')).lower()

                if res == 'n':
                    is_looping = False

        show_product_menu()

    # Update product
    elif menu_option == '3':
        is_looping = True

        while is_looping:
            clear()
            print_products_list()

            old_name = input(
                fmt_string('Which product would you like to update?[ID/Name]: ', fg='Blue')).lower()

            if len(old_name) == 0:
                res = input(fmt_string(
                    'You Must Enter An ID or Name\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                if res == 'n':
                    is_looping = False

                continue

            try:
                index = int(old_name) - 1

                if index >= len(products):
                    raise IndexError

            except (ValueError, IndexError):

                if old_name not in products:
                    res = input(fmt_string(
                        'That product can\'t be found!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                    if res == 'n':
                        is_looping = False
                    continue

                index = products.index(old_name)

            new_name = input(
                fmt_string('What is the new value?:\t', fg='Blue')).lower()

            products[index] = new_name

            res = input(fmt_string(
                'Product Successfully Updated.\nWould you like to update another? [y/n]', fg='Green')).lower()

            if res == 'n':
                is_looping = False

        show_product_menu()

    # Delete product
    elif menu_option == '4':
        is_looping = True

        while is_looping:
            clear()
            print_products_list()

            product_name = input(fmt_string(
                'Which product would you like to delete?[ID/Name]: ', fg='Blue')).lower()

            if len(product_name) == 0:
                res = input(fmt_string(
                    'You Must Enter An ID or Name\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                if res == 'n':
                    is_looping = False

                continue

            try:
                index = int(product_name) - 1

                if index >= len(products):
                    raise IndexError

            except (ValueError, IndexError):
                if product_name not in products:
                    res = input(fmt_string(
                        'That product can\'t be found!\nWould you like to try again? [y/n]', fg='White', bg="Red")).lower()

                    if res == 'n':
                        is_looping = False
                    continue

                index = products.index(product_name)

            del products[index]

            res = input(fmt_string(
                'Product Successfully Deleted.\nWould you like to delete another? [y/n]', fg='Green')).lower()

            if res == 'n':
                is_looping = False

        show_product_menu()

    else:
        input(fmt_string(
            'That option was not recognised. Press "ENTER" key to try again', fg='White', bg='Red'))
        show_product_menu()


def show_main_main():
    clear()
    print(fmt_string('Hi and Welcome to the F&B Ordering System.', fg='Blue'))
    print_table(main_menu[0], main_menu[1:])

    menu_option = input(fmt_string('Please Select An Option.\n', fg='Green'))

    if menu_option == '0':
        exit()

    elif menu_option == '1':
        show_product_menu()

    else:
        input(fmt_string(
            'That option was not recognised. Press "ENTER" key to try again', fg='White', bg='Red'))
        show_main_main()


# Start Loop
while True:
    show_main_main()

# endregion App
