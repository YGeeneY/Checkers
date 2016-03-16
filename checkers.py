import traceback
from itertools import repeat
from string import ascii_letters


class Board:
    LETTERS = ascii_letters[:8]
    next_move = 'W'

    def __init__(self):
        def cell_marker(raw):
            """
            :param raw: raw number
            :return: list of black cells for current raw
            """
            return 'aceg' if (raw + 1) % 2 else 'bdfh'

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
        # list of raws representing initialed deck
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
                        return 'make a move'
                    elif action['action'] == 'strike':
                        return 'make a strike'
                else:
                    return action
            else:
                return validation

        else:
            return coordinates

        # TODO recognize move............50/50
            # TODO recognise queen moves
        # TODO move
        # TODO queen move
        # TODO multi strike
        # TODO multi queen strike
        # TODO state changer

    def move(self, x_d, y_d, x_l, y_l):
        pass

    def recognize_move(self, x_d, y_d, x_l, y_l):
        checker = self.state[x_d][x_l]
        if checker != self.next_move:
            return {'success': False, 'cause': 'It\'s %s turn' % (self.next_move, )}

        if checker in ('B', "W"):
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

    @staticmethod
    def separate(x, y):
        """
        :param x: incoming params for cell e.g. a2 b3
        :param y: incoming params for cell e.g. a2 b3
        :return: dict of separated value x_l, x_d, y_l y_d
        """
        try:
            xys = dict(
                x_l=x[0],
                y_l=y[0],
                x_d=int(x[1]) - 1,
                y_d=int(y[1]) - 1,
            )
            return {'success': True, 'coordinates': xys}

        except (ValueError, AttributeError):
            print(traceback.format_exc())
            return {'success': False, 'cause': 'Invalid args'}

    def data_valid(self, x_d, y_d, x_l, y_l):
        """
        :param x_d: incoming coord
        :param y_d: incoming coord
        :param x_l: incoming coord
        :param y_l: incoming coord
        :return: dict success and cause if unsuccessful
        Validating coordinates
        """
        if x_d in range(8) and y_d in range(8):
            if x_l in self.LETTERS and y_l in self.LETTERS:
                return {'success': True}
            else:
                return {'success': False, 'cause': 'Column identifier is wrong'}
        else:
            return {'success': False, 'cause': 'Raw identifier is wrong'}

    # def move(self, x, y, queen=False):
    #     if queen:
    #         pass
    #         # TODO queen logic

        # else:
        #     if y_l in self.neighbour(x_l):
        #         if self.state[x_d][x_l][0] == self.next_move:
        #             if self.state[y_d][y_l] == 'E':
        #                 to_compare = x_d + 1 if self.next_move == 'B' else x_d - 1
        #
        #                 if y_d == to_compare:
        #                     return True

    # def move(self, x, y):
    #     try:
    #         x_l = x[0]
    #         y_l = y[0]
    #         x_d = int(x[1]) - 1
    #         y_d = int(y[1]) - 1
    #     except:
    #         print(traceback.format_exc())
    #         return False
    #
    #     if self.check(x_l, x_d, y_l, y_d):
    #         self.state[x_d][x_l] = 'E'
    #         self.state[y_d][y_l] = self.next_move
    #         self.switch_user(self.next_move)
    #         return {'success': True,
    #                 'board': self.state}
    #
    #     return {'success': False}
    #
    # def switch_user(self, user):
    #     if user == 'B':
    #         self.next_move = 'W'
    #     else:
    #         self.next_move = 'B'
    #
    # def check(self, x_l, x_d, y_l, y_d):
    #     if x_d in range(8) and y_d in range(8) and x_l in self.LETTERS and y_l in self.LETTERS:
    #         if y_l in self.neighbour(x_l):
    #             if self.state[x_d][x_l][0] == self.next_move:
    #                 if self.state[y_d][y_l] == 'E':
    #                     to_compare = x_d + 1 if self.next_move == 'B' else x_d - 1
    #
    #                     if y_d == to_compare:
    #                         return True
    #     return False
    #
    # def neighbour(self, letter):
    #
    #     position = self.LETTERS.index(letter)
    #     if not position or position == 7:
    #         neighbours = [self.LETTERS[abs(position - 1)], ]
    #     else:
    #         neighbours = [self.LETTERS[position - 1], self.LETTERS[position + 1], ]
    #     return neighbours


if __name__ == '__main__':
    board = Board()
    from time import time
    start = time()
    a = board.action('a3', 'b4')
    print(a, time() - start)

