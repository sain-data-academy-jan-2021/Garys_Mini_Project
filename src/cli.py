import os
from typing import Any
from terminaltables import SingleTable
from math import ceil

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

order_status = {
    'pending': 'Blue',
    'accepted': 'Cyan',
    'preparing': 'Yellow',
    'dispatched': 'Green',
    'cancelled': 'Red',
    'delivered': 'White',
}


def fmt_string(msg: str, fg: str = 'White', bg: str = 'Unset') -> str:
    return f'\u001b[{colors[fg]};1m\u001b[{colors[bg]+10};1m{msg}\u001b[0m'


def print_palette(col: str = 'All') -> None:

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
    print(f"    +{'-' * (width + 8)}+")


def print_row(row: str, width: int) -> None:

    if row != 'Separator':
        print(f"    |{row}{' ' * (width - len(str(row)) + 7)} |")
    else:
        print_outline(width)


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
        return max(len(str(row)) for row in rows)

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


def validated_input(prompt: str, *types, **options) -> tuple[int, Any]:
    cancel_text = ''

    if 'cancel_on' in options:
        if options['cancel_on'] == '':
            options['cancel_on'] = 'BLANK'

    if 'cancel_on' in options and 'cancel_text' in options:
        cancel_text = fmt_string(
            f'({options["cancel_on"]} To {options["cancel_text"].title()})\n', fg='White')

    elif 'cancel_on' in options:
        cancel_text = fmt_string(
            f'({options["cancel_on"]} To Cancel)\n', fg='White')

    prompt += cancel_text

    if 'fg' in options:
        value = str(
            input(fmt_string(prompt, fg=options['fg']))).lower()

    elif 'bg' in options:
        value = str(input(fmt_string(prompt, fg=options['bg']))).lower()

    elif 'fg' in options and 'bg' in options:
        value = str(
            input(fmt_string(prompt, fg=options['fg'], bg=options['bg']))).lower()

    else:
        value = str(input(fmt_string(prompt))).lower()

    if 'cancel_on' in options:
        if value == options['cancel_on']:
            return -1, 'Operation Cancelled'

    if float in types:
        try:
            value = float(value)

            if 'max_value' in options:
                if value > options['max_value']:
                    return 0, fmt_string(f'Input [{value}] was greater than than allowed value [{options["max_value"]}]', fg='White', bg='Red')

            if 'min_value' in options:
                if value < options['min_value']:
                    return 0, fmt_string(f'Input [{value}] was less than than allowed value [{options["min_value"]}]', fg='White', bg='Red')

        except ValueError:
            if str not in types and int not in types:
                return 0, fmt_string(f'Input type ({str(type(value))}) is not one of the valid input type {str(types)}', fg='White', bg='Red')

    if int in types:
        try:
            value = int(value)

            if 'max_value' in options:
                if value > options['max_value']:
                    return 0, fmt_string(f'Input [{value}] was greater than than allowed value [{options["max_value"]}]', fg='White', bg='Red')

            if 'min_value' in options:
                if value < options['min_value']:
                    return 0, fmt_string(f'Input [{value}] was less than than allowed value [{options["min_value"]}]', fg='White', bg='Red')

        except ValueError:
            if str not in types:
                return 0, fmt_string(f'Input type ({str(type(value))}) is not one of the valid input type {str(types)}', fg='White', bg='Red')

    if 'unique' in options:
        if value in options['unique']:
            return 0, fmt_string(f'Input value {value} is already present in object', fg='White', bg='Red')

    if 'is_present' in options:
        if value not in options['is_present']:
            return 0, fmt_string(f'Input value {value} can not be found in object', fg='White', bg='Red')

    if 'min_length' in options:
        if len(str(value)) < options['min_length']:
            return 0, fmt_string(f'Length of input [{len(str(value))}] is less than the minimum length [{options["min_length"]}]', fg='White', bg='Red')

    if 'max_length' in options:
        if len(str(value)) > options['max_length']:
            return 0, fmt_string(f'Length of input [{len(str(value))}] is greater than the maximum length [{options["max_length"]}]', fg='White', bg='Red')

    return 1, value


def get_validated_input(prompt: str, *types, **options) -> Any:
    # Wrapper For validated_input to allow looping until valid
    res, value = validated_input(prompt, *types, **options)

    while res != 1:

        if res == -1:
            return False

        res, value = validated_input(prompt, *types, **options)

    return value


def dicts_to_table(dicts: list[dict[Any, Any]], headers: list = [], enumerated=False, paginate=False) -> None:
    table_data = []
    show_headers = []
    if enumerated:
        show_headers.append('ID')

    if headers == []:
        for key in dicts[0].keys():
            if key != 'items' and key != 'courier':
                show_headers.append(key.title())
    else:
        for hdr in headers:
            if hdr != 'items' and hdr != 'courier':
                show_headers.append(hdr.title())

    table_data.append(show_headers)

    for i, dtn in enumerate(dicts):
        if dtn != {}:
            row = []
            if enumerated:
                row.append(i+1)
            for key, value in dtn.items():

                if key == 'status':
                    row.append(fmt_string(
                        value.title(), fg=order_status[value]))
                elif key != 'items' and key != 'courier':
                    if type(value) == float:
                        row.append('%.2f' % value)
                    else:
                        row.append(str(value).title())

            table_data.append(row)

    is_looping = True
    total_records = len(table_data)
    page_length = 20
    current_page = 0
    total_pages = ceil(int(total_records / page_length))

    if paginate and total_pages > 0:
        while is_looping:
            clear()
            to = (current_page * page_length + page_length + 1) if (current_page *
                                                                    page_length + page_length + 1) < total_records else total_records
            page_slice = []
            page_slice.append(table_data[0])
            page_slice += table_data[current_page *
                                    page_length + 1:to]
            table = SingleTable(page_slice)

            table_width = table.table_width
            fixed_text_width = 40
            width_to_fill = table_width - fixed_text_width

            print(table.table)
            print(fmt_string(
                f'Showing Records {current_page * page_length + 1}-{to} Of {total_records}{" " * width_to_fill} Page {current_page+1} of {total_pages + 1}  ', bg='Blue', fg='White'))
            
            option = input('[+/-] For Next/Previous Page\n').lower()
            
            if option in ['', '+', '-']:
                if option == '':
                    is_looping = False
                elif option == '+':
                    if current_page < total_pages:
                        current_page += 1
                elif option == '-':
                    if current_page > 0:
                        current_page -= 1
    else:
        table = SingleTable(table_data)
        print(table.table)


def list_to_table(lst: list[str], title: str, **options) -> None:
    table_data = []
    lst = [item.title() for item in lst]

    if 'max_length' in options:
        max_length = options['max_length']
    else:
        max_length = 20

    no_cols = ceil(len(lst) / max_length)
    split_lst = []

    for i in range(0, len(lst), no_cols):
        sub_list = lst[i:i + no_cols]

        if 'enumerate' in options:
            if options['enumerate']:
                for idx, _ in enumerate(sub_list):
                    sub_list[idx] = f' [{i + idx + 1}] {sub_list[idx]}'

        split_lst.append(sub_list)

    for sub in split_lst:
        table_data.append(sub)

    # for i, item in enumerate(lst):
    #     table_data.append([i+1, item])
    table = SingleTable(table_data, title.upper())
    table.inner_heading_row_border = False
    print(table.table)
