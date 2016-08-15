# -*- encoding: utf-8 -*-
#

import sys
import time
import struct
import logging
import socket
import threading
import random
import StringIO

HOST = "127.0.0.1"
PORT = 8083

# 并发连接数
CONNECTIONS  = 200

# 每个连接发送消息间隔时间，单位秒
MSG_INTERVAL = 5

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(thread)-8d %(message)s', level=logging.DEBUG)
log = logging.getLogger("SocketTest")

def encodeFrame(d):
    """
    @param d dict, keys maybe:
        FIN: FIN
        opCode: type of payloadData
        length: length of payloadData
        payloadData: the real data to send
        maskingKey: list of 4 unsigned chars, optional

    See http://tools.ietf.org/html/rfc6455

    """
    k = (1 if 'maskingKey' in d else 0)
    s = StringIO.StringIO()
    s.write(struct.pack('B', (d['FIN'] << 7) + d['opCode']))
    l = d['length']
    if l < 126:
        s.write(struct.pack('B', (k << 7) + l))
    elif (l < 0x10000):
        s.write(struct.pack('B', (k << 7) + 126))
        s.write(struct.pack('>H', l))
    else:
        s.write(struct.pack('B', (k << 7) + 127))
        s.write(struct.pack('>Q', l))

    if k:
        i = 0
        while i < 4:
            s.write(struct.pack('B', d['maskingKey'][i]))
            i += 1
        i = 0
        while i < l:
            s.write(struct.pack('B', struct.unpack('B', d['payloadData'][i])[0] ^ d['maskingKey'][i % 4]))
            i += 1
    else:
        s.write(d['payloadData'])
    s.seek(0)
    content = s.read()
    s.close()
    return content

def decodeFrame(d):
    return d

class PluginThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name="SocketTest")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            self.sock = None
            log.error("Error create socket: %s", msg)
        if self.sock is None:
            return
        try:
            self.sock.connect((HOST, PORT))
        except Exception as msg:
            self.sock = None
            log.error("Error connect socket: %s", msg)

    def run(self):
        count = 0
        log.debug("SocketTest thread started")
        self.connect()
        while (True):
            self.sendmsg(('测试消息' * 10) + str(random.randint(0,10000)))
            time.sleep(MSG_INTERVAL)
            count += 1
            if count >= 10:
                break
        self.sendclose()
        self.sock.close()
        log.debug("SocketTest thread finished")

    def connect(self):
        content = "GET /websocket/?request=eyJpZCI6MTg1NjYyMjQxMjA2MDMxOSwiYWRtaW4iOjEsIm5hbWUiOiJcdTRlNjBcdThmZDFcdTVlNzMiLCJ0b2tlbiI6ImFmMjFhZDhhZmIxMjhiNmU1ZjdkNDgxNzQ4NTJiYjg1MWZhMmJmOGMwNGZmY2FmMmExMzQ3MzZhZGQ2MTUwYzYxIn0= HTTP/1.1\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\nHost: "+HOST+':'+str(PORT)+"\r\nOrigin: https://yq.aliyun.com\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: AQIDBAUGBwgJCgsMDQ4PEC==\r\n\r\n"
        self.sock.sendall(content)
        log.debug("SocketTest send handshake msg")
        self.recvmsg()

    def sendmsg(self, msg):
        log.debug("SocketTest send msg: %s", msg)
        log.debug('%r', encodeFrame({'length': len(msg),
            'opCode': 1, 'FIN': 1, 'payloadData': msg, 'maskingKey': [0x25, 0x98, 0x67, 0x99]}))
        self.sock.sendall(encodeFrame({'length': len(msg),
            'opCode': 1, 'FIN': 1, 'payloadData': msg, 'maskingKey': [0x25, 0x98, 0x67, 0x99]}))

    def sendclose(self):
        log.debug("SocketTest send close frame")
        code = 1000 # a normal closure
        msg  = struct.pack('>H', code) + '关闭连接'
        self.sock.sendall(encodeFrame({'length': len(msg),
            'opCode': 8, 'FIN': 1, 'payloadData': msg, 'maskingKey': [0x25, 0x98, 0x67, 0x99]}))

    def recvmsg(self):
        buf = []
        s = self.sock.recv(1024)
        buf.append(s)
        msg = "".join(buf)
        log.debug("SocketTest recv msg: %r", msg)

if __name__ == '__main__':
    tasks = []
    for i in range(CONNECTIONS):
        tasks.append(PluginThread())
    for task in tasks:
        task.start()

    sys.exit(0)
