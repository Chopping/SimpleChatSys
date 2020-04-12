import uuid

from . import ChatRoom
from main.serverlib import clientSocket

DEFAULT_MSG_ENCODE_TYPE = 'utf8'


class User:
    def __init__(self, sock: clientSocket, name: str = None):
        self.username = name
        self.u_id = uuid.uuid1()
        self.socket = sock
        self.rooms = list()

    # 用户加入聊天室
    def join_room(self, room: ChatRoom):
        self.rooms.append(room)
        room.members.add(self)
        room.send_room_msg('[{0}|User:{1}]:{2}'.format(room.chat_room_name, self.username, "%s has joined this chat room!" % self.username))

    def leave_room(self, room: ChatRoom):
        self.rooms.remove(room)
        if len(room.members) == 0 or self not in room.members:
            pass
        else:
            room.members.remove(self)
            room.send_room_msg("user %s has left this chat room!" % self.username)

    # todo: 用户类中用来判断此用户是否在线
    def is_online(self):
        print(self.username)

    # 此方法暂时未用
    def login_system(self):
        # 目前没有需要在登录的时候进行的东西
        print(self.username)

    def logout_system(self):
        # 在每个加入的房间内都退房
        if len(self.rooms) != 0:
            for room in self.rooms:
                self.leave_room(room)
        # 关闭socket
        self.socket.close()
