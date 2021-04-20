from flask_table import Table, Col, LinkCol


class Results(Table):
    game_id = Col("id")
    game_name = Col("game name")
    release_date = Col("release date")
    price = Col("price")
    score = Col("score")
    buy_me = LinkCol("Buy me!", "buy", url_kwargs=dict(game_id="game_id"))
