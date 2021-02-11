from typing import Any, Sequence
import pymysql
from pymysql import converters
import pymysql.cursors


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
    def __execute(cls, sql: str):
        with cls.connection.cursor() as cursor:
            cursor.execute(sql)

            return cursor.fetchall()
    
    @classmethod
    def __escape_seq(cls, seq: Sequence, parnes: bool =True) -> str:
        fields_string = ''
        if parnes:
            fields_string += '('
        for field in seq:
            fields_string += f'{field}, '
        fields_string = fields_string[0:-2]
        if parnes:
            fields_string += ')'
        
        return fields_string
    
    @classmethod
    def close(cls):
        cls.connection.close()
    
    @classmethod
    def get_field_names(cls, table: str):
        res = cls.__execute(f'DESCRIBE mini_project.{table}')
        result = []
        for field in res:
            if field['Field'] != 'id':  # type: ignore
                result.append(field['Field'])  # type: ignore
                
        return result
    
    @classmethod
    def get_all_rows(cls, table: str):
        return cls.__execute(f'SELECT * from {table}')

    @classmethod
    def get_row_by_id(cls, table: str, id: int):
        return cls.__execute(f'SELECT * from {table} WHERE id = {id}')
    
    @classmethod
    def get_all_rows_where(cls, table: str, field: str, condition: str):
        return cls.__execute(f'SELECT * from {table} WHERE {field} = "{condition}"')
    
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
    def update(cls, table: str, id: int, dtn: dict[str, Any]):
        query = ''
        for k,v in dtn.items():
            query += f"{k}='{v}', "
        query = query[0:-2]
        cls.__execute(f'UPDATE {table} SET {query} WHERE id={id}')
    
    @classmethod
    def get_join(cls, fields: list[str], source: str, target: str, condition: str):
        query = f'SELECT {cls.__escape_seq(fields, parnes=False)} FROM {source} LEFT OUTER JOIN {target} ON {condition}'
        return cls.__execute(query)

    @classmethod
    def get_joins(cls, fields: list[str], source: str, targets: list[str], conditions: list[str]):
        query = f'SELECT {cls.__escape_seq(fields, parnes=False)} FROM {source} '
        assert len(targets) == len(conditions)
        for i in range(len(targets)):
            query += f'LEFT OUTER JOIN {targets[i]} ON {conditions[i]} '
        return cls.__execute(query)

# Test Functions
controller = DbController('localhost', 'root', 'password', 'mini_project')
product = {
    'name': 'Bobby Bobbo',
    'phone_number': '07875480922'
}

