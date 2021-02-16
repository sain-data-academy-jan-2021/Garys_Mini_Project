from typing import Any, Sequence
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
    def __execute(cls, sql: str) -> list[dict[Any, Any]]:
        with cls.connection.cursor() as cursor:
            log('debug', sql)
            
            try:
                cursor.execute(sql)
                return cursor.fetchall() #type: ignore
            except Exception as err:
                log('error', str(err))
                print(
                    f'\u001b[37;1m\u001b[41;1mUnable To Process Request. Check Log For Details\u001b[0m')
                input()
                return [{'':'error'}]
    
    @classmethod
    def __escape_seq(cls, seq: Sequence, parens: bool =True) -> str:
        fields_string = ''
        if parens:
            fields_string += '('
        for field in seq:
            fields_string += f'{field}, '
        fields_string = fields_string[0:-2]
        if parens:
            fields_string += ')'
        
        return fields_string
    
    @classmethod
    def __escape_alias(cls, field: str) -> str:
        if 'AS' in field:
            index = field.index('AS')
            return field[:index]
        return field
    
    @classmethod
    def close(cls) -> None:
        cls.connection.close()
    
    @classmethod
    def get_field_names(cls, table: str) -> list[Any]:
        res = cls.__execute(f'DESCRIBE mini_project.{table}')
        result = []
        for field in res:
            if field['Field'] != 'id':  
                result.append(field['Field']) 
                
        return result
    
    @classmethod
    def get_column(cls, table: str, column: str) -> list[dict[Any, Any]]:
        return cls.__execute(f'SELECT {column} FROM {table}')
    
    @classmethod
    def get_all_rows(cls, table: str, order:str ='') -> list[dict[Any, Any]]:
        return cls.__execute(f'SELECT * from {table} {order}')

    @classmethod
    def get_row_by_id(cls, table: str, id: int) -> list[dict[Any, Any]]:
        return cls.__execute(f'SELECT * from {table} WHERE id = {id}')
    
    @classmethod
    def get_all_rows_where(cls, table: str, field: str, condition: Any) -> list[dict[Any, Any]]:
        return cls.__execute(f'SELECT * from {table} WHERE {field} = "{condition}"')
    
    @classmethod
    def get_rows_where(cls, table: str,get: str, field: str, condition: str) -> list[dict[Any, Any]]:
        return cls.__execute(f'SELECT {get} from {table} WHERE {field} = "{condition}"')
    
    @classmethod
    def insert(cls, table: str, dtn: dict[str, Any]):
        fields = cls.__escape_seq([key for key in dtn.keys()])
        
        values = tuple([value for value in dtn.values()])
        cls.__execute(f'INSERT INTO %s %s VALUES %s' %
                       (table, fields, values))

    @classmethod
    def delete(cls, table: str, id: int):
        cls.__execute(f'DELETE FROM {table} WHERE id = {id}')
        
    @classmethod
    def delete_where(cls, table: str,where_fields: list[str],  where_conditions: list[str]):
        query = f'DELETE FROM {table} WHERE '
        assert(len(where_fields) == len(where_conditions))
        for i in range(len(where_fields)):
            query += f'{where_fields[i]} = {where_conditions[i]} '
            if len(where_fields) > 1 and i < len(where_fields) - 1:
                query += 'AND '
        cls.__execute(query)
    
    @classmethod
    def update(cls, table: str, id: int, dtn: dict[str, Any]):
        query = ''
        for k,v in dtn.items():
            if v == None:
                v = NULL
                query += f"{k}={v}, "
            else: 
                query += f"{k}='{v}', "
        query = query[0:-2]
        cls.__execute(f'UPDATE {table} SET {query} WHERE id={id}')
        
    @classmethod
    def update_where(cls, table: str, where_fields: list[str],  where_conditions: list[str], dtn: dict[str, Any]):
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
        cls.__execute(f'UPDATE {table} SET {query}')
    
    @classmethod
    def get_join(cls, fields: list[str], source: str, target: str, condition: str) -> list[dict[Any, Any]]:
        query = f'SELECT {cls.__escape_seq(fields, parens=False)} FROM {source} LEFT OUTER JOIN {target} ON {condition}'
        return cls.__execute(query)

    @classmethod
    def get_joins(cls, fields: list[str], source: str, targets: list[str], conditions: list[str], type: str ='LEFT OUTER', order: str ='') -> list[dict[Any, Any]]:
        query = f'SELECT {cls.__escape_seq(fields, parens=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'{type} JOIN {targets[i]} ON {conditions[i]} '
        query += f'{order}'
        return cls.__execute(query)
    
    @classmethod
    def get_joins_where(cls, fields: list[str], source: str, targets: list[str], conditions: list[str], where: str, type: str = 'LEFT OUTER', order: str = '') -> list[dict[Any, Any]]:
        query = f'SELECT {cls.__escape_seq(fields, parens=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'{type} JOIN {targets[i]} ON {conditions[i]} '
        query += f'WHERE {where} {order}'
        return cls.__execute(query)

    @classmethod
    def search_table(cls, table: str, term: str):
        fields = tuple(cls.get_field_names(table))
        query = f'SELECT * FROM {table} WHERE '
        for i in range(len(fields)):
            query += f'{fields[i]} LIKE "%{term}%" '
            if i < len(fields) - 1:
                query += 'OR '
        return cls.__execute(query)
    
    @classmethod
    def search_joined_table(cls, table: str, term: str,fields: list[str], targets: list[str], conditions: list[str]) -> list[dict[Any, Any]]:
        query = f'SELECT {cls.__escape_seq(fields, parens=False)} FROM {table} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'LEFT OUTER JOIN {targets[i]} ON {conditions[i]} '
        query += 'WHERE '
        for i in range(len(fields)):
            query += f'{cls.__escape_alias(fields[i])} LIKE "%{term}%" '
            if i < len(fields) -1:
                query += 'OR '
        return cls.__execute(query)
        
        
