import tornado.options
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import os
from app import create_app

app = create_app('production')

log_path = os.path.abspath('./log/app.log')

tornado.options.options.log_file_prefix = log_path
tornado.options.parse_command_line()

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(80)
IOLoop.instance().start()
