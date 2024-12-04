import random
import socket
from threading import Thread
import time

class Coordinator:
    def __init__(self, address):
        self.address = address
        self.socket = None
        self.participants = {}
        self.values = {}

    def start_server(self):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.bind(self.address)
        sk.listen(3)

        self.socket = sk

        # Connect with Participants
        socket_a, _ = sk.accept()
        socket_b, _ = sk.accept()

        socket_a.settimeout(3)
        socket_b.settimeout(3)

        self.participants["A"] = socket_a
        self.participants["B"] = socket_b
        
        print('Started coordinator and participant servers!\nWaiting for client request...')

        # Log bank account values
        self.get_values()
        
        # Handle client messages
        Thread(target=self.handle_client, args=()).start()
    
    def get_values(self):
        with open('Bank_A.txt', 'r') as file:
            value_a = int(file.readline())
        with open('Bank_B.txt', 'r') as file:
            value_b = int(file.readline())
        
        self.values["A"] = value_a
        self.values["B"] = value_b

        print(f"Bank A: {self.values['A']}")
        print(f"Bank B: {self.values['B']}")
    
    def handle_client(self):
        while True:
            client_socket, _ = self.socket.accept()
            message = client_socket.recv(1024).decode()
            print(f"Client request: {message}")

            if message == "Transfer 100 A to B":
                result = self.transfer().encode()
            elif message == "Add 20% of A to A and B":
                result = self.add_twenty_percent().encode()
            else:
                result = "Invalid message".encode()
            
            # Log bank account values
            self.get_values()

            # Respond to client
            client_socket.sendall(result)
            client_socket.close()

    def transfer(self):
        # Get sockets, set timeout to 1 second
        socket_a = self.participants["A"]
        socket_b = self.participants["B"]

        # Send prepare messages
        socket_a.sendall("Prepare -100".encode())
        socket_b.sendall("Prepare +100".encode())

        responses = []
        responses.append(self.receive_response(socket_a))
        responses.append(self.receive_response(socket_b))

        # Ensure they all vote commit
        if "Abort" in responses:
            socket_a.sendall("Abort".encode())
            socket_b.sendall("Abort".encode())

            return "Aborted"

        # Send commit messages until successful commit
        response = ""
        while response != "Success":
            socket_a.sendall("Commit -100".encode())
            response = self.receive_response(socket_a)
        
        response = ""
        while response != "Success":
            socket_b.sendall("Commit +100".encode())
            response = self.receive_response(socket_b)
        
        # Return success response
        return "Success"

    def add_twenty_percent(self):
        # Get sockets, set timeout to 1 second
        socket_a = self.participants["A"]
        socket_b = self.participants["B"]

        # Get 20% of A
        add_value = int(self.values["A"] * 0.2)
        
        # Send prepare messages until successful commit
        socket_a.sendall(f"Prepare +{add_value}".encode())
        socket_b.sendall(f"Prepare +{add_value}".encode())

        responses = []
        responses.append(self.receive_response(socket_a))
        responses.append(self.receive_response(socket_b))

        # Ensure they all vote commit
        if "Abort" in responses:
            socket_a.sendall("Abort".encode())
            socket_b.sendall("Abort".encode())

            return "Aborted"
        
        # Send commit messages
        response = ""
        while response != "Success":
            socket_a.sendall(f"Commit +{add_value}".encode())
            response = self.receive_response(socket_a)
        
        response = ""
        while response != "Success":
            socket_b.sendall(f"Commit +{add_value}".encode())
            response = self.receive_response(socket_b)
        
        # Return success response
        return "Success"
    
    def receive_response(self, sk):
        try:
            return sk.recv(1024).decode()  # Attempt to receive and decode data
        except socket.timeout:
            print("Socket timed out!!")
            return "Abort"

class Participant:
    def __init__(self, id, filename):
        self.id = id
        self.socket = None
        self.filename = filename
        self.value = None
        self.crash = 1

    def start_server(self):
        # Connect to coordinator
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(coordinator_address)
        self.socket = sk

        # Log value to class
        self.get_value()

        # Start thread to handle coordinator requests
        Thread(target=self.handle_coordinator_messages, args=()).start()

    def handle_coordinator_messages(self):
        while True:
            request = self.socket.recv(1024).decode()
            response = "Abort"

            if request.startswith("Prepare"):
                # Uncomment to
                # Simulate Crash before sending response ###########################################################
                # if self.id == "B":
                #     time.sleep(3)
                #     continue
                #####################################################################################################

                print(f"Node {self.id}: {request}")
                response = self.prepare(request)
                print(f"Node {self.id}: Vote {response}")
            elif request.startswith("Commit"):
                # Uncomment to
                # Simulate Crash before sending response ###########################################################
                # if self.id == "B" and self.crash > 0:
                #     self.crash -= 1
                #     time.sleep(3.5)
                #     continue
                #####################################################################################################

                print(f"Node {self.id}: {request}")
                response = self.commit(request)
                print(f"Node {self.id}: {response}")
            else:
                print(f"Node {self.id}: {response}")

            self.socket.sendall(response.encode())

    def prepare(self, request):
        response = "Abort"

        # Validate Request
        if request[8] == "+":
            response = "Commit"
        elif request[8] == "-":
            value = int(request[9:])
            if self.value >= value:
                response = "Commit"

        # Respond to Coordinator
        return response

    def commit(self, request):
        response = "Abort"

        # Validate request and write new value
        if request[7] == "+":
            value = self.value + int(request[8:])
            response = "Success"
        elif request[7] == "-":
            value = self.value - int(request[8:])
            response = "Success"

        if response == "Success":
            self.write_value(value)
            self.get_value()
        
        # Send response to Coordinator
        return response
    
    def get_value(self):
        with open(self.filename, 'r') as file:
            self.value = int(file.readline())
        
    def write_value(self, value):
        with open(self.filename, 'w') as file:
            file.write(str(value))


# Start coordinator
coordinator_address = ('10.128.0.2', 5001)
coordinator = Coordinator(coordinator_address)
Thread(target=coordinator.start_server, args=()).start()

# Connect participants to coordinator
participant_a = Participant("A", "Bank_A.txt")
participant_a.start_server()

participant_b = Participant("B", "Bank_B.txt")
participant_b.start_server()
