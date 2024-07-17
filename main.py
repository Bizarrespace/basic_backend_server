# Create a basic HTTP server
    # How to start HTTP server using python

import http.server as HS
import socketserver

# Custom handler to process requests the way you want
class myHandler(HS.SimpleHTTPRequestHandler):
   def do_GET(self):
      # Response code telling browser what the status is
      self.send_response(200)

      # Set the response headers so client knows what info is coming in
      self.send_header('Content-type', 'text/html')
      self.end_headers()

      # Write response body "Hello world" to the output stream (wfile)
      # String is encoded to bytes needed by HTTP 
      # Content is then displayed in client's browser
      self.wfile.write("Hellow, world".encode())


PORT = 8000
handler = myHandler

with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
   print("Server at port ", PORT)
   httpd.serve_forever() 