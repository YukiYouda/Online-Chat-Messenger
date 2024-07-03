import socket
import os
from pathlib import Path

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

print('Starting up on {} port {}'.format(server_address, server_port))

# ソケットをアドレスとポートに紐付け
sock.bind((server_address, server_port))

while True:
    print('\nwaiting to receive message')
    header, address = sock.recvfrom(1)
    username_length = int.from_bytes(header[:1], "big")

    print(sock.recvfrom(username_length)[0].decode('utf-8'))

    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data:
        sent = sock.sendto(data, address)
        print('sent {} bytes back to {}'.format(sent, address))