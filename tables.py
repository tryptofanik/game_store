from flask_table import Table, Col, LinkCol


class ResultsTable(Table):
    game_id = Col("id")
    game_name = Col("game name")
    release_date = Col("release date")
    price = Col("price")
    score = Col("score")
    buy_me = LinkCol("Buy me!", "buy", url_kwargs=dict(game_id="game_id"))

class OrdersManagerTable(Table):
    order_id = Col('id')
    order_date = Col('order date')
    game_id = Col('game id')
    net_amount = Col('net amount')
    discount = Col('discount')
    gross_amount = Col('gross amount')
    edit = LinkCol("Edit me!", "edit_order", url_kwargs=dict(order_id="order_id"))
    delete = LinkCol("Delete me!", "delete_order", url_kwargs=dict(order_id="order_id"))

class GamesManagerTable(Table):
    game_id = Col("id")
    game_name = Col("game name")
    release_date = Col("release date")
    price = Col("price")
    score = Col("score")
    edit = LinkCol("Edit me!", "edit_game", url_kwargs=dict(game_id="game_id"))
    delete = LinkCol("Delete me!", "delete_game", url_kwargs=dict(game_id="game_id"))
