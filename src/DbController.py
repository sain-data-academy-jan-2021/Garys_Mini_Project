from __future__ import annotations
from typing import Any, Sequence, Union
import pymysql
from pymysql import converters
import pymysql.cursors
from pymysql import NULL

from .file_system import log


class DbController():

    __instance = None

    def __new__(cls, host: str, user: str, password: str, database: str, autocommit: bool = True):
        # SET DECIMAL CONVERSION TO FLOAT
        conv = converters.conversions.copy()
        conv[246] = float

        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            cls.connection = pymysql.connect(
                host,
                user,
                password,
                database,
                autocommit=autocommit,
                cursorclass=pymysql.cursors.DictCursor,
                conv=conv
            )

        return cls.__instance
    
    @classmethod
    def instance(cls) -> Union[DbController, None]:
        return cls.__instance

    
    def __execute(self, sql: str) -> list[dict[Any, Any]]:
        with self.connection.cursor() as cursor:
            log('info', sql)

            try:
                cursor.execute(sql)
                return cursor.fetchall()  # type: ignore
            except Exception as err:
                log('error', str(err))
                log('error', sql)
                print(
                    f'\u001b[37;1m\u001b[41;1mUnable To Process Request. Check Log For Details\u001b[0m')
                input()
                return [{'': 'error'}]

    
    def __escape_seq(self, seq: Sequence, parens: bool = True) -> str:
        fields_string = ''
        if parens:
            fields_string += '('
        for field in seq:
            fields_string += f'{field}, '
        fields_string = fields_string[0:-2]
        if parens:
            fields_string += ')'

        return fields_string

    
    def __escape_alias(self, field: str) -> str:
        if 'AS' in field:
            index = field.index('AS')
            return field[:index]
        return field

    
    def close(self) -> None:
        self.connection.close()

    
    def get_field_names(self, table: str) -> list[Any]:
        res = self.__execute(f'DESCRIBE mini_project.{table}')
        result = []
        for field in res:
            if field['Field'] != 'id':
                result.append(field['Field'])

        return result

    
    def get_column(self, table: str, column: str) -> list[dict[Any, Any]]:
        return self.__execute(f'SELECT {column} FROM {table}')

    
    def get_all_rows(self, table: str, order: str = '') -> list[dict[Any, Any]]:
        return self.__execute(f'SELECT * from {table} {order}')

    
    def get_row_by_id(self, table: str, id: int) -> list[dict[Any, Any]]:
        return self.__execute(f'SELECT * from {table} WHERE id = {id}')

    
    def get_all_rows_where(self, table: str, field: str, condition: Any) -> list[dict[Any, Any]]:
        return self.__execute(f'SELECT * from {table} WHERE {field} = "{condition}"')

    
    def get_rows_where(self, table: str, get: str, field: str, condition: str) -> list[dict[Any, Any]]:
        return self.__execute(f'SELECT {get} from {table} WHERE {field} = "{condition}"')

    
    def insert(self, table: str, dtn: dict[str, Any]):
        fields = self.__escape_seq([key for key in dtn.keys()])

        values = tuple([value for value in dtn.values()])
        self.__execute(f'INSERT INTO %s %s VALUES %s' %
                      (table, fields, values))

    
    def delete(self, table: str, id: int):
        self.__execute(f'DELETE FROM {table} WHERE id = {id}')

    
    def delete_where(self, table: str, where_fields: list[str],  where_conditions: list[str]):
        query = f'DELETE FROM {table} WHERE '
        assert(len(where_fields) == len(where_conditions))
        for i in range(len(where_fields)):
            query += f'{where_fields[i]} = {where_conditions[i]} '
            if len(where_fields) > 1 and i < len(where_fields) - 1:
                query += 'AND '
        self.__execute(query)

    
    def update(self, table: str, id: int, dtn: dict[str, Any]):
        query = ''
        for k, v in dtn.items():
            if v == None:
                v = NULL
                query += f"{k}={v}, "
            else:
                query += f"{k}='{v}', "
        query = query[0:-2]
        self.__execute(f'UPDATE {table} SET {query} WHERE id={id}')

    
    def update_where(self, table: str, where_fields: list[str],  where_conditions: list[str], dtn: dict[str, Any]):
        query = ''
        for k, v in dtn.items():
            if v == None:
                v = NULL
                query += f"{k}={v}, "
            else:
                query += f"{k}='{v}', "
        query = query[0:-2]
        query += 'WHERE '
        assert(len(where_fields) == len(where_conditions))
        for i in range(len(where_fields)):
            query += f'{where_fields[i]} = {where_conditions[i]} '
            if len(where_fields) > 1 and i < len(where_fields) - 1:
                query += 'AND '
        self.__execute(f'UPDATE {table} SET {query}')

    
    def get_join(self, fields: list[str], source: str, target: str, condition: str) -> list[dict[Any, Any]]:
        query = f'SELECT {self.__escape_seq(fields, parens=False)} FROM {source} LEFT OUTER JOIN {target} ON {condition}'
        return self.__execute(query)

    
    def get_joins(self, fields: list[str], source: str, targets: list[str], conditions: list[str], type: str = 'LEFT OUTER', order: str = '') -> list[dict[Any, Any]]:
        query = f'SELECT {self.__escape_seq(fields, parens=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'{type} JOIN {targets[i]} ON {conditions[i]} '
        query += f'{order}'
        return self.__execute(query)

    
    def get_joins_where(self, fields: list[str], source: str, targets: list[str], conditions: list[str], where: str, type: str = 'LEFT OUTER', order: str = '') -> list[dict[Any, Any]]:
        query = f'SELECT {self.__escape_seq(fields, parens=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'{type} JOIN {targets[i]} ON {conditions[i]} '
        query += f'WHERE {where} {order}'
        return self.__execute(query)

    
    def search_table(self, table: str, term: str):
        fields = tuple(self.get_field_names(table))
        query = f'SELECT * FROM {table} WHERE '
        for i in range(len(fields)):
            query += f'{fields[i]} LIKE "%{term}%" '
            if i < len(fields) - 1:
                query += 'OR '
        return self.__execute(query)

    
    def search_joined_table(self, table: str, term: str, fields: list[str], targets: list[str], conditions: list[str]) -> list[dict[Any, Any]]:
        query = f'SELECT {self.__escape_seq(fields, parens=False)} FROM {table} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'LEFT OUTER JOIN {targets[i]} ON {conditions[i]} '
        query += 'WHERE '
        for i in range(len(fields)):
            query += f'{self.__escape_alias(fields[i])} LIKE "%{term}%" '
            if i < len(fields) - 1:
                query += 'OR '
        return self.__execute(query)

    
    def get_order_status_summary(self) -> list[dict[Any, Any]]:
        return  self.__execute(
            'SELECT UPPER(s.code) AS status, COUNT(o.status) AS count FROM orders o LEFT OUTER JOIN status s ON o.status = s.id GROUP BY status')

    
    def get_order_totals(self) -> list[dict[Any, Any]]:
        return self.__execute(
            'SELECT o.id, UPPER(o.name) AS Name, SUM((b.quantity * p.price)) AS Total FROM basket b LEFT OUTER JOIN orders o ON b.order_id=o.id LEFT OUTER JOIN products p ON b.item=p.id GROUP BY o.id')

    
    def get_unassigned_orders(self) -> list[dict[Any, Any]]:
        return self.__execute('SELECT id, name FROM orders WHERE courier is NULL')
    
    
    def get_unassigned_couriers(self) -> list[dict[Any, Any]]:
        return self.__execute('SELECT c.id, c.name FROM couriers c LEFT OUTER JOIN orders o ON o.courier=c.id WHERE o.courier is NULL')
    
    
    
