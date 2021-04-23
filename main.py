from datetime import date
from collections import namedtuple

import flask
import pyodbc
from flask import Flask, request, url_for
from markupsafe import escape

from forms import GameEditForm, GameForm, OrdersEditForm
from tables import GamesManagerTable, OrdersManagerTable, ResultsTable
from orders_manager import OrdersManager, order
from games_manager import GamesManager, game

app = Flask(__name__)


conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=0.0.0.0;DATABASE=Store;UID=SA;PWD=SQL_server0!'
)

cursor = conn.cursor()


Orders = OrdersManager(cursor)
Games = GamesManager(cursor)

@app.route("/", methods=["GET", "POST"])
def index():
    search = GameForm(request.form)

    if request.method == "POST":
        return search_results(search)

    games = Games.select_games()
    table = ResultsTable(games)
    return flask.render_template("index.html", form=search, table=table)


@app.route("/")
def search_results(search):
    games = Games.select_games(**search.data)
    table = ResultsTable(games)
    return flask.render_template("index.html", form=search, table=table)


@app.route("/buy/<int:game_id>", methods=["GET", "POST"])
def buy(game_id):
    game_id, game_name, release_date, net_amount, score = Games.get_game_by_id(game_id)
    net_amount = round(float(net_amount), 2)
    now = date.today()
    discount = 'NULL'
    gross_amount = net_amount
    if (now - release_date).days > 365 * 3:  # game is older than 3 years
        discount = round(net_amount * 0.2, 2)
        gross_amount = (net_amount - discount) * 1.23

    success = Orders.create_order(game_id, net_amount, discount, gross_amount)
    if success:
        return f"You have bought game {game_name} for {gross_amount} ({net_amount} - {discount} + 23%)"
    else:
        return "There were some troubles on our site. Try again."


@app.route("/manager", methods=["GET"])
def manager():
    games = Games.select_games(min_score=0)
    games_table = GamesManagerTable(games)
    orders = Orders.get_all_orders()
    orders_table = OrdersManagerTable(orders)
    return flask.render_template(
        "manager.html", games_table=games_table, orders_table=orders_table)


@app.route('/manager/edit/game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    form = GameEditForm(request.form)
    if request.method == 'POST':
        success = Games.edit_game(game_id=game_id, data=form.data)

    return flask.render_template('edit_game.html', form=form)


@app.route('/manager/edit/order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    form = OrdersEditForm(request.form)
    if request.method == 'POST':
        success = Orders.edit_order(order_id=order_id, data=form.data)

    return flask.render_template('edit_order.html', form=form)


@app.route('/manager/delete/game/<int:game_id>', methods=['GET'])
def delete_game(game_id):
    query = f"DELETE FROM Games WHERE game_id = {game_id}"
    try:
        cursor.execute(query)
        return f'You successfully deleted game of id {game_id}'
    except Exception:
        return f'Failed to delete game of id {game_id}'


@app.route('/manager/delete/order/<int:order_id>', methods=['GET'])
def delete_order(order_id):
    success = Orders.delete_order(order_id=order_id)
    if success:
        return f'You successfully deleted order of id {order_id}'
    return f'Failed to delete order of id {order_id}'
