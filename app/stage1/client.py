import socket
import time
import threading

def recieve_response(sock):
    while True:
        try:
            data, server = sock.recvfrom(4906)
            print('\nreceives {!r}'.format(data))
        except Exception as e:
            print(f'\n予期しないエラーが発生しました: {e}')
            break

def protocol_header(username_length):
    return username_length.to_bytes(1, "big")

# AF_INETを使用し、UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001

address = ''
port = 9051

user_name = input('ユーザー名を入力してください : ')
user_name_bits = user_name.encode('utf-8')

sock.bind((address, port))

# タイムアウトの設定
timeout = 100
last_send_time = time.time()

# 応答受信用スレッドの開始
thread = threading.Thread(target=recieve_response, args=(sock,))
thread.daemon = True
thread.start()

while True:
    message = input('メッセージを入力してください : ')
    message_bits = message.encode('utf-8')
    message_bits_length = len(message_bits)

    # 4096バイト以上のメッセージは送信できないようにする
    if message_bits_length > 4096:
        print('メッセージの最大は4096バイトです')
        continue

    # messageの送信時間
    current_time = time.time()

    # 一定時間経過したかどうかチェック
    if current_time - last_send_time >= timeout:
        print('タイムアウトです')
        sock.close()
        break

    try:
        print('sending {!r}'.format(message))
        # ヘッダー情報の作成
        header = protocol_header(len(user_name_bits))
        print(header)

        # サーバーへヘッダーの送信
        sock.sendto(header, (server_address, server_port))

        # サーバーへユーザーネームの送信
        sock.sendto(user_name_bits, (server_address, server_port))

        # サーバーへメッセージの送信
        sock.sendto(message_bits, (server_address, server_port))

        # 最後の送信時間を更新
        last_send_time = current_time

    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        print('closing socket')
        sock.close()