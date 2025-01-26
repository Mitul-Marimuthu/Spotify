from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Received request: {self.path}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, this is a test!")

server = HTTPServer(('localhost', 8888), TestHandler)
print("Server is running at http://localhost:8888")
server.serve_forever()
