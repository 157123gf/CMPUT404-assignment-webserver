#  coding: utf-8 
import os
import socketserver
import mimetypes




# Copyright 2023 Luofan Peng
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/



#Author: Luofan Peng


class MyWebServer(socketserver.BaseRequestHandler):


    def send_response(self, status_code, content, content_type='text/html'):
        response = f"HTTP/1.1 {status_code} {self.get_status_text(status_code)}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += "\r\n"
        response += content
        self.request.sendall(response.encode('utf-8'))

    def get_status_text(self, status_code):
        return {
            200: 'OK',
            301: 'Moved Permanently',
            404: 'Not Found',
            405: 'Method Not Allowed'
        }.get(status_code, '')

    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8")
        print("Got a request of: %s\n" % self.data)

        lines = self.data.splitlines()
        method, path, version = lines[0].split(' ')

        if method not in ['GET']:
            self.send_response(405, "Method Not Allowed")
            return
        www_dir = os.path.join(os.getcwd(), 'www')
        file_path = os.path.join(www_dir, path.lstrip('/'))

        # Security Check
        if not self.is_safe_path(www_dir, file_path):
            self.send_response(404, 'Not Found')
            return        

        www_dir = os.path.join(os.getcwd(), 'www')
        file_path = os.path.join(www_dir, path.lstrip('/'))

        if os.path.isdir(file_path):
            if not path.endswith('/'):
                new_location = path + '/'
                self.send_response(301, f'<a href="{new_location}">Moved Permanently</a>', content_type='text/html')
                return
            file_path = os.path.join(file_path, 'index.html')

        if not os.path.exists(file_path) or not file_path.startswith(www_dir):
            self.send_response(404, 'Not Found')
            return

        with open(file_path, 'r') as file:
            content = file.read()
            content_type = mimetypes.guess_type(file_path)[0] or 'text/html'
            self.send_response(200, content, content_type)
            
    def is_safe_path(self, base_dir, path):
        absolute_path = os.path.abspath(path)
        return absolute_path.startswith(os.path.abspath(base_dir))
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
