import json
import os
import sys
import logging
import SimpleHTTPServer
import SocketServer
import urlparse
from datetime import datetime

import multiprocessing

from web_server.url_config import URL_CONFIG
from web_server.entities import JsonResponse, Request

from memory_corrector.memory_corrector import destroy_sessions

from urllib3.exceptions import MaxRetryError, ProtocolError

logger = logging.getLogger(__name__)

BaseHTTPRequestHandler = SimpleHTTPServer.SimpleHTTPRequestHandler


def create_handler_class(drivers, time_to_live, logs_directory=None):

    class QueueHandler(BaseHTTPRequestHandler, object):

        def __init__(self, request, client_address, server):
            super(QueueHandler, self).__init__(request, client_address, server)

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
            except IndexError:
                qs = None
                path = self.path

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
            except KeyError:
                json_data = None

            request = Request(self.path, "POST", json_data)
            response = self._dispatch(request)
            self._send_response(response)

        def do_PUT(self):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                json_data = self._get_response_dict(post_data)
            except KeyError:
                json_data = None

            url_parts = self.path.split("/")
            try:
                update_entity_id = url_parts[-1]
                path = "/".join(url_parts[0:-1]) + "/"
            except ValueError:
                update_entity_id = None
                path = self.path

            request = Request(
                path,
                "PUT",
                json_data,
                update_entity_id=update_entity_id
            )

            response = self._dispatch(request)
            self._send_response(response)

        def _get_response_dict(self, post_data):
            post_data_str = post_data.decode('UTF-8')
            return json.loads(post_data_str)

        def _dispatch(self, request):

            self._mark_dirty_and_erase()

            try:
                url_object = URL_CONFIG[request.path]
                controller = url_object.controller
                allowed_methods = url_object.allowed_methods
            except KeyError:
                logger.info("{request} failed: {reason}".format(
                    request=request,
                    reason="The end point you requested was not found."
                ))

                return JsonResponse(
                    404,
                    "The end point you requested was not found."
                )

            if not allowed_methods:
                try:
                    return controller(
                        request,
                        drivers=drivers,
                        time_to_live=time_to_live,
                    )
                except Exception as e:
                    logger.info("{request} failed: {reason}".format(
                        request=request,
                        reason=e
                    ))

                    return JsonResponse(
                        500,
                        "Unexpected Error occured while processing your request."
                    )

            if request.method not in allowed_methods:
                logger.info("{request} failed: {reason}".format(
                    request=request,
                    reason="Method not supported."
                ))

                return JsonResponse(
                    405,
                    "Method not supported."
                )

            try:
                return controller(
                    request,
                    drivers=drivers,
                    time_to_live=time_to_live,
                )
            except Exception as e:
                logger.info("{request} failed: {reason}".format(
                    request=request,
                    reason=e
                ))

                return JsonResponse(
                    500,
                    "Unexpected Error occured while processing your request."
                )

        def _send_response(self, response):
            self._set_headers(response)
            self.wfile.write(response.get_content())

        def _mark_dirty_and_erase(self):

            expired_drivers = {}

            for token, driver_details in drivers.items():

                ts_now = datetime.now()

                driver = driver_details['driver']
                ts = driver_details['ts']

                if (ts_now - ts).seconds > time_to_live and not driver_details['lock']:
                    expired_drivers[token] = driver
                    del drivers[token]

            if len(expired_drivers.keys()):
                m_corrector = multiprocessing.Process(
                    target=destroy_sessions,
                    args=(expired_drivers,)
                )
                m_corrector.start()

    return QueueHandler


class ThreadedHTTPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def run(port, time_to_live, logs_directory=None):

    drivers = {}

    logger.setLevel(logging.INFO)

    if not logs_directory:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    else:
        log_path = os.path.join(logs_directory, "web_service.log")
        logger.addHandler(logging.FileHandler(log_path))

    server_address = ('', port)

    print("Started web service at port: {}".format(port))

    handler_class = create_handler_class(drivers, time_to_live, logs_directory)
    httpd = ThreadedHTTPServer(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("shutting down server")
        httpd.server_close()
