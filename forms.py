from wtforms import Form, StringField

class GameForm(Form):

    choices = [('Artist', 'Artist'),
               ('Album', 'Album'),
               ('Publisher', 'Publisher')]
    from_time = StringField('filter by release date:')
    to_time = StringField('')
    keywords = StringField('filter by keyword:')
    min_score = StringField('filter by min. score:')
