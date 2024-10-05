# -*- coding:utf-8 -*-

import socket
import threading
import uuid

"""
Active clients hashmap
Client id -> client socket

This hashmap will be used to get the list of active client ids,
and getting a client's socket for forwarding messages.

Key (String): client id
Value (Socket): client socket
"""
active_clients = {}

"""
Forwarded chat history between clients hashmap
client_id_1:client_id_2 string -> chat history string

Key (String): "client_id_1:client_id_2"
    The order of the 2 client ids in the key is determined by alphabetical order
    So, client_id_1 will always be the client id that is alphabetically first
    Example:
        "540a9d86-cd60-4fb7-ac73-40068ad442f8:71542820-29e7-424f-95f3-4bffe206e679"

Value (String): String with full chat history between clients including sender id and line returns
    Example:
        71542820-29e7-424f-95f3-4bffe206e679: Hi
        540a9d86-cd60-4fb7-ac73-40068ad442f8: Hello
"""
chat_history = {}


def link_handler(client_socket, client_address, client_id):
    # Add client id and socket to active_clients
    active_clients[client_id] = client_socket
    client_socket.sendall(f'Your ID is {client_id}'.encode())

    print(f'Server starting to receiving msg from {client_id}')

    while True:
        message = client_socket.recv(1024).decode()
        
        if message == 'exit':
            # Remove client id from clients
            del active_clients[client_id]
        
            client_socket.sendall('Goodbye'.encode())
            print(f'Ended communication with {client_id}')
            break
        elif message == 'list':
            # Get list of all active clients as a string
            active_clients_str = '\n'.join(active_clients.keys())

            client_socket.sendall(active_clients_str.encode())
            continue

        # If chat history between two clients is requested
        elif len(message) == 44 and message[:7] == 'history':
            recipient_id = message[8:49]

            if recipient_id in active_clients:
                # Make chat_history hashmap key
                if client_id < recipient_id:
                    key = f'{client_id}:{recipient_id}'
                else:
                    key = f'{recipient_id}:{client_id}'
                
                # Get chat history and send to client
                history = chat_history.get(key, None)
                if history is not None:
                    history = f'Chat history with {recipient_id}{history}'
                    client_socket.sendall(history.encode())
                else:
                    client_socket.sendall(f'No chat history with {recipient_id}'.encode())
            else:
                client_socket.sendall('Client ID not found'.encode())
            continue

        # If message is being forwarded
        elif len(message) > 37 and message[36] == ':':
            if message[:36] in active_clients:
                # Get client socket
                recipient_id = message[:36]
                recipient_socket = active_clients[recipient_id]
                
                # Add message to chat history
                message = f'\n{client_id}:{message[37:]}'
                if client_id < recipient_id:
                    key = f'{client_id}:{recipient_id}'
                else:
                    key = f'{recipient_id}:{client_id}'

                chat_history[key] = chat_history.get(key, '') + message

                # Forward message to client
                recipient_socket.sendall(message.encode())
                client_socket.sendall(f'Message sent to {recipient_id}'.encode())
            else:
                client_socket.sendall('Client ID not found'.encode())
            continue
        
        print(f'{client_id}: {message}')
        client_socket.sendall('Server received your message'.encode())
    client_socket.close()

# Create socker server
ip_port = ('127.0.0.1', 9999)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.SOCK_STREAM is tcp

sk.bind(ip_port)
sk.listen(5)
print('Started socket server!\nWaiting for clients...')

while True:
    client_socket, client_address = sk.accept()
    client_id = str(uuid.uuid4())
    print(f'Creating new connection with {client_id}')
    
    thread = threading.Thread(target=link_handler, args=(client_socket, client_address, client_id))
    thread.start()
