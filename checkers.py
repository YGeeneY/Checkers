import traceback
from functools import wraps
from itertools import repeat, product
from pprint import pprint


class Board:
    LETTERS = 'abcdefgh'
    next_move = 'W'
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
                return self.recognize_move(**cords)
            else:
                return validation
        else:
            return coordinates

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

    def recognize_move(self, **kwargs):
        step = 1 if self.next_move == 'B' else -1
        to_cell_index = kwargs['y_d'], kwargs['y_l']

        current_can_strike = self.can_strike(**kwargs)
        if current_can_strike:
            for option in current_can_strike:
                if (option['y_d'], option['y_l']) == to_cell_index:
                    return self.state_changer(x_d=kwargs['x_d'], x_l=kwargs['x_l'], **option)
            return {'success': False, 'cause': 'this checker should strike first!'}
        else:
            for checker in self.all_current_move_checkers():
                if self.can_strike(**checker):
                    return {'success': False, 'cause': 'You should should strike first!'}

        for neighbour_cell in self.neighbours_cells(kwargs['x_d'], kwargs['x_l']):
            if (kwargs['x_d'] + step) == neighbour_cell[0] and to_cell_index == neighbour_cell:
                return self.move(**kwargs)

    def move(self, **kwargs):
        if self.state[kwargs['y_d']][kwargs['y_l']] == 'E':
            return self.state_changer(**kwargs)
        else:
            return {'success': False, 'cause': 'in move'}

    def can_strike(self, **kwargs):
        result = []
        for neighbour_cell in self.neighbours_cells(kwargs['x_d'], kwargs['x_l']):
            diagonal = list(self.diagonal_way(x_d_next=neighbour_cell[0], x_l_next=neighbour_cell[1], **kwargs))
            if len(diagonal) > 1:
                possible_y_d, possible_y_l = diagonal[1]
                if self.state[neighbour_cell[0]][neighbour_cell[1]] == self.return_opposite_move():
                    if self.state[possible_y_d][possible_y_l] == 'E':
                        result.append({'y_d': possible_y_d,
                                       'y_l': possible_y_l,
                                       't_d': neighbour_cell[0],
                                       't_l': neighbour_cell[1]})
        return result

    def state_changer(self, t_l=False, t_d=False, **kwargs):
        current = self.state[kwargs['x_d']][kwargs['x_l']]
        self.state[kwargs['x_d']][kwargs['x_l']] = 'E'
        self.state[kwargs['y_d']][kwargs['y_l']] = current

        if t_d and t_l:
            self.state[t_d][t_l] = 'E'
        else:
            self.change_next_move()
        return {'success': True, 'state': self.state}

    def return_opposite_move(self):
        result = ['W', 'B']
        result.remove(self.next_move)
        return result[0]

    def change_next_move(self):
        self.next_move = self.return_opposite_move()

    def neighbours_cells(self, x_d, x_l):
        def get_neighbour(index):
            if index in self.on_edge:
                return [abs(index - 1), ]
            else:
                return [index - 1, index + 1, ]
        return product(get_neighbour(x_d), get_neighbour(x_l))

    def diagonal_way(self, **kwargs):
        def diagonal(x, y):
            step = x - y
            while x in range(7):
                x -= step
                yield x

        rows_way = diagonal(kwargs['x_d'], kwargs['x_d_next'])
        column_way = diagonal(kwargs['x_l'], kwargs['x_l_next'])
        return list(zip(rows_way, column_way))

    def all_current_move_checkers(self):
        result = []
        for raw in range(len(self.state)):
            for column in self.state[raw]:
                if self.state[raw][column] == self.next_move:
                    result.append({'x_d': raw,
                                   'x_l': column})
        yield from result

if __name__ == '__main__':
    board = Board()
    pprint(list(enumerate(board.state)))
    print(board.all_current_move_checkers())
    print({'a': 1, 'b':2} == {'b':2, 'a': 1})
