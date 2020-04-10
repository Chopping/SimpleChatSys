import json
import struct
import uuid
import socket

DEFAULT_MSG_MAX_SIZE = 10
DEFAULT_MSG_ENCODE_TYPE = 'utf8'


class clientSocket:

    def __init__(self, sock: socket):
        self.socket = sock

    def read(self, encode_type: str = DEFAULT_MSG_ENCODE_TYPE):
        # recv_d = self.socket.recv(DEFAULT_MSG_MAX_SIZE)
        # msg_length = struct.unpack("q", recv_d)

        recv_d = self.socket.recv(4096)
        if recv_d is None:
            return None
        data = json.loads(recv_d.decode(encode_type))
        return data

    def write(self, content: str, msg_type: int, encode_type: str = DEFAULT_MSG_ENCODE_TYPE):
        # msg_len = len(content.encode(encode_type))
        # self.socket.sendall(struct.pack("q", msg_len))  # 先发送消息的长度
        try:
            self.socket.sendall(json.dumps({"msg": content, "type": msg_type}).encode(encode_type))  # 转成 bytes 才能发送
            return True
        except socket.error as e:
            print("error happen : %s", e)
            return False

    # todo: 在这步里再次检查 在线信息是否已经清理完毕
    def close(self):
        # print(self.name, "has leaved this channel!")
        # 通知客户端 服务端也要关闭连接了
        self.write("Quit ACK", 14, DEFAULT_MSG_ENCODE_TYPE)
        self.socket.close()




