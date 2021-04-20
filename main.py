from datetime import date

import flask
from flask import Flask, request, url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

from forms import GameForm
from tables import Results

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
    def get_game_by_id(cls, game_id):
        query = (
            db.session.query(
                Games.game_id,
                Games.game_name,
                Games.release_date,
                Games.price,
                Games.score,
            )
            .filter(Games.game_id == game_id)
            .first()
        )
        return query


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


@app.route("/", methods=["GET", "POST"])
def index():
    search = GameForm(request.form)

    if request.method == "POST":
        return search_results(search)

    games = Games.get_all_games()
    table = Results(games)
    return flask.render_template("index.html", games=games, form=search, table=table)


@app.route("/results")
def search_results(search):
    games = Games.select_games(**search.data)
    table = Results(games)
    return flask.render_template("index.html", games=games, form=search, table=table)


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
