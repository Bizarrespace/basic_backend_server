import http.server as HS
import socketserver
import json
from http import HTTPStatus

# Custom handler to process requests
class myHandler(HS.SimpleHTTPRequestHandler):
    tasks = []
    unique_ID_map = set()
    next_id = 1

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

            # Find the next free ID starting from +1 from the last ID that worked
            # Checking in a set here is a lot faster than an array of number
            while self.next_id in self.unique_ID_map:
                self.next_id += 1

            # Once we have a free ID use it and then update next_id pointer that helps with keeping track of what ID might be free
            id = self.next_id
            self.unique_ID_map.add(id)
            self.next_id += 1
            
            new_task = {
                'id': id,
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

    def do_PUT(self):
        if (self.path.startswith('/tasks/')):
            
            # Get the id that the user wants to change
            try: 
                task_id = int(self.path.split('/')[-1])
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid task ID")
                return
            
            # Check if task_id is valid
            if task_id <= 0 or task_id > len(self.tasks):
                self.send_error(HTTPStatus.NOT_FOUND, "Invalid task ID")
                return

            # Decode the data
            content_length = int(self.headers["content-length"])
            data = self.rfile.read(content_length)
            decoded_data = json.loads(data.decode('utf-8'))

            # B/c of 0 based indexing, when the user says 2, the data that they actually want to change is in index 1
            task_index = task_id - 1

            new_task = {
                    'id': task_id,
                    'title': decoded_data['title'],
                    'description': decoded_data.get ('description', ''),
                    'status': decoded_data['status']
                }

            # Replace the task at the index with the new one from the user
            self.tasks[task_index] = new_task

            response = json.dumps(self.tasks[task_index])
            self.send_response(HTTPStatus.OK)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return 
        
    def do_DELETE(self):
        if (self.path.startswith('/tasks/')):
            # Get the id that the user wants to change
            try: 
                task_id = int(self.path.split('/')[-1])
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid task ID")
                return
            
            found_task = None
            for task in self.tasks:
                if task['id'] == task_id:
                    found_task = task
            
            if found_task:
                self.tasks.remove(found_task)
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write("Task deleted".encode())
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "Task not found")

            # Remove from ID from set
            # If the ID that was removed is less than the pointer, update the pointer to show that we have a free ID in the back
            # Or if the task_id is the last ID we just use that ID again because we just deleted it and know that it must be free
            self.unique_ID_map.remove(task_id)
            self.next_id = min(self.next_id, task_id)

    

PORT = 8000
handler = myHandler

with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
   print("Server at port ", PORT)
   httpd.serve_forever() 


# We are making a backend-api that simply has as tasks array, that shows the task name, description, and if its completed or not
# The get gets all of the tasks so just the task array, if there is an id then get the task with that specific id
# POST sends a task to the "server" in a JSON? format, the server than reads all of it, and then makes a new task object, that then 
# gets inserted into the tasks array, and then returns the task that was just inserted 
