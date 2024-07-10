import socket
import sys
import math
import json
import base64
import threading
import time

# TCP通信のヘッダー作成用の関数
def protocol_tcp_header(room_name_size, operation, state, operation_payload_size):
    return room_name_size.to_bytes(1, "big") + operation.to_bytes(1, "big") + state.to_bytes(1, "big") + operation_payload_size.to_bytes(29, "big")

# UDP通信のヘッダー作成用の関数
def protocol_udp_header(room_name_size, token_size):
    return room_name_size.to_bytes(1, "big") + token_size.to_bytes(1, "big")

# サーバーからの返信受け取り用の関数
def recieve_response(sock):
    while True:
        try:
            data, server = sock.recvfrom(4096)
            print('\nreceives {!r}'.format(data))
        except Exception as e:
            print(f'\n予期しないエラーが発生しました: {e}')
            break

sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = '0.0.0.0'
tcp_server_port = 9001
udp_sever_port = 9002

print('connecting to {}'.format(server_address, tcp_server_port))

try:
    sock_tcp.connect((server_address, tcp_server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

token = ''
room_name = ''

try:
    while True:
        operation = int(input('操作コードを入力してください : '))

        # 操作コードが0のとき
        if operation == 0:
            user_name = input('ユーザー名を入力してください : ')
            room_name = ''
            room_name_bits = room_name.encode('utf-8')
            state = 0
            operation_payload = user_name
            operation_payload_bits = operation_payload.encode('utf-8')
            header = protocol_tcp_header(len(room_name_bits), operation, state, len(operation_payload_bits))

            # サーバーにヘッダーの送信
            sock_tcp.send(header)

            # サーバーにルーム名の送信
            sock_tcp.send(room_name_bits)

            # サーバーにopreration_payloadの送信
            sock_tcp.send(operation_payload_bits)

        # 操作コードが1のとき(ルームの新規作成)
        if operation == 1:
            room_name = input('作成するルーム名を入力してください : ')
            room_name_bits = room_name.encode('utf-8')
            state = 0
            operation_payload = ''
            operation_payload_bits = operation_payload.encode('utf-8')
            header = protocol_tcp_header(len(room_name_bits), operation, state, len(operation_payload_bits))

            # サーバーにヘッダーの送信
            sock_tcp.send(header)

            # サーバーにルーム名の送信
            sock_tcp.send(room_name_bits)

            # サーバーにopreration_payloadの送信
            sock_tcp.send(operation_payload_bits)

            # サーバーからの応答を受信
            data = json.loads(sock_tcp.recv(int(math.pow(2, 29))).decode('utf-8'))
            print(data)
            token = data['200']

            # tcp接続を閉じる
            sock_tcp.close()
            break

        # 操作コードが2のとき(既存のルームに参加)
        if operation == 2:
            room_name = input('参加するルーム名を入力してください : ')
            room_name_bits = room_name.encode('utf-8')
            state = 0
            operation_payload = ''
            operation_payload_bits = operation_payload.encode('utf-8')
            header = protocol_tcp_header(len(room_name_bits), operation, state, len(operation_payload_bits))

            # サーバーにヘッダーの送信
            sock_tcp.send(header)

            # サーバーにルーム名の送信
            sock_tcp.send(room_name_bits)

            # サーバーにopreration_payloadの送信
            sock_tcp.send(operation_payload_bits)

            # サーバーからの応答を受信
            data = json.loads(sock_tcp.recv(int(math.pow(2, 29))).decode('utf-8'))
            token = data['200']

            # tcp接続を閉じる
            sock_tcp.close()
            break

finally:
    print('closing tcp_socket')
    sock_tcp.close()

# ここからUDP接続の処理

# AF_INETを使用し、UDPソケットを作成
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ''
port = 9051

sock_udp.bind((address, port))

# タイムアウトの設定
timeout = 100
last_send_time = time.time()

# 応答受信用スレッドの開始
thread = threading.Thread(target=recieve_response, args=(sock_udp,))
thread.daemon = True
thread.start()

while True:
    message = input('メッセージを入力してください : ')
    message_bits = message.encode('utf-8')
    message_bits_length = len(message_bits)

    # 4094バイト以上のメッセージは送信できないようにする
    if message_bits_length > 4094:
        print('メッセージの最大は4094バイトです')
        continue

    # messageの送信時間
    current_time = time.time()

    # 一定時間経過したかどうかチェック
    if current_time - last_send_time >= timeout:
        print('タイムアウトです')
        sock_udp.close()
        break

    try:
        print('sending {!r}'.format(message))
        # ヘッダー情報の作成
        room_name_bits = room_name.encode('utf-8')
        header = protocol_udp_header(len(room_name_bits), len(token))

        # サーバーへヘッダーの送信
        sock_udp.sendto(header, (server_address, udp_sever_port))

        # サーバーへルーム名の送信
        sock_udp.sendto(room_name_bits, (server_address, udp_sever_port))

        # サーバーへトークン文字列の送信
        sock_udp.sendto(base64.b64decode(token), (server_address, udp_sever_port))

        # サーバーへメッセージの送信
        sock_udp.sendto(message_bits, (server_address, udp_sever_port))

        # 最後の送信時間の更新
        last_send_time = current_time

    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        print('closing socket')
        sock_udp.close()