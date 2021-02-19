from __future__ import annotations
from typing import Any, Sequence, Union
import pymysql
from pymysql import converters
import pymysql.cursors
from pymysql import NULL

from .file_system import log


class DbController():

    inst = None

    def __new__(cls, host: str, user: str, password: str, database: str, autocommit: bool = True):
        # SET DECIMAL CONVERSION TO FLOAT
        conv = converters.conversions.copy()
        conv[246] = float

        if cls.inst == None:
            cls.inst = object.__new__(cls)
            try:
                cls.connection = pymysql.connect(
                    host,
                    user,
                    password,
                    database,
                    autocommit=autocommit,
                    cursorclass=pymysql.cursors.DictCursor,
                    conv=conv
                )
            except Exception as err:
                cls.connection = None

        return cls.inst
    
    @classmethod
    def instance(cls) -> Union[DbController, None]:
        return cls.inst

    
    def execute(self, sql: str) -> list[dict[Any, Any]]:
        
        ##JUST FOR TEST RUNNER <--> CHECK FOR CONNECTION SHOULD BE USED##
        if not self.connection:
            log('error', 'No Connection To Source')
            return [{'':'error'}]
        
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


    def call_proc(self, name: str) -> list[dict[Any, Any]]:
        
        #JUST FOR TEST RUNNER <--> CHECK FOR CONNECTION SHOULD BE USED##
        if not self.connection:
            log('error', 'No Connection To Source')
            return [{'': 'error'}]

        with self.connection.cursor() as cursor:
            log('info', name)

            try:
                cursor.callproc(name)
                return cursor.fetchall()  # type: ignore
            except Exception as err:
                log('error', str(err))
                print(
                    f'\u001b[37;1m\u001b[41;1mUnable To Process Request. Check Log For Details\u001b[0m')
                input()
                return [{'': 'error'}]
    
    
    def escape_seq(self, seq: Sequence, parens: bool = True) -> str:
        fields_string = ''
        if parens:
            fields_string += '('
        for field in seq:
            fields_string += f'{field}, '
        fields_string = fields_string[0:-2]
        if parens:
            fields_string += ')'

        return fields_string

    
    def escape_alias(self, field: str) -> str:
        if 'AS' in field:
            index = field.index('AS')
            return field[:index]
        return field

    
    def close(self) -> None:
        self.connection.close()

    
    def get_field_names(self, table: str) -> list[Any]:
        res = self.execute(f'DESCRIBE mini_project.{table}')
        result = []
        for field in res:
            if 'Field' in field and field['Field'] != 'id':
                result.append(field['Field'])

        return result

    
    def get_column(self, table: str, column: str) -> list[dict[Any, Any]]:
        return self.execute(f'SELECT {column} FROM {table}')

    
    def get_all_rows(self, table: str,get: str, order: str = '') -> list[dict[Any, Any]]:
        return self.execute(f'SELECT {get} FROM {table} {order}')


    def get_rows_where(self, table: str, get: str, field: str, condition: str) -> list[dict[Any, Any]]:
        return self.execute(f'SELECT {get} FROM {table} WHERE {field} = "{condition}"')

    
    def insert(self, table: str, dtn: dict[str, Any]):
        fields = self.escape_seq([key for key in dtn.keys()])

        values = tuple([value for value in dtn.values()])
        self.execute(f'INSERT INTO %s %s VALUES %s' %
                      (table, fields, values))

    
    def delete(self, table: str, id: int):
        self.execute(f'DELETE FROM {table} WHERE id = {id}')

    
    def delete_where(self, table: str, where_fields: list[str],  where_conditions: list[str]):
        query = f'DELETE FROM {table} WHERE '
        assert(len(where_fields) == len(where_conditions))
        for i in range(len(where_fields)):
            query += f'{where_fields[i]} = {where_conditions[i]} '
            if len(where_fields) > 1 and i < len(where_fields) - 1:
                query += 'AND '
        self.execute(query)

    
    def update(self, table: str, id: int, dtn: dict[str, Any]):
        query = ''
        for k, v in dtn.items():
            if v == None:
                v = NULL
                query += f"{k} = {v}, "
            else:
                query += f"{k} = '{v}', "
        query = query[0:-2]
        self.execute(f'UPDATE {table} SET {query} WHERE id = {id}')

    
    def update_where(self, table: str, where_fields: list[str],  where_conditions: list[str], dtn: dict[str, Any]):
        query = ''
        for k, v in dtn.items():
            if v == None:
                v = NULL
                query += f"{k} = {v}, "
            else:
                query += f"{k} = '{v}', "
        query = query[0:-2]
        query += ' WHERE '
        assert(len(where_fields) == len(where_conditions))
        for i in range(len(where_fields)):
            query += f'{where_fields[i]} = {where_conditions[i]} '
            if len(where_fields) > 1 and i < len(where_fields) - 1:
                query += 'AND '
        self.execute(f'UPDATE {table} SET {query}')

    
    def get_joins(self, fields: list[str], source: str, targets: list[str], conditions: list[str], type: str = 'LEFT OUTER', order: str = '') -> list[dict[Any, Any]]:
        query = f'SELECT {self.escape_seq(fields, parens=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'{type} JOIN {targets[i]} ON {conditions[i]} '
        query += f'{order}'
        return self.execute(query)

    
    def get_joins_where(self, fields: list[str], source: str, targets: list[str], conditions: list[str], where: str, type: str = 'LEFT OUTER', order: str = '') -> list[dict[Any, Any]]:
        query = f'SELECT {self.escape_seq(fields, parens=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'{type} JOIN {targets[i]} ON {conditions[i]} '
        query += f'WHERE {where} {order}'
        return self.execute(query)

    
    def search_table(self, table: str, term: str):
        fields = tuple(self.get_field_names(table))
        query = f'SELECT * FROM {table} WHERE '
        for i in range(len(fields)):
            query += f'{fields[i]} LIKE "%{term}%" '
            if i < len(fields) - 1:
                query += 'OR '
        return self.execute(query)

    
    def search_joined_table(self, table: str, term: str, fields: list[str], targets: list[str], conditions: list[str]) -> list[dict[Any, Any]]:
        query = f'SELECT {self.escape_seq(fields, parens=False)} FROM {table} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'LEFT OUTER JOIN {targets[i]} ON {conditions[i]} '
        query += 'WHERE '
        for i in range(len(fields)):
            query += f'{self.escape_alias(fields[i])} LIKE "%{term}%" '
            if i < len(fields) - 1:
                query += 'OR '
        return self.execute(query)


    def get_available_procs(self) -> list[Any]:
        procs = self.execute('SHOW PROCEDURE STATUS WHERE Db="mini_project"')
        return [proc['Name'].replace('_', ' ') for proc in procs]
    
