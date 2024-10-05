# -*- coding:utf-8 -*-

import socket
import threading

ip_port = ('127.0.0.1', 9999)
stop_thread = False

# Create the socket and connect to the server
s = socket.socket()
s.connect(ip_port)

# Function to receive messages from the server
def receive_messages():
    while not stop_thread:
        server_reply = s.recv(1024).decode()
        print(f'\n{server_reply}')
        if server_reply != 'Goodbye':
            print('\nEnter message: ', end='', flush=True)
            

# Start a thread to handle receiving messages from the server
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

# Main loop for sending messages
while True:
    message = input('').strip()
    if not message:
        continue
    s.sendall(message.encode())

    if message == 'exit':
        stop_thread = True
        thread.join()
        print('Communication ended!')
        break

s.close()

