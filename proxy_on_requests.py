import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import requests

logger = logging.getLogger(__name__)


class ProxyServer(ThreadingMixIn, HTTPServer):
    def serve_forever(self):
        logger.info('Serving HTTP Proxy on {} port {} ...'.format(*self.server_address))
        super().serve_forever()


class ProxyHandler(BaseHTTPRequestHandler):
    def do_request(self):
        """Handle one request"""
        # make request to an external site
        response = requests.request(self.command, self.path)

        # write headers
        self.wfile.write('{} {} {}\r\n'.format(
            self.protocol_version, response.status_code, response.reason).encode())
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()

        # write body
        self.wfile.write(response.content)
        self.wfile.flush()

        logger.info(' '.join((self.command, self.path, str(response.status_code))))

    do_GET = do_request
    do_POST = do_request
    do_PUT = do_request
    do_DELETE = do_request
    do_HEAD = do_request
    do_PATCH = do_request
    do_OPTIONS = do_request


def run():
    logging.basicConfig(level=logging.INFO, format='%(asctime).19s %(levelname)s %(funcName)s %(message)s')

    port = int(sys.argv[1]) if sys.argv[1:] else 8080
    server = ProxyServer(('', port), ProxyHandler)
    server.serve_forever()


if __name__ == '__main__':
    run()
