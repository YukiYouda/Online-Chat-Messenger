import socket
import select
import time

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

print('Starting up on {} port {}'.format(server_address, server_port))

# ソケットをアドレスとポートに紐付け
sock.bind((server_address, server_port))

# 接続しているユーザー情報
user_name = ''
user_info = {}
last_message_time = {}

# タイムアウトの設定
timeout = 100

while True:
    print('\nwaiting to receive message')

    # selectを使って読み取り可能なソケットを監視
    ready = select.select([sock], [], [], timeout)

    if ready[0]:
        header, address = sock.recvfrom(1)
        username_length = int.from_bytes(header[:1], "big")
        user_name = sock.recvfrom(username_length)[0].decode('utf-8')

        # ユーザー情報の登録
        user_info[user_name] = address

        # メッセージの受信
        message = sock.recvfrom(4096)[0]

        # 現在の時刻を取得
        current_receive_time = time.time()

        # 最終メッセージ受信時刻を更新
        last_message_time[address] = current_receive_time

        if message:
            for value in user_info.values():
                sock.sendto(message, value)
                print('sending {} {}'.format(message, value))
        print(user_info)
    else:
        if user_name in user_info:
            current_time = time.time()
            for client_address, last_time in list(last_message_time.items()):
                if current_time - last_time >= timeout:
                    print(f'No message received from {client_address} within the timeout period. Removing client.')
                    del last_message_time[client_address]
                    del user_info[user_name]