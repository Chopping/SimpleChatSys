import uuid

from . import User

DEFAULT_MSG_ENCODE_TYPE = 'utf8'


class ChatRoom:
    # todo: 逻辑上暂时未定的情况：群主离开群聊 讨论群是保留还是移除？ 讨论群的群主是否需要更新
    def __init__(self, room_name: str, creator: User):
        self.chat_room_name = room_name
        self.room_id = uuid.uuid1()
        self.creator = creator  # 设置此字段的目的是为了支持 聊天室发起人一些特殊权利的 设计
        self.members = {creator}
        self.send_room_msg("Room Created!")

    # 用来发送房内消息
    def send_room_msg(self, content: str, encode_type=DEFAULT_MSG_ENCODE_TYPE):
        for member in self.members:
            member.socket.write(content, 12, encode_type)