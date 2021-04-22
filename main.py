from datetime import date

import flask
from flask import Flask, request, url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

from forms import GameForm, GameEditForm, OrdersEditForm
from tables import Results, GamesManager, OrdersManager

app = Flask(__name__)

connect_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=0.0.0.0;DATABASE=Store;UID=SA;PWD=SQL_server0!"

app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc:///?odbc_connect=%s" % connect_str
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class Games(db.Model):

    game_id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.Text)
    release_date = db.Column(db.Date)
    price = db.Column(db.Float)
    score = db.Column(db.Float)
    orders = db.relationship("Orders", backref="games", lazy=False)

    @classmethod
    def get_all_games(cls):
        return (
            db.session.query(
                Games.game_id,
                Games.game_name,
                Games.release_date,
                Games.price,
                Games.score,
            )
            .order_by(Games.score.desc())
            .all()
        )

    @classmethod
    def select_games(cls, from_time=None, to_time=None, keywords=None, min_score=50):
        query = db.session.query(
            Games.game_id, Games.game_name, Games.release_date, Games.price, Games.score
        )
        if min_score:
            query = query.filter(Games.score >= int(min_score))
        if from_time or to_time:
            query = query.filter(Games.release_date >= from_time)
        if to_time:
            query = query.filter(Games.release_date <= to_time)
        if keywords:
            query = query.filter(Games.game_name.contains(keywords)).from_self()
        query = query.order_by(Games.score.desc())
        return query.all()

    @classmethod
    def get_game_by_id(cls, game_id, return_query_obj=False):
        query = (
            db.session.query(
                Games.game_id,
                Games.game_name,
                Games.release_date,
                Games.price,
                Games.score,
            )
            .filter(Games.game_id == game_id)
        )
        if not return_query_obj:
            return query.first()
        return query


    @classmethod
    def edit_game(cls, game_id, **kwargs):
        game = cls.get_game_by_id(game_id, return_query_obj=True)
        game.update(dict(**kwargs))
        try:
            db.session.commit()
        except Exception as err:
            print(f'Sth went wrong with editing game of id {game_id}', err)
            return False
        return True

    @classmethod
    def delete_game(cls, game_id):
        game = cls.get_game_by_id(game_id, return_query_obj=True)
        try:
            game.delete()
            db.session.commit()
        except Exception as err:
            print(f'Sth went wrong with deleting game of id {game_id}', err)
            return False
        return True

class Orders(db.Model):

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.Date)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"))
    net_amount = db.Column(db.Float)
    discount = db.Column(db.Float)
    gross_amount = db.Column(db.Float)

    @classmethod
    def create_order(cls, game_id, net_amount, discount, gross_amount):
        new_order = Orders()
        new_order.order_date = date.today()
        new_order.game_id = game_id
        new_order.net_amount = net_amount
        new_order.discount = discount
        new_order.gross_amount = gross_amount
        try:
            db.session.add(new_order)
            db.session.commit()
        except Exception as err:
            print(f"There was an error during adding order to the database!", err)
            return False
        return True
    
    @classmethod
    def get_all_orders(cls):
        return (
            db.session.query(
                Orders.order_id,
                Orders.order_date,
                Orders.game_id,
                Orders.net_amount,
                Orders.discount,
                Orders.gross_amount,
            )
            .all()
        )

    @classmethod
    def get_order_by_id(cls, order_id):
        return (
            db.session.query(
                Orders.order_id,
                Orders.order_date,
                Orders.game_id,
                Orders.net_amount,
                Orders.discount,
                Orders.gross_amount,
            )
            .filter(Orders.order_id == order_id)
        )
    
    @classmethod
    def edit_order(cls, order_id, **kwargs):
        order = cls.get_order_by_id(order_id)
        order.update(dict(**kwargs))
        try:
            db.session.commit()
        except Exception as err:
            print(f'Sth went wrong with editing order of id {order_id}', err)
            return False
        return True
    
    @classmethod
    def delete_order(cls, order_id):
        order = cls.get_order_by_id(order_id)
        try:
            order.delete()
            db.session.commit()
        except Exception as err:
            print(f'Sth went wrong with deleting order of id {order_id}', err)
            return False
        return True

@app.route("/", methods=["GET", "POST"])
def index():
    search = GameForm(request.form)

    if request.method == "POST":
        return search_results(search)

    games = Games.get_all_games()
    table = Results(games)
    return flask.render_template("index.html", form=search, table=table)


@app.route("/")
def search_results(search):
    games = Games.select_games(**search.data)
    table = Results(games)
    return flask.render_template("index.html", form=search, table=table)


@app.route("/buy/<int:game_id>", methods=["GET", "POST"])
def buy(game_id):
    game_id, game_name, release_date, net_amount, score = Games.get_game_by_id(game_id)
    net_amount = round(float(net_amount), 2)
    now = date.today()
    discount = 0
    if (now - release_date).days > 365 * 3:  # game is older than 3 years
        discount = round(net_amount * 0.3, 2)
    gross_amount = (net_amount - discount) * 1.23

    success = Orders.create_order(game_id, net_amount, discount, gross_amount)
    if success:
        return f"You have bought game {game_name} for {gross_amount} ({net_amount} - {discount} + 23%)"
    else:
        return "There were some troubles on our site. Try again."


@app.route("/manager", methods=["GET"])
def manager():
    games = Games.select_games(min_score=0)
    games_table = GamesManager(games)
    orders = Orders.get_all_orders()
    orders_table = OrdersManager(orders)
    return flask.render_template(
        "manager.html", games_table=games_table, orders_table=orders_table)


@app.route('/manager/edit/game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    form = GameEditForm(request.form)
    if request.method == 'POST':
        success = Games.edit_game(game_id=game_id, **form.data)

    return flask.render_template('edit_game.html', form=form)


@app.route('/manager/edit/order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    form = OrdersEditForm(request.form)
    if request.method == 'POST':
        success = Orders.edit_order(order_id=order_id, **form.data)

    return flask.render_template('edit_order.html', form=form)


@app.route('/manager/delete/game/<int:game_id>', methods=['GET'])
def delete_game(game_id):
    success = Games.delete_game(game_id=game_id)
    if success:
        return f'You successfully deleted game of id {game_id}'
    return f'Failed to delete game of id {game_id}'


@app.route('/manager/delete/order/<int:order_id>', methods=['GET'])
def delete_order(order_id):
    success = Orders.delete_order(order_id=order_id)
    if success:
        return f'You successfully deleted order of id {order_id}'
    return f'Failed to delete order of id {order_id}'
