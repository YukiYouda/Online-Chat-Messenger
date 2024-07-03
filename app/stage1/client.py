import socket

def protocol_header(username_length):
    return username_length.to_bytes(1, "big")

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

address = ''
port = 9050

user_name = input('ユーザー名を入力してください : ')
user_name_bits = user_name.encode('utf-8')

sock.bind((address, port))

message = input('メッセージを入力してください : ')
message_bits = message.encode('utf-8')

try:
    print('sending {!r}'.format(message))
    # ヘッダー情報の作成
    header = protocol_header(len(user_name_bits))
    print(header)

    # ヘッダーの送信
    sock.sendto(header, (server_address, server_port))

    # サーバーへユーザーネームの送信
    sock.sendto(user_name_bits, (server_address, server_port))

    # サーバーメッセージの送信
    sock.sendto(message_bits, (server_address, server_port))

    # 応答を受信
    print('waiting to receive')
    data, server = sock.recvfrom(4906)
    print('receives {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()