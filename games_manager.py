from collections import namedtuple


game = namedtuple('Game', ['game_id', 'game_name', 'release_date', 'price', 'score'])


class GamesManager():

    def __init__(self, cursor):
        self.cursor = cursor

    def select_games(self, from_time=None, to_time=None, keywords=None, min_score=None):
        query = 'SELECT * FROM Games'

        conditions = []
        if min_score:
            conditions.append(f"score >= {min_score}")
        if keywords:
            conditions.append(f"game_name like '%{keywords}%'")
        if from_time:
            conditions.append(f"release_date >= '{from_time}'")
        if to_time:
            conditions.append(f"release_date <= '{to_time}'")
        if len(conditions):
            query += ' WHERE ' + ' AND '.join(conditions)

        print(query)
        self.cursor.execute(query)

        return [game(*list(i)) for i in self.cursor]

    def get_game_by_id(self, game_id):
        query = f"SELECT * FROM Games WHERE game_id={game_id}"
        print(query)
        self.cursor.execute(query)
        return [game(*list(i)) for i in self.cursor][0]

    def edit_game(self, game_id, data):
        updates = []
        if data.get('game_name'):
            updates.append(f"game_name='{data.get('game_name')}'")
        if data.get('release_date'):
            updates.append(f"release_date='{data.get('release_date')}'")
        if data.get('price'):
            updates.append(f"price={data.get('price')}")
        if data.get('score'):
            updates.append(f"score={data.get('score')}")

        query = f'UPDATE Games SET {", ".join(updates)} WHERE game_id={game_id}'
        print(query)
        try:
            self.cursor.execute(query)
        except Exception as err:
            print(f'Sth went wrong with editing game of id {game_id}', err)
            return False
        return True

    def delete_game(self, game_id):
        query = f"DELETE FROM Games WHERE game_id = {game_id}"
        print(query)
        try:
            self.cursor.execute(query)
        except Exception as err:
            print(f'Sth went wrong with deleting game of id {game_id}', err)
            return False
        return True