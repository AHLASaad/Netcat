import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
	cmd = cmd.strip()
	if not cmd:
		return
	output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
	return output.decode("utf-8")


class NetCat:
        def __init__(self, args, buffer=None):
                self.args = args
                self.buffer = buffer
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        def run(self):
                if self.args.listen:
                        self.listen()
                else:
                        self.send()

        def send(self):
                self.socket.connect((self.args.target, self.args.port))
                if self.buffer: # if we have a buffer we send it
                        self.socket.send(self.buffer)

                try: #so we can close the connection with CTRL+C
                        while True:
                                recv_len = 1
                                response = ''
                                while recv_len:
                                        data = self.socket.recv(4096)
                                        recv_len = len(data)
                                        response +=data.decode('utf-8')
                                        if recv_len < 4096: # if we receive no data  , break the loop
                                                break
                                if response: # print the response data
                                        print(response)
                                        buffer = input('> ')
                                        buffer += '\n' 
                                        self.socket.send(buffer.encode('utf-8'))
                except KeyboaardInterrup: # loop continue until CTRL+C = close the socket
                        print('User terminated.')
                        self.socket.close()
                        sys.exit()
        def listen(self):
                self.socket.bind((self.args.target, self.args.port))
                self.socket.listen(5)
                while True:
                        client_socket,_ = self.socket.accept()
                        client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                        client_thread.start()

        def handle(self, client_socket):
                if self.args.execute: # the handle method passes that command to the execute function and send the output back on the socket.
                        output = execute(self.args.execute)
                        client_socket.send(output.encode('utf-8'))

                elif self.args.upload:
                        file_buffer = b''
                        while True:
                                data = client_socket.recv(4096)
                                if data:
                                        file_buffer +=data
                                else:
                                        break
                        with open(self.args.upload, 'wb') as f:
                                f.write(file_buffer)
                        message = f'Saved file {self.args.upload}'
                        client_socket.send(message.encode('utf-8'))

                elif self.args.command:
                        cmd_buffer = b''
                        while True:
                                try:
                                        client_socket.send(b'AHLA:#> ')
                                        while '\n' not in cmd_buffer.decode('utf-8'):
                                                cmd_buffer +=client_socket.recv(64)
                                        response = execute(cmd_buffer.decode('utf-8'))
                                        if response:
                                                client_socket.send(response.encode('utf-8'))
                                        cmd_buffer = b''
                                except Exception as e:
                                        print(f'server killed {e}')
                                        self.socket.close()
                                        sys.exit()




if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='AHLA Netcat Fl3alam',
					formatter_class=argparse.RawDescriptionHelpFormatter,
					epilog=textwrap.dedent('''Example:
        netcat.py -t <ip> -p <port> -l -c <command> #Command shell 
	netcat.py -t <ip> -p <port> -l -u=<pathToFile> #Upload a file
	netcat.py -t <ip> =p <port> -l -e=<command> #execute command
	echo 'TEXT' | ./netcat.py -t <ip> -p <port> #echo text to server port <port>
	netcat.py -t <ip> -p <port> #connect to server port
	'''))
	parser.add_argument('-c', '--command', action='store_true', help='command shell')
	parser.add_argument('-e', '--execute', help='execute a command')
	parser.add_argument('-l', '--listen', action='store_true', help='listen')
	parser.add_argument('-p', '--port', type=int, default=1234, help='port to listen bydefault')
	parser.add_argument('-t', '--target', default='127.0.0.1', help='default IP')
	parser.add_argument('-u', '--upload', help='upload a file')
	args = parser.parse_args()
	if args.listen:
		buffer = ''
	else:
		buffer = sys.stdin.read()
	
	nc = NetCat(args, buffer.encode())
	nc.run()

