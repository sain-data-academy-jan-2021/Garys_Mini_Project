import datetime
from pathlib import Path
from typing import Any
import json
from csv import DictReader, DictWriter

base_path = Path(__file__).parent.parent


def get_absolute_path(filepath: Any = '') -> Any:
    if type(filepath) != str:
        return TypeError

    return (base_path / filepath).resolve()


def log(type: str, msg: str, logfile: Path = get_absolute_path('../data/log.log')) -> None:

    try:
        with open(logfile, 'a') as file:
            file.write(
                f'{datetime.datetime.now()} @ {type.upper()}: {msg}' + '\n')

    except Exception as err:
        print(f'CRITICAL - Unable to create log: {str(err)}')
        input()


def load_list(filename: str, lst: list[Any]) -> list[Any]:
    try:
        with open(get_absolute_path(filename), 'r') as file:
            for item in file.readlines():
                item = item.strip()
                lst.append(item)

            log('info', f'{filename} successfully loaded')

    except Exception as err:
        log('error', f'Failed to load data - {str(err)}')

    return lst


def save_list(filename: str, lst: list[Any], mode: str = 'w') -> None:
    try:
        with open(get_absolute_path(filename), mode) as file:
            for item in lst:
                file.write(item + '\n')

            log('info', f'data successfully saved to {filename}')

    except Exception as err:
        log('error', f'Failed to save data - {str(err)}')


def load_json(filename: str) -> dict[Any, Any]:
    json_string = ''

    try:
        with open(get_absolute_path(filename), 'r') as file:
            for line in file.readlines():
                json_string += line
            log('info', f'{filename} successfully loaded')

    except Exception as err:
        log('error', f'Failed to load data - {str(err)}')

    return json.loads(json_string)


def save_json(filename: str, dtn: dict[Any, Any]):
    json_string = json.dumps(dtn)

    try:
        with open(get_absolute_path(filename), 'w') as file:
            file.write(json_string)
        log('info', f'data successfully saved to {filename}')
    except Exception as err:
        log('error', f'Failed to save data - {str(err)}')


def load_csv_to_dict(filename: str) -> list[Any]:
    
    temp = []
    
    with open(get_absolute_path(filename)) as file:
        reader = DictReader(file)
        for row in reader:
            temp.append(row)
            
    return temp


def save_dict_to_csv(filename: str, dicts: list[dict[Any, Any]]) -> None:
    headers = list(dicts[0].keys())
    with open(get_absolute_path(filename),'w') as file:
        writer = DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dicts)
