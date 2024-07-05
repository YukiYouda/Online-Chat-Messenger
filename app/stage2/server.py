import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001

print('Starting up on {} port {}'.format(server_address, server_port))

sock.bind((server_address, server_port))

sock.listen(1)

while True:
    conneciton, client_address = sock.accept()
    try:
        print('connection from', client_address)
        header = conneciton.recv(32)
        print(header)

    except Exception as e:
        print('Error: ' + str(e))

    finally:
        print("Closing current connection")
        conneciton.close()