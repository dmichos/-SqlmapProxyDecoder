import base64
import http.server
import socketserver
import ssl
import requests
from urllib.parse import urlparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORT = 8080
CERT_FILE = "cert.pem"
KEY_FILE = "private_key.pem"


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_REQUEST(self):
        self.handle_request()

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        request_headers = self.headers
        request_method = self.command
        request_path = self.path
        content_length = int(request_headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        target_url = self.construct_target_url(request_headers)
        try:
            response = requests.request(
                request_method,
                target_url,
                headers=dict(request_headers),
                data=body,
                allow_redirects=False,
                verify=False,
            )
            decoded_content = response.text
            try:
                if len(decoded_content) % 4 == 0 and all(
                    c
                    in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
                    for c in decoded_content.strip()
                ):
                    decoded_content = base64.b64decode(decoded_content).decode("utf-8")
            except Exception as e:
                pass
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(decoded_content.encode())
        except requests.exceptions.SSLError as ssl_error:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"SSL Error")

    def construct_target_url(self, headers):
        host = headers.get("Host")
        if not host:
            raise ValueError("Host header is missing in the request.")
        scheme = "https"
        target_url = f"{scheme}://{host}{self.path}"
        return target_url


def run_proxy():
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        httpd.serve_forever()


if __name__ == "__main__":
    run_proxy()
