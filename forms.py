from wtforms import Form, StringField

class GameForm(Form):

    from_time = StringField('filter by release date:')
    to_time = StringField('')
    keywords = StringField('filter by keyword:')
    min_score = StringField('filter by min. score:')

class GameEditForm(Form):

    game_name = StringField('new game name')
    release_date = StringField('new release date')
    price = StringField('new price')
    score = StringField('new score')

class OrdersEditForm(Form):

    order_date = StringField('new order date')
    game_id = StringField('new game_id')
    net_amount = StringField('new net amount')
    discount = StringField('new discount')
    gross_amount = StringField('new gross amount')
