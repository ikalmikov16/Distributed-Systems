import socket

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# coordinator_address = ('10.128.0.2', 5001)
coordinator_address = ('127.0.0.1', 5001)

sk.connect(coordinator_address)

# Transfer 100 A to B ############################
request = "Transfer 100 A to B"

# Add 20% of A to A and B ########################
# request = "Add 20% of A to A and B"

sk.sendall(request.encode())
print(f"Request sent: {request}")

coordinator_response = sk.recv(1024).decode()
print(coordinator_response)
