import json
import os
import sys
import logging
import uuid
import SimpleHTTPServer
import SocketServer
import urlparse

import multiprocessing

from web_server.url_config import URL_CONFIG
from web_server.entities import Response, Request

logger = logging.getLogger(__name__)

BaseHTTPRequestHandler = SimpleHTTPServer.SimpleHTTPRequestHandler


def create_handler_class(q, logs_directory=None):
    class QueueHandler(BaseHTTPRequestHandler, object):

        def __init__(self, request, client_address, server):
            super(QueueHandler, self).__init__(request, client_address, server)
            self.q = q

            if logs_directory:
                request_log_path = os.path.join(logs_directory, "request.log")
                file_handle = open(request_log_path, 'w')
                sys.stdout = file_handle

        def _set_headers(self, response):
            self.send_response(response.code)
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()

        def do_GET(self):
            try:
                url_parts = self.path.split("?")
                qs = url_parts[1]
                path = url_parts[0]
            except IndexError as e:
                qs = None

            data = None
            if qs:
                data = urlparse.parse_qs(qs)

            request = Request(path, "GET", data)

            response = self._dispatch(request)
            self._send_response(response)

        def do_POST(self):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                json_data = self._get_response_dict(post_data)
            except KeyError as e:
                json_data = None

            request = Request(self.path, "POST", json_data)
            response = self._dispatch(request)
            self._send_response(response)

        def _get_response_dict(self, post_data):
            post_data_str = post_data.decode('UTF-8')
            return json.loads(post_data_str)

        def _get_id(self):
            return uuid.uuid4().hex

        def _dispatch(self, request):
            try:
                controller = URL_CONFIG[request.path]
                return controller(request)
            except KeyError as e:
                return Response(
                    404,
                    "The end point you requested was not found."
                )

        def _send_response(self, response):
            self._set_headers(response)
            self.wfile.write(response.get_content())

    return QueueHandler


def run(q, port, logs_directory):

    logger.setLevel(logging.INFO)

    if not logs_directory:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    else:
        log_path = os.path.join(args.logs_directory, "mailer.log")
        logger.addHandler(logging.FileHandler(log_path))

    server_address = ('', port)

    handler_class = create_handler_class(q, logs_directory)
    httpd = SocketServer.TCPServer(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    q = multiprocessing.Queue()
    run(q, 9999, None)