import socket as socket_lib
import time

# класс для кастомных исключений
class ClientError(BaseException):
    pass

# ответ сервера, просто структура для хранения
class ServerResponse:
    def __init__(self, status, data):
        self.status = status
        self.data = data

    @property
    def has_error(self):
        return self.status == 'error'

    def __str__(self):
        return f'status: {self.status}\ndata: {self.data}'


# парсер ответов сервера
class ServerResponseParser:

    # индекс заголовка, всё, что после - считаем телом сообщения
    IDX_HEADER = 0
    # минимальное число строк в ответе, чтобы считаться валидным
    MIN_LINES = 1

    @staticmethod
    def from_binary(data):
        # преобразуем бинарщину в текст и разобьём на строки
        text = data.decode('utf-8')
        lines = text.strip().split('\n')
        # если пришло меньше, чем мы решили считать нормальным - ругаемся
        if len(lines) < ServerResponseParser.MIN_LINES:
            print(len(lines))
            raise ClientError('wrong answer format')
        # формируем структуру ответа, здесь возможен более сложный парсинг
        response = ServerResponse(lines[ServerResponseParser.IDX_HEADER], lines[ServerResponseParser.IDX_HEADER + 1:])
        return response


class Client:

    def __init__(self, host, port, timeout=None, buff_size=4096):

        # зададим размер буффера как аттрибут, чтобы не хардкодить
        self.buff_size = buff_size
        # инстанс сокета
        self.connection = socket_lib.socket()
        # таймаут
        if timeout is not None:
            self.connection.settimeout(timeout)
        # сразу же пытаемся подключиться
        try:
            self.connection.connect((host, port))
        except BaseException:
            raise ClientError('connection failed')
        pass

    # обёртка, чтобы не повторяться
    def _send(self, message):
        try:
            self.connection.sendall(message.encode())
        except BaseException:
            raise ClientError('something went wrong')

    # обёртка, чтобы не повторяться
    def _recv(self):
        data = self.connection.recv(self.buff_size)
        if not data:
            raise ClientError('server doesn\'t answer')
        # прочитали бинарщину - хотим получить ответ в структуре
        response = ServerResponseParser.from_binary(data)
        return response

    def command(self, message):
        # отправляем сообщение
        print(f' >> {message.strip()}')
        self._send(message)
        # читаем ответ
        response = self._recv()
        print(f' << {response.status}')
        # если в ответе статус ошибки - выбросим исключение,
        # по-хорошему это надо делать иначе - статус оговорит об ошибке, но это не исключение,
        # а часть нормального общения по протоколу, но для учебного примера - пойдёт
        if response.has_error:
            raise ClientError(f'some "get" errors: {"".join(response.data)}')
        return response
        pass

    def put(self, metric, value, timestamp=None):
        # формируем сообщение
        if timestamp is None:
            timestamp = int(time.time())
        response = self.command(f'put {metric} {value} {timestamp}\n')
        return response
        pass

    def get(self, metric='*'):
        # получаем ответ как обычно
        response = self.command(f'get {metric}\n')
        # а дальше парсим его в нужный нам формат

        idx_key, idx_value, idx_time = 0, 1, 2

        result = {}
        for line in response.data:
            values = line.split(sep=' ')
            if values[idx_key] not in result:
                result[values[idx_key]] = []
            try:
                result[values[idx_key]].append((int(values[idx_time]), float(values[idx_value])))
            except BaseException:
                raise ClientError("stored metrics format error")
        for key in result.keys():
            result[key] = sorted(result[key], key=lambda x: x[0])
        return result


def do_stuff(name):
    # создаём клиент
    client = Client('127.0.0.1', 8888, timeout=15)
    client.put("palm.cpu", 0.5, timestamp=1150864247)
    client.put("palm.cpu", 2.0, timestamp=1150864248)
    client.put("palm.cpu", 0.5, timestamp=1150864248)
    client.put("eardrum.cpu", 3, timestamp=1150864250)
    client.put("eardrum.cpu", 4, timestamp=1150864251)
    client.put("eardrum.memory", 4200000)

    # хранение на сервере не реализовано - по условиям задачи реализуем только клиент
    stored = client.get("something")
    print('stored metrics:')
    print(stored)

    # потестируем получение ошибки
    client.command("zzzzzzz")


if __name__ == '__main__':
    do_stuff('PyCharm')
