from flask import Flask, jsonify
from flask import request
import os
import json
import ast

from flask.wrappers import Response
from src.DbController import DbController

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Welcome To F&B Api'


@app.route('/view/<string:table>', methods=['GET'])
def get_table(table):
    query_res = DbController.instance().get_all_rows(table, '*')
    
    res = app.response_class(response=json.dumps(query_res), status=200,
                             mimetype='application/json')
    res.headers["Access-Control-Allow-Origin"] = '*'
    return res


@app.route('/view/<string:table>/<int:id>', methods=['GET', 'POST'])
def get_item(table: str, id: int):
    if request.method == 'GET':
        query_res = DbController.instance().get_rows_where(table, '*', 'id', str(id))
        
        res = app.response_class(response=json.dumps(query_res), status=200,
                                mimetype='application/json')
        res.headers["Access-Control-Allow-Origin"] = '*'
        return res
    else:
        query = DbController.instance().update(table, id, ast.literal_eval(request.data.decode('UTF-8')))
        res = app.response_class(response=json.dumps(query), status=200,
                                 mimetype='application/json')
        res.headers["Access-Control-Allow-Origin"] = '*'
        return res
        


@app.route('/orders', methods=['GET'])
def get_order_view():
    query_res = DbController.instance().get_joins(
        fields=['o.id', 'o.name', 'o.address',
                'o.area', 'o.phone', 'courier.name AS Courier', 's.code AS status'],
        source='orders o',
        targets=['couriers courier', 'status s'],
        conditions=['courier.id = o.courier', 's.id = o.status'],
        order=f'ORDER BY o.status')
    
    res = app.response_class(response=json.dumps(query_res), status=200,
                             mimetype='application/json')
    res.headers["Access-Control-Allow-Origin"] = '*'
    return res


@app.route('/orders/<int:id>', methods=['GET', 'POST'])
def get_order(id: int):    
    query_res = DbController.instance().get_joins_where(
        fields=['b.quantity AS "#x"', 'p.name',
                'b.quantity * p.price AS "Sub Total"'],
        source='orders o',
        targets=['basket b', 'products p'],
        conditions=[f'b.order_id = {id}', 'b.item = p.id'],
        where=f'o.id = {id}',
        type= 'INNER')

    res = app.response_class(response=json.dumps(query_res), status=200,
                             mimetype='application/json')
    res.headers["Access-Control-Allow-Origin"] = '*'
    return res


@app.errorhandler(404)
def not_found(error):
    return error

    
host = os.environ.get("mysql_host")
user = os.environ.get("mysql_user")
password = os.environ.get("mysql_pass")
database = os.environ.get("mysql_db")

DbController(host, user, password, database) #type: ignore
