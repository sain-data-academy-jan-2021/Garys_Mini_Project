from logging import FATAL
from typing import Any, Sequence
import pymysql
from pymysql import converters
import pymysql.cursors


class DbController():

    def __init__(self, host: str, user: str, password: str, database: str, autocommit: bool = True):
        # SET DECIMAL CONVERSION TO FLOAT
        conv = converters.conversions.copy()
        conv[246] = float

        self.connection = pymysql.connect(
            host,
            user,
            password,
            database,
            autocommit=autocommit,
            cursorclass=pymysql.cursors.DictCursor,
            conv=conv
        )

    def __execute(self, sql: str):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)

            return cursor.fetchall()
        
    def __escape_seq(self, seq: Sequence, parnes: bool =True) -> str:
        fields_string = ''
        if parnes:
            fields_string += '('
        for field in seq:
            fields_string += f'{field}, '
        fields_string = fields_string[0:-2]
        if parnes:
            fields_string += ')'
        
        return fields_string

    def close(self):
        self.connection.close()

    def get_field_names(self, table: str):
        res = self.__execute(f'DESCRIBE mini_project.{table}')
        result = []
        for field in res:
            if field['Field'] != 'id':  # type: ignore
                result.append(field['Field'])  # type: ignore
                
        return result
    
    def get_all_rows(self, table: str):
        return self.__execute(f'SELECT * from {table}')

    def get_row_by_id(self, table: str, id: int):
        return self.__execute(f'SELECT * from {table} WHERE id = {id}')
    
    def get_all_rows_where(self, table: str, field: str, condition: str):
        return self.__execute(f'SELECT * from {table} WHERE {field} = "{condition}"')
    
    def insert(self, table: str, dtn: dict[str, Any]):
        fields = self.__escape_seq([key for key in dtn.keys()])
        
        values = tuple([value for value in dtn.values()])
        self.__execute(f'INSERT INTO %s %s VALUES %s' %
                       (table, fields, values))
        
    def delete(self, table: str, id: int):
        self.__execute(f'DELETE FROM {table} WHERE id = {id}')
        
    def update(self, table: str, id: int, dtn: dict[str, Any]):
        query = ''
        for k,v in dtn.items():
            query += f"{k}='{v}', "
        query = query[0:-2]
        self.__execute(f'UPDATE {table} SET {query} WHERE id={id}')
    
    def get_join(self, fields: list[str], source: str, target: str, condition: str):
        query = f'SELECT {self.__escape_seq(fields, parnes=False)} FROM {source} LEFT OUTER JOIN {target} ON {condition}'
        return self.__execute(query)   

# Test Functions
controller = DbController('localhost', 'root', 'password', 'mini_project')
product = {
    'name': 'Bobby Bobbo',
    'phone_number': '07875480922'
}
print(controller.get_join(['o.name', 'o.area', 'o.phone', 'c.name'],'orders o', 'couriers c', 'c.id = o.courier'))

