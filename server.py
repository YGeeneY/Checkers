import traceback

import tornado.ioloop
import tornado.web
import tornado.websocket
from checkers import Board
import json
from pprint import pprint
from tornado.options import define, options, parse_command_line

define("port", default=8800, help="run on the given port", type=int)

# we gonna store clients in dictionary..
rooms = {}


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, game_id):
        self.render("templates/index.html", path=game_id)


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    # def __init__(self, *args, **kwargs):
    #     self.player = kwargs.pop('player')
    #     self.player.socket = self
    #     self.player.left = False
    #     super(EchoWebSocket, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self, game_id):
        room = rooms.get(game_id, False)
        self.game_id = game_id
        if not room:
            rooms[game_id] = dict(game=Board(), clients=[self])
        else:
            rooms[game_id]['clients'].append(self)
        self.write_message(json.dumps(rooms[game_id]['game'].serialize()))

    def on_message(self, message):
        try:
            message = json.loads(message)
            response = rooms[self.game_id]['game'].action(message['from'], message['to'])
            for client in rooms[self.game_id]['clients']:
                client.write_message(json.dumps(response))

        except ValueError:
            print(traceback.format_exc())
            self.write_message('Bad request')

    def on_close(self):
        rooms[self.game_id]['clients'].remove(self)
        pprint(rooms)


settings = {'auto_reload': True, 'debug': True}
app = tornado.web.Application([
    (r'/(?P<game_id>\d\d\d\d\d)', IndexHandler),
    (r'/websocket/(?P<game_id>\d\d\d\d\d)', EchoWebSocket),
], **settings)


if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()