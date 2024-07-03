import socket

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

address = ''
port = 9050
message = input('メッセージを入力してください : ')
message_byte = message.encode('utf-8')

sock.bind((address, port))

try:
    print('sending {!r}'.format(message))
    # サーバーへのデータ送信
    sent = sock.sendto(message_byte, (server_address, server_port))
    print('Send {} bytes'.format(sent))

    # 応答を受信
    print('waiting to receive')
    data, server = sock.recvfrom(4906)
    print('receives {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()