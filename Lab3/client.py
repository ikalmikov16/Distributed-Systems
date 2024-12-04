import socket

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
coordinator_address = ('127.0.0.1', 5001)

sk.connect(coordinator_address)

# Transfer 100 A to B
message = "Transfer 100 A to B".encode()
# Add 20% of A to A and B
# message = "Add 20% of A to A and B".encode()

sk.sendall(message)
coordinator_response = sk.recv(1024).decode()
print(coordinator_response)
