import http.server as HS
import socketserver
import json
from http import HTTPStatus

# Custom handler to process requests
class myHandler(HS.SimpleHTTPRequestHandler):
    tasks = []

    def do_POST(self):
        if self.path == "/tasks":
            # Get how many bytes to read
            content_length = int(self.headers["content-length"])

            # Use rfile's read method to read in the undecoded data
            data = self.rfile.read(content_length)

            # Decode the data to strings and make it into JSON format
            decoded_data = json.loads(data.decode('utf-8'))

            # Validate title, making sure that the field is there
            if 'title' not in decoded_data:
                self.send_error(HTTPStatus.BAD_REQUEST, "Missing 'title' field")
                return 

            # Create a new task
            new_task = {
                'id': len(self.tasks) + 1,
                'title': decoded_data['title'],
                'description': decoded_data.get ('description', ''),
                'status': 'Not Started'
            }

            # add new task into storage area
            self.tasks.append(new_task)

            # Prepare the response
            response = json.dumps(new_task)

            # Send response
            self.send_response(HTTPStatus.CREATED)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_GET(self):
        # If request is just tasks then get all the tasks, if followed by # then
        # get specific
        if self.path == "/tasks":
            self.get_all_tasks()
        elif self.path.startswith('/tasks/'):
            self.get_specific_task()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        
    def get_all_tasks(self):
        response = json.dumps(self.tasks)

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def get_specific_task(self):
        # self.path is just /tasks/#, so we want to split to using / to 
        # get our task #
        task_id = int(self.path.split('/')[-1])

    
        found_task = None
        for task in self.tasks:
            if task['id'] == task_id:
                found_task = task
        
        if found_task:
            response = json.dumps(found_task)

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Task not found")



PORT = 8000
handler = myHandler

with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
   print("Server at port ", PORT)
   httpd.serve_forever() 