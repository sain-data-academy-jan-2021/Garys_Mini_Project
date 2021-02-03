import json
from typing import Any
from PyInquirer import prompt, Separator
from modules.cli import (
    clear,
    dicts_to_table,
    fmt_string,
    list_to_table,
    print_table,
    validated_input,
    order_status,
)
from modules.file_system import load_json, load_list, save_json, save_list, log

title_width = 35


def sort_orders_by_status():
    orders = get_external_data("orders")
    for i in range(len(orders)):
        for j in range(len(orders) - 1):
            status_index1 = list(order_status.keys()).index(orders[j]["status"])
            status_index2 = list(order_status.keys()).index(orders[j + 1]["status"])
            if status_index1 > status_index2:
                orders[j], orders[j + 1] = orders[j + 1], orders[j]


def load_external_data(data: dict[str, Any]) -> None:
    for data_source in data.values():
        if "location" in data_source:
            if "type" not in data_source:
                load_list(data_source["location"], data_source["data"])
            else:
                if data_source["type"] == "json":
                    data_source["data"] = load_json(data_source["location"])


def save_external_data(data: dict[str, Any]) -> None:
    for data_source in data.values():
        if "location" in data_source:
            if "type" not in data_source:
                save_list(data_source["location"], data_source["data"])
            else:
                if data_source["type"] == "json":
                    save_json(data_source["location"], data_source["data"])


def get_external_data(key: str, attr: str = "data") -> Any:
    global external_data
    return external_data[key][attr]


def update_order_references(name: str, index: int):
    log("debug", f"Attempting To Update Order references For {name}")
    orders = get_external_data("orders")

    if name == "products":
        for order in orders:
            data = order["items"]

            for i, el in enumerate(data):
                if el == index:
                    data[i] = -1

                elif el > index:
                    data[i] -= 1

        # update catagory_mapping
        catagories = get_external_data("catagory_mapping")
        for catagory in catagories:
            for i, item in reversed(list(enumerate(catagories[catagory]))):
                print(item)
                if index == item:
                    del catagories[catagory][i]
                elif item > index:
                    catagories[catagory][i] -= 1

    if name == "couriers":
        for order in orders:
            value = order["courier"]
            if value == index:
                order["courier"] = -1

            elif value > index:
                order["courier"] -= 1


def show_menu(menu_name: str) -> None:
    # Set the global menu_state to the selected menu to allow us to backtrack when returning
    global menu_state
    menu_state = menu_name

    log("debug", f"Menu {menu_name} loaded")

    clear()
    print(fmt_string("Hi and Welcome to the F&B Ordering System.", fg="Blue"))

    # Get the menu structure from the menus object, using it's items value to print to the screen
    menu = menus[menu_name]
    print_table(menu["title"], menu["items"])

    if (
        menu_option := validated_input(
            "Please Select An Option.\n",
            int,
            fg="Green",
            max_value=len(menu["handlers"]) - 1,
        )
    )[0] == 0:
        log("debug", menu_option[1])
        input(menu_option[1])
        return

    # Call the function associated with the selected menu item
    menu["handlers"][menu_option[1]]()


def print_list(lst: list[Any], title: str = "All Items", add_id: bool = True) -> None:
    # Wrapper for print_table, to allow us to print the each items index number beside its name
    # print_table(
    #     title, [f'[{i+1}] {name.title()}' for i, name in enumerate(lst)])
    list_to_table(lst, title, enumerate=add_id)


def print_list_view(key: str) -> None:
    # Wrapper for print_list to allow it to be used as it's own menu 'page'
    lst = get_external_data(key)
    log("debug", f"Menu print_list_view loaded")

    clear()
    print_list(lst, f"All {key}", add_id=False)

    input(fmt_string('Press "ENTER" to return to the previous menu', fg="Green"))


def create_list_item(key: str) -> None:
    lst = get_external_data(key)

    is_looping = True

    # Loop until the user decides otherwise, to provide us to add multiple items or reset after invalid input
    while is_looping:
        log("info", f"Attempting to create new item")

        clear()
        print_list(lst)
        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))

        res, value = validated_input(
            "Item Name:\t", str, fg="Blue", min_length=1, unique=lst
        )

        if res == 0:
            if (
                _ := input(
                    f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", value)
                is_looping = False
            continue

        # Cancel Condition
        if value == "0":
            return

        lst.append(value)
        log("info", f"New item added - {value}")

        clear()
        print_list(lst)

        if (
            _ := input(
                fmt_string(
                    "New Item Successfully Added.\nWould you like to add another? [y/n]",
                    fg="Green",
                )
            ).lower()
        ) == "n":
            is_looping = False

    save_external_data(external_data)


def update_list_item(key: str, idx: Any = None) -> None:
    lst = get_external_data(key)

    is_looping = True

    # Loop until the user decides otherwise, to provide us to update multiple items or reset after invalid input
    while is_looping:
        index = None
        log("info", f"Attempting to update item")

        clear()
        print_list(lst)
        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))

        # If the caller has not provided an index then get this as input from the user
        if idx == None:

            res, old_value = validated_input(
                "Which item would you like to update?[ID/Name]: ",
                int,
                str,
                fg="Blue",
                max_value=len(lst),
                min_length=1,
                is_present=lst,
            )

            if res == 0:
                if (
                    _ := input(
                        f'{old_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                    ).lower()
                ) == "n":
                    log("debug", old_value)
                    is_looping = False
                continue

            # Cancel condition
            if old_value == 0:
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
            "What is the new value?:\t", str, fg="Blue", unique=lst
        )

        if res == 0:
            if (
                _ := input(
                    f'{new_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", new_value)
                is_looping = False
            continue

        # Finally update the value and check for reset or return
        log("info", f"{lst[index]} updated - new value = {new_value}")
        lst[index] = new_value

        clear()
        print_list(lst)

        if (
            _ := input(
                fmt_string(
                    "New Item Successfully Updated.\nWould you like to add another? [y/n]",
                    fg="Green",
                )
            ).lower()
        ) == "n":
            is_looping = False

        idx = None

    save_external_data(external_data)


def delete_list_item(key: str, idx: Any = None) -> None:
    lst = get_external_data(key)
    lst_name = get_external_data(key, "name")

    is_looping = True
    # Loop until the user decides otherwise, to provide us to update multiple items or reset after invalid input
    while is_looping:
        index = None
        log("info", f"Attempting to delete item")

        clear()
        print_list(lst)
        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))

        # If the caller doen't provide an item index, get it from user input
        if idx == None:

            res, item_name = validated_input(
                "Which item would you like to delete?[ID/Name]: ",
                int,
                str,
                fg="Blue",
                max_value=len(lst),
                min_length=1,
                is_present=lst,
            )

            if res == 0:
                if (
                    _ := input(
                        f'{item_name}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                    ).lower()
                ) == "n":
                    log("debug", item_name)
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
        log("info", f"{lst[index]} successfully deleted")
        del lst[index]
        update_order_references(lst_name, index)

        clear()
        print_list(lst)

        if (
            _ := input(
                fmt_string(
                    f"Item Successfully Deleted.\nWould you like to delete another? [y/n]",
                    fg="Green",
                )
            ).lower()
        ) == "n":
            is_looping = False

        idx = None

    save_external_data(external_data)


def search(term: str, lists: list[Any]) -> list[dict[str, Any]]:
    results = []

    # Create a dictionary for each list passed to store the results from each
    for lst in lists:
        dtn = {
            "title": lst,
            # Reference to actual list object to allow future function calls
            "list": external_data[lst]["data"],
            "items": [],
        }

        items = []

        # Loop through list, if a match is found add it to the items list. Note an empty string returns all items
        for item in external_data[lst]["data"]:
            if term in item:
                items.append(item)

            dtn["items"] = items

        results.append(dtn)
    return results


def search_list(lst: list[Any]) -> None:
    clear()
    action_options = ["u", "d", "v", "0"]

    search_term = input(fmt_string("please enter a seach term.", fg="Blue")).lower()

    is_looping = True
    while is_looping:

        results = search(search_term, lst)

        clear()
        count = 0  # To display number of results found to user

        # Loop through the results removing any lists thats didn't not contain a match
        # This is enumerated to allow us access to the list index and revesed to deal with shifting after a del
        for i, dtn in reversed(list(enumerate(results))):
            items = dtn["items"]
            count += len(items)

            if len(items) < 1:
                del results[i]

        # Display the results to the user in a more readable form - 1 table per list supplied with ID number
        for i, dtn in enumerate(results):
            print_list(dtn["items"], title=f'[{i+1}] {dtn["title"]}')

        print(
            f'\nResults Found: {fmt_string(str(count),fg="Green" if count > 0 else "Red" )}'
        )

        if count < 1:
            input(
                fmt_string('Press "ENTER" to return to the previous menu', fg="Green")
            )
            print(results)
            return

        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))

        # If only one table contained a match set the table to access as the first one in the list, to prevent unneccasary input
        if len(results) != 1:
            res, list_option = validated_input(
                "Which Table Would You Like To Access[ID]: ",
                int,
                fg="Blue",
                max_value=len(results),
            )
            if res == 0:
                if (
                    _ := input(
                        f'{list_option}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                    ).lower()
                ) == "n":
                    log("debug", list_option)
                    is_looping = False
                continue

            # Cancel condition
            if list_option == 0:
                return

            list_index = list_option - 1

        else:
            list_index = 0

        # list that contains results as strings
        working_result_list = results[list_index]["items"]
        # reference to the actual list object
        working_list = results[list_index]["list"]

        res, item_option = validated_input(
            "Which Item Would You Like To Access[ID]: ",
            int,
            fg="Blue",
            max_value=len(working_result_list),
        )

        if res == 0:
            if (
                _ := input(
                    f'{item_option}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", item_option)
                is_looping = False
            continue

        # Cancel condition
        if item_option == 0:
            return

        item_index = item_option - 1

        res, action_option = validated_input(
            "Which Would You Like To Do?[(u)pdate, (d)elete, (v)iew]: ",
            str,
            fg="Blue",
            min_length=1,
            max_length=1,
            is_present=action_options,
        )

        if res == 0:
            if (
                _ := input(
                    f'{action_option}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", action_option)
                is_looping = False
            continue

        # Cancel condition
        if action_option == 0:
            return

        # Call relevent function based on option selected
        # results index likely is not list index, i.e. result index 4 may be list index 10 etc. so get actual index using .index()
        working_list_index = working_list.index(working_result_list[item_index])
        working_list_key = results[list_index]["title"]

        if action_option == "u":
            update_list_item(working_list_key, idx=working_list_index)

        elif action_option == "d":
            delete_list_item(working_list_key, idx=working_list_index)

        elif action_option == "0":
            return

        else:
            print_list_view(working_list_key)


# TODO: Add update/delete option from this screen OR full menu from this screen??
def view_order_details(index: int):
    clear()
    print(f'\n{" " * title_width} Viewing Order {index + 1} {" " * title_width}\n')

    for key, value in get_external_data("orders")[index].items():

        if key == "courier":
            idx = int(value)
            if idx < 0:
                print(
                    f'{fmt_string(f"{key.title()}: ",fg="Blue")} {fmt_string("Unassigned", fg="Red")}'
                )
            else:
                courier = get_external_data("couriers")[idx]
                print(f'{fmt_string(f"{key.title()}: ",fg="Blue")} {courier.title()}')

        elif key == "status":
            print(
                f'{fmt_string(f"{key.title()}: ",fg="Blue")} {fmt_string(value.title(),fg=order_status[value])}'
            )

        elif key != "items":
            print(f'{fmt_string(f"{key.title()}: ",fg="Blue")} {value}')

        else:
            table_data = []
            for item in value:
                if item != -1:
                    table_data.append(get_external_data("products")[item].title())
                    # print(f'\t{get_external_data("products")[item].title()}')
                else:
                    table_data.append("Item Deleted")
                    # print(fmt_string('\tItem Deleted', fg='Red'))
            list_to_table(summerise_list(table_data), "Current Order")

        print()

    input(fmt_string('Press "ENTER" to return to the previous menu', fg="Green"))


def view_orders() -> None:
    orders_data = get_external_data("orders")
    is_looping = True
    set_filter = "clear filter_all"

    while is_looping:
        clear()
        print(
            f'\n{" " * title_width} Viewing Orders {" - FILTER [" + set_filter.title() + "]" if set_filter != "clear filter_all" else ""} {" " * title_width}\n'
        )

        if set_filter == "clear filter_all":
            dicts_to_table(orders_data)
        else:
            res = []
            for order in orders_data:
                filter_on = set_filter.split("_")
                if filter_on[1] in order[filter_on[0]]:
                    res.append(order)
                else:
                    res.append({})

            dicts_to_table(res, headers=list(orders_data[0].keys()))

        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))
        res, value = validated_input(
            "Select An Order To View [ID] Or Filter [-1]: ",
            int,
            fg="Green",
            min_value=-1,
            min_length=1,
            max_value=len(orders_data),
        )

        if res == 0:
            if (
                _ := input(
                    f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", value)
                is_looping = False
            continue

        # Cancel condition
        if value == 0:
            return

        if value == -1:
            filter_options = [
                {
                    "type": "list",
                    "name": "filter_type",
                    "message": "Which Key Would You Like To Filter On",
                    "choices": [
                        "Clear Filter",
                        Separator(),
                        "Name",
                        "Address",
                        "Area",
                        "Number",
                        "Status",
                    ],
                    "filter": lambda val: val.lower(),
                }
            ]

            filter_type = prompt(filter_options)

            if filter_type["filter_type"] == "clear filter":
                filter_on_value = "all"

            elif filter_type["filter_type"] != "status":
                filter_on_value = input("What Is Your Filter Term: ")

            else:
                on_options = [
                    {
                        "type": "list",
                        "name": "filter_on",
                        "message": "Which Key Would You Like To Filter On",
                        "choices": [status.title() for status in order_status.keys()],
                        "filter": lambda val: val.lower(),
                    }
                ]

                filter_on_value_itd = prompt(on_options)
                filter_on_value = filter_on_value_itd["filter_on"]

            set_filter = filter_type["filter_type"] + "_" + filter_on_value
            continue

        index = value - 1

        view_order_details(index)


def create_order() -> None:
    current_orders = get_external_data("orders")
    is_looping = True

    while is_looping:

        clear()
        print(f'\n{" " * title_width} Create New Order {" " * title_width}\n')
        dicts_to_table(current_orders)
        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))

        res, name_value = validated_input(
            "Customer Name?: ", str, fg="Blue", min_length=1
        )

        if res == 0:
            if (
                _ := input(
                    f'{name_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", name_value)
                is_looping = False
            continue

        # Cancel condition
        if name_value == "0":
            return

        res, address_value = validated_input("Address?: ", str, fg="Blue")

        if res == 0:
            if (
                _ := input(
                    f'{address_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", address_value)
                is_looping = False
            continue

        # Cancel condition
        if address_value == "0":
            return

        res, area_value = validated_input("Postcode?: ", str, fg="Blue")

        if res == 0:
            if (
                _ := input(
                    f'{area_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", area_value)
                is_looping = False
            continue

        # Cancel condition
        if area_value == "0":
            return

        res, phone_value = validated_input("Contact Number?: ", str, fg="Blue")

        if res == 0:
            if (
                _ := input(
                    f'{phone_value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", phone_value)
                is_looping = False
            continue

        # Cancel condition
        if phone_value == "0":
            return

        items = select_order_items()

        current_orders.append(
            {
                "name": name_value.lower(),
                "address": address_value.lower(),
                "area": area_value.lower(),
                "number": phone_value,
                "courier": -1,
                "status": "pending",
                "items": items,
            }
        )

        clear()
        sort_orders_by_status()
        dicts_to_table(current_orders)

        if (
            _ := input(
                fmt_string(
                    f"Order Successfully Created.\nWould you like to add another? [y/n]",
                    fg="Green",
                )
            ).lower()
        ) == "n":
            is_looping = False


def update_status(index=None) -> None:
    orders_data = get_external_data("orders")

    is_looping = True
    while is_looping:
        clear()
        print(f'\n{" " * title_width} Update Order Status {" " * title_width}\n')
        dicts_to_table(orders_data)
        print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))

        res, value = validated_input(
            "Please Enter An ID To Update[ID]: ",
            int,
            fg="Blue",
            min_length=1,
            max_value=len(orders_data),
            min_value=0,
        )

        if orders_data[value - 1]["courier"] == -1:
            choices = ["CANCEL", Separator()]
            questions = [
                {
                    "type": "list",
                    "name": "courier",
                    "message": "No Courier Assigned! Please Update Before Updating Status",
                    "choices": choices
                    + [val.title() for val in get_external_data("couriers")],
                    "filter": lambda val: val.lower(),
                }
            ]

            answers = prompt(questions)

            if answers["courier"].lower() == "cancel":
                continue

            orders_data[value - 1]["courier"] = get_external_data("couriers").index(
                answers["courier"]
            )

        if res == 0:
            if (
                _ := input(
                    f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                ).lower()
            ) == "n":
                log("debug", value)
                is_looping = False
            continue

        if value == 0:
            return

        questions = [
            {
                "type": "list",
                "name": "status",
                "message": f'What Is The New Status?({orders_data[value -1]["status"].title()})',
                "choices": [val.title() for val in order_status],
                "filter": lambda val: val.lower(),
            }
        ]

        answers = prompt(questions)
        orders_data[value - 1]["status"] = answers["status"]
        sort_orders_by_status()


def update_order(index=None) -> None:
    orders_data = get_external_data("orders")
    is_looping = True

    while is_looping:
        sort_orders_by_status()
        if index == None:
            clear()
            print(f'\n{" " * title_width} Update Order {" " * title_width}\n')
            dicts_to_table(orders_data)
            print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))
            res, value = validated_input(
                "Select An Order To Update[ID] ",
                int,
                fg="Green",
                min_value=0,
                min_length=1,
                max_value=len(orders_data),
            )

            if res == 0:
                if (
                    _ := input(
                        f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                    ).lower()
                ) == "n":
                    log("debug", value)
                    is_looping = False
                continue

            # Cancel condition
            if value == 0:
                return

            idx = value - 1
        else:
            idx = index

        clear()
        print(f'\n{" " * title_width} Updating Order {idx + 1} {" " * title_width}\n')

        dicts_to_table([get_external_data("orders")[idx]])

        print(fmt_string("\nPress ENTER to skip field", fg="Green"))

        for key, value in get_external_data("orders")[idx].items():

            if key == "courier":
                current_courier = get_external_data("couriers")[int(value)]
                choices = []
                choices.append("SKIP")
                choices.append(Separator())
                for name in get_external_data("couriers"):
                    choices.append(name.title())

                update_courier = [
                    {
                        "type": "list",
                        "name": "courier",
                        "message": f"Update Courier ({current_courier.title()}): ",
                        "choices": choices,
                        "filter": lambda val: val.lower(),
                    }
                ]
                answer = prompt(update_courier)

                if answer["courier"].lower() != "skip":
                    orders_data[idx][key] = get_external_data("couriers").index(
                        answer["courier"]
                    )

            elif key == "status":
                current_status = orders_data[idx]["status"]
                choices = []
                choices.append("SKIP")
                choices.append(Separator())
                for status in order_status.keys():
                    choices.append(status.title())

                update_status = [
                    {
                        "type": "list",
                        "name": "status",
                        "message": f"Update Status ({current_status.title()}): ",
                        "choices": choices,
                        "filter": lambda val: val.lower(),
                    }
                ]
                answer = prompt(update_status)

                if answer["status"].lower() != "skip":
                    orders_data[idx][key] = answer["status"].lower()

            elif key != "items":
                res, val = validated_input(f"Update {key.title()}?: ", str, fg="Blue")

                if val != "":
                    orders_data[idx][key] = val

            else:
                print(f'{fmt_string(f"Order: ",fg="Blue")}')
                new_items = select_order_items(value)
                orders_data[idx][key] = new_items

        clear()
        print(f'\n{" " * title_width} Update Order {idx + 1} {" " * title_width}\n')
        dicts_to_table([get_external_data("orders")[idx]])
        input(
            fmt_string(
                'Order Successfully Updated.\nPress "ENTER" to return to the previous menu',
                fg="Green",
            )
        )


def delete_order(index=None) -> None:
    orders_data = get_external_data("orders")
    is_looping = True

    while is_looping:
        if index == None:
            clear()
            print(f'\n{" " * title_width} Delete Order {" " * title_width}\n')
            dicts_to_table(orders_data)
            print(fmt_string("Enter 0 to return to the previous menu!", fg="Green"))
            res, value = validated_input(
                "Please select an order to delete[ID]: ",
                int,
                fg="Blue",
                min_length=1,
                min_value=0,
                max_value=len(orders_data),
            )

            if res == 0:
                if (
                    _ := input(
                        f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                    ).lower()
                ) == "n":
                    log("debug", value)
                    is_looping = False
                continue

            if value == 0:
                return

            idx = value - 1
        else:
            idx = index

        log("info", f"Order Deleted - {json.dumps(orders_data[idx])}")
        del orders_data[idx]
        clear()
        dicts_to_table(orders_data)
        if (
            _ := input(
                fmt_string(
                    f"Order Successfully Deleted.\nWould you like to delete another? [y/n]",
                    fg="Green",
                )
            ).lower()
        ) == "n":
            is_looping = False


def select_order_items(current_order: list = []) -> list[int]:
    is_looping = True

    while is_looping:
        clear()
        current_items = [
            get_external_data("products")[index].title() for index in current_order
        ]
        list_to_table(summerise_list(current_items), "Current Order")

        update_type_question = {
            "type": "list",
            "message": "Please select an action",
            "name": "type",
            "choices": ["DONE", Separator(), "Add", "Remove"],
            "filter": lambda val: val.lower(),
        }

        update_type_answer = prompt(update_type_question)

        if update_type_question["type"].lower() == "done":
            is_looping = False
            continue

        if update_type_answer["type"] == "add":
            loop_cat = True
            while loop_cat:
                choices = []
                choices.append("BACK")
                choices.append(Separator())
                for key in get_external_data("catagory_mapping").keys():
                    choices.append(key.title())

                catagory_choice_question = {
                    "type": "list",
                    "message": "Please select a catagory",
                    "name": "catagory",
                    "choices": choices,
                    "filter": lambda val: val.lower(),
                }

                catagory_choice_answer = prompt(catagory_choice_question)

                if catagory_choice_answer["catagory"].lower() == "back":
                    loop_cat = False
                    continue

                loop_items = True
                while loop_items:
                    clear()
                    list_to_table(
                        summerise_list(
                            [
                                get_external_data("products")[index].title()
                                for index in current_order
                            ]
                        ),
                        "Current Order",
                    )

                    choices = ["Back", Separator()]
                    for index in get_external_data("catagory_mapping")[
                        catagory_choice_answer["catagory"]
                    ]:
                        item_name = get_external_data("products")[index].title()
                        choices.append(item_name)

                    item_choice_question = {
                        "type": "list",
                        "message": "Please select items to add",
                        "name": "items",
                        "choices": choices,
                    }

                    items_choice_answers = prompt(item_choice_question)

                    if items_choice_answers["items"] == "Back":
                        loop_items = False
                        continue

                    current_order.append(
                        get_external_data("products").index(
                            items_choice_answers["items"].lower()
                        )
                    )

        elif update_type_answer["type"] == "remove":

            if len(current_order) == 0:
                continue

            choices = []
            for item in current_items:
                choices.append({"name": item})
            choices = sorted(choices, key=lambda k: k["name"])
            item_choice_question = {
                "type": "checkbox",
                "message": "Please select items to delete",
                "name": "items",
                "choices": choices,
            }

            items_choice_answers = prompt(item_choice_question)
            list_to_remove = items_choice_answers["items"]

            for item in list(set(list_to_remove)):
                current_items.remove(item)
                current_order.remove(get_external_data("products").index(item.lower()))

        else:
            is_looping = False

    return current_order


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


###### Adjacent To Mini Project ########
def update_group_items(working_group: str) -> list[int]:
    clear()
    print(
        f'\n{" " * title_width} Updating Menu Group - {working_group.title()} {" " * title_width}\n'
    )

    working_list_indexs = get_external_data("catagory_mapping")[working_group]
    working_list_items = [
        get_external_data("products")[i].title() for i in working_list_indexs
    ]
    list_to_table(working_list_items, "Current Items")
    print()

    menu_to_update_question = {
        "type": "list",
        "message": "What Would You Like To Do: ",
        "name": "edit_type",
        "choices": ["RETURN", Separator(), "Add To Group", "Remove From Group"],
        "filter": lambda val: val.lower(),
    }

    edit_type = prompt(menu_to_update_question)["edit_type"]

    result = []
    if edit_type == "return":
        return result

    elif edit_type == "add to group":
        is_adding = True
        while is_adding:
            clear()
            print(
                f'\n{" " * title_width} Adding To Menu Group - {working_group.title()} {" " * title_width}\n'
            )
            list_to_table(
                [product.title() for product in get_external_data("products")],
                "All Items",
                enumerate=True,
            )

            # TODO: Select Item, get its ID And Add To Group with key working_group
            res, value = validated_input(
                f"Please Select An Option: (ID To Add, -1 To Search, 0 To Exit)\n",
                int,
                min_value=-1,
                max_value=len(get_external_data("products")),
            )

            if res == 0:
                if (
                    _ := input(
                        f'{value}\n{fmt_string("Would you like to try again? [y/n]", fg="White", bg="Red")}'
                    ).lower()
                ) == "n":
                    log("debug", value)
                    is_adding = False
                continue

            if value == 0:
                is_adding = False
                continue

    else:

        # TODO: Show working_list_items, get id to remove and remove from group with key working_group

        pass

    return result


def update_menu_group() -> None:
    clear()
    print(f'\n{" " * title_width} Update Menu Group {" " * title_width}\n')

    list_to_table(get_external_data("catagory_mapping"), "Current Groups", max_length=3)
    print()

    choices = [
        group.title() for group in list(get_external_data("catagory_mapping").keys())
    ]

    menu_to_update_question = {
        "type": "list",
        "message": "Which Menu Group Would You Like To Update: ",
        "name": "menu",
        "choices": ["Add New Group", Separator()] + choices,
        "filter": lambda val: val.lower(),
    }

    working_group = prompt(menu_to_update_question)["menu"]

    if working_group == "add new group":
        pass
    else:
        result = update_group_items(working_group)

print('test')
external_data = load_json("../data/config.json")
load_external_data(external_data)

menus = {
    "main_menu": {
        "title": "Main Menu",
        "items": [
            "[0] Exit",
            "[1] Product Maintainance",
            "[2] Courier Maintainance",
            "[3] Order Maintainance",
            "[4] Search",
            "Separator",
            "[5] System Maintainance",
        ],
        "handlers": [
            exit,
            lambda: show_menu("product_menu"),
            lambda: show_menu("courier_menu"),
            lambda: show_menu("orders"),
            lambda: search_list([lst for lst in external_data]),
            lambda: show_menu("system_maintainance_menu"),
        ],
    },
    "product_menu": {
        "title": "Product Maintainance",
        "items": [
            "[0] Return To Main Menu",
            "[1] Show All Products",
            "[2] Create New Product",
            "[3] Update Product",
            "[4] Delete Product",
            "[5] Search",
        ],
        "handlers": [
            lambda: show_menu("main_menu"),
            lambda: print_list_view("products"),
            lambda: create_list_item("products"),
            lambda: update_list_item("products"),
            lambda: delete_list_item("products"),
            lambda: search_list(["products"]),
        ],
    },
    "courier_menu": {
        "title": "Courier Maintainance",
        "items": [
            "[0] Return To Main Menu",
            "[1] Show All Couriers",
            "[2] Create New Courier",
            "[3] Update Courier",
            "[4] Delete Courier",
            "[5] Search",
        ],
        "handlers": [
            lambda: show_menu("main_menu"),
            lambda: print_list_view("couriers"),
            lambda: create_list_item("couriers"),
            lambda: update_list_item("couriers"),
            lambda: delete_list_item("couriers"),
            lambda: search_list(["couriers"]),
        ],
    },
    "orders": {
        "title": "Manage Orders",
        "items": [
            "[0] Return To Main Menu",
            "[1] View Current Orders",
            "[2] Create New Order",
            "[3] Update Status",
            "[4] Update Order",
            "[5] Delete Order",
        ],
        "handlers": [
            lambda: show_menu("main_menu"),
            view_orders,
            create_order,
            update_status,
            update_order,
            delete_order,
        ],
    },
    "system_maintainance_menu": {
        "title": "System Maintainance",
        "items": ["[0] Return To Main Menu", "[1] Update Menu Grouping"],
        "handlers": [lambda: show_menu("main_menu"), update_menu_group],
    },
}

# Start Loop
menu_state = "main_menu"

while menu_state:
    show_menu(menu_state)
    save_external_data(external_data)

# endregion App
