import traceback
from itertools import repeat, product
from pprint import pprint

import time


class Board:
    LETTERS = 'abcdefgh'
    next_move = 'W'
    off_board = {'B': 0, 'W': 0}

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
    # TODO initialize from kwargs

    def action(self, x, y, **kwargs):
        self.start = time.time()
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

        except (ValueError, AttributeError, IndexError):
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
                if self.state[x_d][x_l][0] == self.next_move:
                    return {'success': True}
                else:
                    return {'success': False, 'cause': 'It\'s %s turn' % (self.next_move, )}
            except KeyError:
                return {'success': False, 'cause': 'You can\'t manipulate with white cells'}
        else:
            return {'success': False, 'cause': 'Raw identifier is wrong'}

    def recognize_move(self, **kwargs):
        if self.state[kwargs['x_d']][kwargs['x_l']][-1] == 'Q':
            return self.recognize_queen_move(**kwargs)

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

        for neighbour_cell in self.neighbours_cells(**kwargs):
            if (kwargs['x_d'] + step) == neighbour_cell[0] and to_cell_index == neighbour_cell:
                return self.move(**kwargs)

        return {'success': False, 'cause': 'Illegal move'}

    def recognize_queen_move(self, **kwargs):
        to_cell_index = (kwargs['y_d'], kwargs['y_l'])
        neighbours = self.neighbours_cells(**kwargs)
        for neighbour in neighbours:
            diagonal = self.diagonal_way(x_d_next=neighbour[0], x_l_next=neighbour[1], **kwargs)
            if to_cell_index in diagonal:
                active_diagonal = diagonal[:diagonal.index(to_cell_index) + 1]
                enemies = list(map(lambda x: self.state[x[0]][x[1]] in self.enemies(), active_diagonal))

                if any(enemies):
                    if enemies.count(True) == 1 and self.state[active_diagonal[-1][0]][active_diagonal[-1][1]] == 'E':
                        # TODO BUG POSSIBLE ! map all e active_diagonal[enemies.i:]
                        t_d, t_l = active_diagonal[enemies.index(True)]
                        return self.state_changer(t_d=t_d, t_l=t_l, **kwargs)
                    else:
                        return {'success': False, 'cause': 'More than 1 enemy in a diagonal'}

                for cell in active_diagonal:
                    if self.state[cell[0]][cell[1]] in self.alliance():
                        return {'success': False, 'cause': 'Alliance is on the way'}
                return self.state_changer(**kwargs)

        return {'success': False, 'cause': 'Invalid move'}

    def move(self, **kwargs):
        if self.state[kwargs['y_d']][kwargs['y_l']] == 'E':
            return self.state_changer(**kwargs)
        else:
            return {'success': False, 'cause': 'in move'}

    def can_strike(self, **kwargs):
        result = []
        for neighbour_cell in self.neighbours_cells(**kwargs):
            diagonal = list(self.diagonal_way(x_d_next=neighbour_cell[0], x_l_next=neighbour_cell[1], **kwargs))
            if len(diagonal) > 1:
                possible_y_d, possible_y_l = diagonal[1]
                if self.state[neighbour_cell[0]][neighbour_cell[1]] in self.enemies():
                    if self.state[possible_y_d][possible_y_l] == 'E':
                        result.append({'y_d': possible_y_d,
                                       'y_l': possible_y_l,
                                       't_d': neighbour_cell[0],
                                       't_l': neighbour_cell[1]})
        return result

    def state_changer(self, t_l=False, t_d=False, **kwargs):
        current = self.state[kwargs['x_d']][kwargs['x_l']]
        if (kwargs['y_d'] == 7 and current == 'B') or (not kwargs['y_d'] and current == 'W'):
            current += 'Q'
        self.state[kwargs['x_d']][kwargs['x_l']] = 'E'
        self.state[kwargs['y_d']][kwargs['y_l']] = current

        if t_d and t_l:
            self.state[t_d][t_l] = 'E'
            self.off_board[self.return_opposite_move()] += 1
            if not self.can_strike(x_d=kwargs['y_d'], x_l=kwargs['y_l']):
                self.change_next_move()
        else:
            self.change_next_move()
        return self.serialize()

    def return_opposite_move(self):
        result = ['W', 'B']
        result.remove(self.next_move)
        return result[0]

    def enemies(self):
        enemy = self.return_opposite_move()
        return [enemy, enemy+'Q']

    def alliance(self):
        return [self.next_move, self.next_move + 'Q']

    def change_next_move(self):
        self.next_move = self.return_opposite_move()

    @staticmethod
    def neighbours_cells(**kwargs):
        def get_neighbour(index):
            if index in (0, 7):
                return [abs(index - 1), ]
            else:
                return [index - 1, index + 1, ]
        return product(get_neighbour(kwargs['x_d']), get_neighbour(kwargs['x_l']))

    @staticmethod
    def diagonal_way(**kwargs):
        def diagonal(x, y):
            step = x - y
            while x in range(8):
                yield x
                x -= step

        rows_way = diagonal(kwargs['x_d'], kwargs['x_d_next'])
        column_way = diagonal(kwargs['x_l'], kwargs['x_l_next'])
        return list(zip(rows_way, column_way))[1:]

    def all_current_move_checkers(self):
        for raw in range(len(self.state)):
            for column in self.state[raw]:
                if self.state[raw][column] == self.next_move:
                    yield {'x_d': raw, 'x_l': column}

    def serialize(self):
        if hasattr(self, 'start'):
            print((time.time() - self.start)*1000, ' ms')
        for key in self.off_board:
            if self.off_board[key] == 12:
                return {'success': False, 'cause': 'Game over beaches'}
        return dict(
            success=True,
            state=self.state,
            next_move=self.next_move,
            off_board=self.off_board
        )

if __name__ == '__main__':
    board = Board()
    pprint(list(enumerate(board.state)))
