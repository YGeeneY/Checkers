import traceback

import tornado.ioloop
import tornado.web
import tornado.websocket
from checkers import Board
import json

from tornado.options import define, options, parse_command_line

define("port", default=8800, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("templates/index.html")


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    board = Board()

    def open(self):
        self.write_message(json.dumps({'board': self.board.state}))

    def on_message(self, message):
        try:
            message = json.loads(message)
            response = self.board.move(message['from'], message['to'])
            self.write_message(json.dumps(response))

        except ValueError:
            print(traceback.format_exc())
            self.write_message('Bad request')

    def on_close(self):
        print("WebSocket closed")


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', EchoWebSocket),
])


if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()