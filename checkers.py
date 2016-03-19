import traceback
from itertools import repeat, product
from pprint import pprint
from string import ascii_letters


class Board:
    LETTERS = ascii_letters[:8]
    next_move = 'B'
    on_edge = (0, 7)

    def __init__(self):
        def cell_marker(raw):
            """
            :param raw: raw number
            :return: list of black cells for current raw
            """
            return range(0, 8, 2) if (raw + 1) % 2 else range(1, 8, 2)

        def cup_marker(raw):
            """
            :param raw ~> raw number
            :return ~> cell's value based on the raw
            """
            return 'B' if raw in (0, 1, 2) else 'W' if raw in (5, 6, 7) else 'E'

        def produce_raw(raw_number):
            """
            :param raw_number: ~> dict of black cells with value of current cup
            # cell       ~> key in the raw_number dict
            # value      ~> value of the cell
            :return # raw as dict with marked checkers
                    # as W, B, E for White, Black, Empty
            """
            return {cell: value for cell, value in zip(cell_marker(raw_number),
                                                       repeat(cup_marker(raw_number)))}
        # list of rows representing initialed deck
        self.state = [produce_raw(raw_number) for raw_number in range(8)]

    def action(self, x, y):
        coordinates = self.separate(x, y)
        if coordinates['success']:
            cords = coordinates['coordinates']
            validation = self.data_valid(**cords)
            if validation['success']:
                action = self.recognize_move(**cords)
                if action['success']:
                    if action['action'] == 'move':
                        return self.move(**cords)

                    elif action['action'] == 'strike':
                        return self.strike(**cords)
                else:
                    return action
            else:
                return validation

        else:
            return coordinates

        # TODO recognize move............50/50
            # TODO recognise queen moves
        # TODO queen strike

    def separate(self, x, y):
        """
        :param x: incoming params for cell e.g. a2 b3
        :param y: incoming params for cell e.g. a2 b3
        :return: dict of separated value x_l, x_d, y_l y_d
        """
        try:
            xys = dict(
                x_l=self.LETTERS.index(x[0]),
                y_l=self.LETTERS.index(y[0]),
                x_d=int(x[1]) - 1,
                y_d=int(y[1]) - 1,
            )
            return {'success': True, 'coordinates': xys}

        except (ValueError, AttributeError):
            print(traceback.format_exc())
            return {'success': False, 'cause': 'Invalid args'}

    def data_valid(self, x_l, x_d, y_l, y_d):
        """
        :param x_d: incoming coord
        :param y_d: incoming coord
        :param x_l: incoming coord
        :param y_l: incoming coord
        :return: dict: success True or False and cause if unsuccessful
        Validating coordinates
        """
        valid_in_range = all(map(lambda x: x in range(8), [x_l, x_d, y_l, y_d]))
        if valid_in_range:
            try:
                temp = self.state[x_d][x_l], self.state[y_d][y_l]
                if self.state[x_d][x_l] == self.next_move:
                    return {'success': True}
                else:
                    return {'success': False, 'cause': 'It\'s %s turn' % (self.next_move, )}
            except KeyError:
                return {'success': False, 'cause': 'You can\'t manipulate with white cells'}
        else:
            return {'success': False, 'cause': 'Raw identifier is wrong'}

    def recognize_move(self, x_d, y_d, x_l, y_l):
        checker = self.state[x_d][x_l]
        if checker != self.next_move:
            return {'success': False, 'cause': 'It\'s %s turn' % (self.next_move, )}

        if checker in ('B', 'W'):
            diff = abs(x_d - y_d)
            if diff == 1:
                to_compare = x_d + 1 if self.next_move == 'B' else x_d - 1
                if y_d == to_compare:
                    return {'success': True, 'action': 'move'}
                else:
                    return {'success': False, 'cause': 'You can\'t move backwards'}

            elif diff == 2:
                return {'success': True, 'action': 'strike'}

            else:
                return {'success': False, 'cause': 'Move is illegal'}

        elif checker in ('BQ', 'WQ'):
            pass
            # TODO strike, move for queens
            # TODO diagonals

        else:
            return {'success': False, 'cause': 'No checker in current cell'}

    def move(self, x_d, y_d, x_l, y_l):
        checker = self.state[x_d][x_l]
        cell_to_move = self.state[y_d][y_l]
        if cell_to_move != 'E':
            return {'success': False, 'cause': 'Move to cell is not empty'}

        self.state[x_d][x_l], self.state[y_d][y_l] = 'E', checker
        self.change_next_move()
        return {'success': True, 'state': self.state}

    @staticmethod
    def strike_neighbour_cells(x):
        result = []
        if x <= 5:
            result.append(x+2)
        if x >= 2:
            result.append(x-2)
        return result

    def strike_target_cell(self, x_d, x_l, y_d,  y_l):
        avg = lambda x, y: (x + y) // 2

        striker_column_index = self.LETTERS.index(x_l)
        target_column_index = self.LETTERS.index(y_l)

        target_column = self.LETTERS[avg(striker_column_index, target_column_index)]
        target_raw = avg(x_d, y_d)
        return target_column, target_raw

    def can_strike(self, x_d, x_l):
        result = []

        striker_column_index = self.LETTERS.index(x_l)
        columns_index = self.strike_neighbour_cells(striker_column_index)
        columns = map(lambda x: self.LETTERS[x], columns_index)
        rows = self.strike_neighbour_cells(x_d)

        strike_cells = product(columns, rows)

        for i in strike_cells:
            target = self.strike_target_cell(x_d, x_l, i[1], i[0])

            target_cell = self.state[target[1]][target[0]]
            strike_cell = self.state[i[1]][i[0]]

            if strike_cell == 'E' and target_cell == self.return_opposite_move():
                result.append((
                    (target[1], target[0]),  # target cell
                    (i[1], i[0]),            # to cell
                ))

        return result

    def strike(self, x_d, x_l, y_d,  y_l):
        strike_options = self.can_strike(x_d=x_d, x_l=x_l)

        if strike_options:
            for i in strike_options:
                target_cell, to_cell = i
                if (y_d, y_l) == to_cell:
                    self.state[x_d][x_l] = 'E'
                    self.state[target_cell[0]][target_cell[1]] = 'E'
                    self.state[to_cell[0]][to_cell[1]] = self.next_move

                    if not self.can_strike(y_d, y_l):
                        self.change_next_move()

                    return {'success': True, 'state': self.state}
                else:
                    return {'success': False, 'cause': 'Illegal move'}
        else:
            return {'success': False, 'cause': 'Can not make a strike'}

    def return_opposite_move(self):
        result = ['W', 'B']
        result.remove(self.next_move)
        return result[0]

    def change_next_move(self):
        self.next_move = self.return_opposite_move()

    def neighbours_cell(self, x_d, x_l, **kwargs):
        def get_neighbour(index):
            if index in self.on_edge:
                return [abs(index - 1), ]
            else:
                return [index - 1, index + 1, ]
        return product(get_neighbour(x_l), get_neighbour(x_d))

    def diagonal_way(self, **kwargs):
        def diagonal(x, y):
            step = x - y
            while x not in self.on_edge:
                x -= step
                yield x

        rows_way = diagonal(kwargs['x_d'], kwargs['x_direction'])
        column_way = diagonal(kwargs['y_d'], kwargs['y_direction'])
        return zip(rows_way, column_way)

if __name__ == '__main__':
    board = Board()
    pprint(list(enumerate(board.state)))

    print(list(board.neighbours_cell(x_d=6, x_l=1)))
