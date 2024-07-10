import socket
import os
import base64
import json
import select
import time
import threading

# トークンリストに該当のIPアドレスとトークンの組み合わせがあるか検索する関数
def find_token_by_ip(token_list, ip_address):
    for entry in token_list:
        if entry['ip'] == ip_address:
            return True
    return False

# TCPの処理を行う関数
def handle_tcp_cilent(connection, client_address, room_info):
    try:
        print('connection from', client_address)

        while True:
            header = connection.recv(32)
            if not header:
                break
            room_name_length = int.from_bytes(header[:1], "big")
            operation = int.from_bytes(header[1:2], "big")
            state = int.from_bytes(header[3:4], "big")
            operation_payload_length = int.from_bytes(header[5:32], "big")

            room_name = connection.recv(room_name_length).decode('utf-8')
            operation_payload = connection.recv(operation_payload_length).decode('utf-8')

            # クライアントから送られてくる操作コードが0のとき
            if operation == 0:
                room_info = {}
                print('サーバ情報を初期化しました')

            # クライアントから送られてくる操作コードが1のとき
            if operation == 1:

                # 189バイトのランダムバイト列を作成
                raw_token = os.urandom(189)

                # バイト列をBase64でエンコード
                encoded_token = base64.b64encode(raw_token).decode('utf-8')

                # ルーム名とユーザー情報を登録
                # ルーム名が存在しない場合は初期化
                if room_name not in room_info:
                    room_info[room_name] = []

                room_info[room_name].append({'ip': client_address[0], 'token': encoded_token})

                # テスト用のユーザー情報
                room_info[room_name].append({'ip': '0.0.0.0', 'token': 'test'})

                # 生成したトークンとステータスコードをクライアントに送信
                operation_payload_dict = {'200': encoded_token}
                print(operation_payload_dict)
                operation_payload_json = json.dumps(operation_payload_dict)
                operation_payload_bits = operation_payload_json.encode('utf-8')
                connection.sendall(operation_payload_bits)
                print('{}を作成しました'.format(room_name))

            # クライアントから送られてくる操作コードが2のとき
            if operation == 2:

                # 189バイトのランダムバイト列を作成
                raw_token = os.urandom(189)

                # バイト列をBase64でエンコード
                encoded_token = base64.b64encode(raw_token).decode('utf-8')

                # ルーム名とユーザー情報を登録
                # ルーム名が存在しない場合は初期化
                if room_name not in room_info:
                    room_info[room_name] = []

                room_info[room_name].append({'ip': client_address[0], 'token': encoded_token})

                # テスト用のユーザー情報
                room_info[room_name].append({'ip': '0.0.0.0', 'token': 'test'})

                # 生成したトークンとステータスコードをクライアントに送信
                operation_payload_dict = {'200': encoded_token}
                operation_payload_json = json.dumps(operation_payload_dict)
                operation_payload_bits = operation_payload_json.encode('utf-8')
                connection.sendall(operation_payload_bits)

    except Exception as e:
        print('Error: ' + str(e))
    finally:
        connection.close()
        print('operation完了')

# TCPサーバーを開始する関数
def start_tcp_server(room_info):

    # TCP接続の開始
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Starting up on {} port {}'.format(server_address, tcp_server_port))

    sock_tcp.bind((server_address, tcp_server_port))

    sock_tcp.listen(1)

    while True:
        connection, client_address = sock_tcp.accept()
        client_thread = threading.Thread(target=handle_tcp_cilent, args=(connection, client_address, room_info))
        client_thread.start()

# ルームごとの情報
room_info = {}

# UDPサーバーを開始する関数
def start_udp_server(room_info):

    # AF_INETを使用し、UDPソケットを作成
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('Starting up on {} port {}'.format(server_address, udp_server_port))

    # ソケットをアドレスとポートに紐付け
    sock_udp.bind((server_address, udp_server_port))

    # タイムアウトの設定
    timeout = 100

    # 接続しているユーザー情報
    user_info = {}
    address = {}


    while True:
        print('\nwaiting to receive message')

        # selectを使って読み取り可能なソケットを監視
        ready = select.select([sock_udp], [], [])

        if ready[0]:
            # ヘッダー情報の受信
            header, address = sock_udp.recvfrom(2)
            room_name_size = int.from_bytes(header[:1], "big")
            token_size = int.from_bytes(header[1:2], "big")

            # ルーム名、トークンの受信
            room_name = sock_udp.recvfrom(room_name_size)[0].decode('utf-8')
            token = base64.b64encode(sock_udp.recvfrom(token_size)[0]).decode('utf-8')

            # トークンリストとクライアントのトークンの照合
            if find_token_by_ip(room_info[room_name], address[0]):

                # 現在時刻の取得
                current_receive_time = time.time()

                # ユーザー情報にipアドレス、ポート番号と最終メッセージ受信時刻を登録
                user_info[address] = current_receive_time

                # メッセージの受信
                message = sock_udp.recvfrom(4094)[0]

                if message:
                    for key in user_info.keys():
                        sock_udp.sendto(message, key)
                        print('sending {} {}'.format(message, key))

            else:
                print('トークンが一致しません')
        else:
            if address in user_info:

                # ユーザー情報の削除
                current_time = time.time()
                for value in user_info.values():
                    if current_time - value >= timeout:
                        print(f'No message received from {address} within the timeout period. Removing client.')
                        del user_info[address]

                # トークンの削除
                filtered_data = []
                for entry in room_info[room_name]:
                    if entry['ip'] != address[0]:
                        filtered_data.append(entry)
                        room_info[room_name] = filtered_data

if __name__ == "__main__":
    room_info = {}
    server_address = '0.0.0.0'
    tcp_server_port = 9001
    udp_server_port = 9002
    tcp_thread = threading.Thread(target=start_tcp_server, args=(room_info,))
    udp_thread = threading.Thread(target=start_udp_server, args=(room_info,))

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()
