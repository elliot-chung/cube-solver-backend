from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from rubikscube import *
from solve import solve

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def _enable_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
    
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self._enable_cors()
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self._enable_cors()
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("Cubesolver Backend", "utf-8"))
        
    def do_POST(self):
        content_type = self.headers['Content-Type']
        if content_type != 'application/json':
            self.send_response(400)
            self._enable_cors()
            self.end_headers()
            return
        
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length))
        try: 
            color_data = parse_color_input(data)
            cube_state = build_cube_state(color_data)
        except Exception as e:
            self.send_response(200)
            self._enable_cors()
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps("Invalid Cube").encode("utf-8"))
            return
        
        
        cube = Cube(cube_state)
        sequence = solve(cube)
        response = json.dumps(sequence)
        
        self.send_response(200)
        self._enable_cors()
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

        

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

