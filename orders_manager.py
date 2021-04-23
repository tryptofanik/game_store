from collections import namedtuple
from datetime import date


order = namedtuple('Order', ['order_id', 'order_date', 'game_id', 'net_amount', 'discount', 'gross_amount'])


class OrdersManager():

    def __init__(self, cursor):
        self.cursor = cursor

    def create_order(self, game_id, net_amount, discount, gross_amount):
        query = f"""
        INSERT INTO Orders (order_date, game_id, net_amount, discount, gross_amount)
        VALUES ('{date.today()}', {game_id}, {net_amount}, {discount}, {gross_amount})
        """
        print(query)
        try:
            self.cursor.execute(query)
        except Exception as err:
            print(f"There was an error during adding order to the database!", err)
            return False
        return True
    
    def get_all_orders(self, ):
        query = "SELECT * FROM Orders"
        print(query)
        self.cursor.execute(query)
        return [order(*list(i)) for i in self.cursor]

    def get_order_by_id(self, order_id):
        query = f"SELECT * FROM Orders WHERE order_id = {order_id}"
        print(query)
        self.cursor.execute(query)
        return [order(*list(i)) for i in self.cursor][0]
    
    def edit_order(self, order_id, data):
        updates = []
        if data.get('order_date'):
            updates.append(f"order_date='{data.get('order_date')}'")
        if data.get('game_id'):
            updates.append(f"game_id='{data.get('game_id')}'")
        if data.get('net_amount'):
            updates.append(f"net_amount={data.get('net_amount')}")
        if data.get('discount'):
            updates.append(f"discount={data.get('discount')}")
        if data.get('gross_amount'):
            updates.append(f"gross_amount={data.get('gross_amount')}")

        query = f'UPDATE Orders SET {", ".join(updates)} WHERE order_id={order_id}'
        print(query)

        try:
            self.cursor.execute(query)
        except Exception as err:
            print(f'Sth went wrong with editing order of id {order_id}', err)
            return False
        return True
    
    def delete_order(self, order_id):
        query = f"DELETE FROM Orders WHERE order_id = {order_id}"
        try:
            self.cursor.execute(query)
        except Exception as err:
            print(f'Sth went wrong with deleting order of id {order_id}', err)
            return False
        return True
