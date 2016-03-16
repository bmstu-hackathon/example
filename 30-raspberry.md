## Raspberry Pi
Данный раздел посвящён коммуникации с Arduino и Bluemix со стороны Raspberry Pi, для чего мы напишем скрипт на python. К сожалению, придётся использовать python 2 из-за библиотеки `pi_switch`.


### Получение данных с Arduino
Для начала необходимо получить данные по радиоканалу. Вспомним формат передаваемых данных:
```
+----------+-----------+---------+
| group id | sensor id |  data   |
|  8 bits  |   8 bits  | 16 bits |
+----------+-----------+---------+
|<----------- 32 bits ---------->|
```

Для работы с радиоканалом нам потребуется использовать библиотеку `pi_switch`:
```python
from pi_switch import RCSwitchReceiver

receiver = RCSwitchReceiver()
receiver.enableReceive(2)
  ```

Так как нас интересует далеко не вся информация, необходимо перед декодированием пакета проверять номер группы:
```python
def check_group(packet):
    return (packet >> 24) == GROUP_ID
```

Так же нам потребуется функция для декодирования пакета, т.е. извлечения идентификатора датчика и данных с этого датчика. Данные с датчика хранятся в дополнительном коде, что необходимо учесть:
```python
def decode(packet):
    sid = (packet >> 16) & 0xff
    data = packet & 0xffff

    # Преобразование отрицательного значения.
    if data & 0x8000:
        data = data - 0x10000
    return sid, data
```

Взаимодействие с библиотекой происходит в неблокирующем стиле: данные накапливаются во внутреннем буфере, пока пакет не будет полностью получен, после чего данные могут быть обработаны:
```python
def receive_if_available():
    # Проверка наличия данных в буфере.
    if not receiver.available():
        return

    # Получение данных и сброс буфера.
    packet = receiver.getReceivedValue()
    receiver.resetAvailable()

    # Наш ли это пакет.
    if packet and check_group(packet):
        return decode(packet)
```


### Отправка данных в Bluemix
Для связи с Bluemix логично использовать протоколы, основанные на TCP или UDP. В данном примере используется MQTT.

После регистрации устройства в Bluemix мы получаем данные для авторизации, которые поместим в файл [device.cfg](src/device.cfg):
```ini
[device]
org=md8qpm
type=bmstu001
id=bmstu000
auth-method=token
auth-token=B!rA*o2Y9UKnCV?nTe
```

Bluemix предоставляет библиотеку ibmotf — небольшую обёртку над MQTT, инициализация соединения с которой выглядит как:
```python
import ibmiotf.device

def connect(config):
    options = ibmiotf.device.ParseConfigFile(config)
    client = ibmiotf.device.Client(options)
    client.connect()

client = connect('device.cfg')
```

После открытия соединения можно передавать данные, публикуя события:
```python
sid_to_topic = ['temperature', 'angle']

def send_data(sid, data):
    topic = sid_to_topic[sid]
    client.publishEvent(topic, 'json', data)
```

Теперь мы можем отправлять данные в облако по MQTT, получаемые с arduino по 433MHz-радиоканалу:
```python
def main():
    while True:
        payload = receive_if_available()
        if payload:
            sid, data = payload
            send_data(sid, data)
        else:
            # Если данных нет, то ждём.
            time.sleep(0.1)
```

Стоит заметить, что ждать необходимо только в отсутствии данных. Действительно, если ждать при любом исходе, то это может привести к накапливанию в буфере ненужных пакетов (полученных по ошибке) или в результате задержки на самой arduino.

### Получение данных из Bluemix
Теперь необходимо подписаться на получение данных из Bluemix:
```python
def connect(config):
    # ...
    client.commandCallback = on_message

def on_message(cmd):
    if cmd.command != 'button':
        return

    print cmd
```

При инициализации соединения библиотека создаёт отдельный поток, в котором ожидаются поступающие события, называемые командами. После получения команды вызывается наш обработчик.

Полный код доступен [здесь](src/raspberry.py).
