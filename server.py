# https://www.coursera.org/learn/diving-in-python/discussions/forums/lkajRXtJEeeh0gq4yYKIVA/threads/BkiXTtjtEembnxKC4yfdRg

import socket

sock = socket.socket()
sock.bind(('127.0.0.1', 8888))
sock.listen(1)
conn, addr = sock.accept()

print('Соединение установлено:', addr)


while True:

    data = conn.recv(1024)
    if not data:
        break

    request = data.decode('utf-8')
    print(f'Получен запрос: {ascii(request)}')

    # print(f'Отправлен ответ {ascii(response.decode("utf-8"))}')
    # conn.send(response)

    if request.startswith('put '):
        conn.send('ok\n\n'.encode())
    elif request.startswith('get '):
        conn.send(b'ok\npalm.cpu 10.5 1501864247\neardrum.cpu 15.3 1501864259\neardrum.cpu 16.3 1123864259\n\n')
    else:
        conn.send('error\nunrecognized command\n\n'.encode())



conn.close()