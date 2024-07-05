import socket
import sys

def protocol_header(room_name_size, operation, state, operation_payload_size):
    return room_name_size.to_bytes(1, "big") + operation.to_bytes(1, "big") + state.to_bytes(1, "big") + operation_payload_size.to_bytes(29, "big")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = '0.0.0.0'
server_port = 9001

print('connecting to {}'.format(server_address, server_port))

try:
    sock.connect((server_address, server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

try:
    room_name = 'room_name'
    room_name_bits = room_name.encode('utf-8')
    operation = 1
    state = 1
    operation_payload = 'operation'
    operation_payload_bits = operation_payload.encode('utf-8')
    header = protocol_header(len(room_name_bits), operation, state, len(operation_payload_bits))

    sock.send(header)

finally:
    print('closing socket')
    sock.close()