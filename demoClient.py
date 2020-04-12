# Import socket module
import json
import socket
from _thread import *

# 服务端的基本配置细腻些
import struct
from threading import Thread

from main.Tools.TimeTools import TimeTools

HOSTNAME = "localhost"
PORT = 12345
DEFAULT_MSG_MAX_SIZE = 10
DEFAULT_MSG_ENCODE_TYPE = 'utf8'
IS_CONN = False


# todo:有个考虑 有可能需要引入 消息队列处理传入的多条消息

# todo:要求传入的msg 必须是有效的md5的值类型的  需要添加一个值校验,
# todo: 需要加入一些额外的消息组装的校验 content 是否内容合法等
# todo: 需要校验 encode_type 是否是有效的编码格式 建议 encode_type 采用枚举类型
# todo: 发送消息之前可以加入对私聊消息的对象是否在线进行校验||聊天室是否存在进行校验
# 根据传递的socket 对象进行消息的发送
def sendMsg2Server(sock: socket, msg: str, msg_type: int, encode_type: str):
    # todo: 这里还没有校验 传入的socket 是否已经建立连接了
    # 发送消息的部分
    data = json.dumps({"msg": msg, "type": msg_type}).encode(encode_type)
    sock.sendall(data)


# 用来欢迎用户并且提示用户如何使用该系统的部分
def sayHelloToUser():
    print("Welcome to use this chatting system!")
    print("Please enter your name to join the chat rooms:\n")


# 获取用户的输入内容，msg 是用来提示用输入的部分
def getUserInput(msg: str):
    content = input(msg)
    return content


# todo: 已弃用此方法 需要加入一些额外的消息组装的校验 content 是否内容合法等
# 弃用方法
# 根据传入的消息类型以及消息内容组装一个新的消息体
def create_message(msg_type: int, content: str):
    return {"msg": content, "type": msg_type}


# 读取服务器端的传递的消息
def readFromServer(sock: socket, encode_type: str):
    try:
        recv_d = sock.recv(4096)
        if recv_d is None:
            return None
        data = json.loads(recv_d.decode(encode_type))
    except error as e:
        print(system_output_format("system", e))
        data = None
    return data


# todo: 这里的接收服务器传递的消息的部分需要做成多线程的
# 监听服务器的消息传递
def listenFromServer(conn: socket):
    while True:
        if IS_CONN:
            try:
                # conn.settimeout(20)
                msg = readFromServer(conn, DEFAULT_MSG_ENCODE_TYPE)
                if msg is None:
                    pass
                else:
                    '''
                    服务器约定 返回给 client 的消息中:
                    type = 11 表示 此条消息是私聊消息
                    type = 12 表示 此条消息是群聊消息
                    type = 13 表示 此条消息是系统广播消息
                    '''
                    echoNewMsg(msg)
            except socket.error as e:
                print(system_output_format("System", "Connection Error:" + e))
        else:
            break


def system_output_format(output_type, content):
    return "[{0}|{1}]:{2}\n".format(TimeTools.getLocalTime(), output_type, content)


def echoNewMsg(new_msg):
    """
    服务器约定 返回给 client 的消息中:
    type = 10 表示 此条消息是用来提示用户出现错误  目前只规定了 用户名重复这单一 错误
    type = 11 表示 此条消息是私聊消息
    type = 12 表示 此条消息是群聊消息
    type = 13 表示 此条消息是系统通知消息
    type = 15 表示 用户的错误消息  系统无法返回对应的操作或服务
    """
    if new_msg.get('type') == 11:
        # 私聊消息 消息体内会包含私聊消息的表示信息
        print(system_output_format('Private', new_msg.get('msg')))
    elif new_msg.get('type') == 12:
        # 群聊消息 群消息 todo: 这里可以加入群聊的名字
        print(system_output_format('Group Talk', new_msg.get('msg')))
        # print("[{0}|Group Talk|{2}]:{3}".format(TimeTools.getLocalTime(), group_name,new_msg.get('msg')))
    elif new_msg.get('type') == 13:
        # 系统通知消息 广播消息 直接print
        print(system_output_format('Broadcast', new_msg.get('msg')))
    elif new_msg.get('type') == 15:
        # 服务不可达通知
        print(system_output_format('System', new_msg.get('msg')))


def handleUserInput(conn: socket, input):
    """
    客户端约定 发送给 server 的消息中:
    type = 0 表示 新用户登录 ，传入自己的姓名  独特的消息类型 唯一
    type = 1 表示 私聊消息，消息体内会包含目标用户信息
    type = 2 表示 群发消息，直接转发到用户当前所在的群聊中  当拓展为多群聊->单用户 时，需要引入 聊天室id
    type = 3 表示 广播消息
    type = 4 表示 此条消息是系统通知消息 例如 用户下线
    """
    if "@" in input:  # 表示是私信消息
        if len(input) > 1:
            # 截取目标用户的名字
            des_user = input[input.index("@") + 1:input.index(":")]
            print(system_output_format('Private',
                                       "[send to User:{0}]:{1}".format(des_user, input[input.index(":") + 1:])))
            sendMsg2Server(conn, "{0}:{1}".format(des_user, input[input.index(":") + 1:]), 1, DEFAULT_MSG_ENCODE_TYPE)
    elif "#" in input:
        if len(input) > 1:
            # 截取群聊名称
            des_group_name = input[1:input.index(":")]
            sendMsg2Server(conn, "{0}:{1}".format(des_group_name, input[input.index(":") + 1:]), 2,
                           DEFAULT_MSG_ENCODE_TYPE)
    elif "leave" in input:
        if len(input) > 1:
            # 截取群聊名称 leave [group name]包括一个空格
            des_group_name = input[input.index("leave") + 6:]
            sendMsg2Server(conn, "{0}:{1}".format(des_group_name, "leave_type"), 2, DEFAULT_MSG_ENCODE_TYPE)
    elif "join" in input:
        if len(input) > 1:
            # 截取群聊名称 leave [group name]包括一个空格
            des_group_name = input[input.index("join") + 5:]
            sendMsg2Server(conn, "{0}:{1}".format(des_group_name, "join_type"), 2, DEFAULT_MSG_ENCODE_TYPE)
    elif "create" in input:
        if len(input) > 1:
            # 截取群聊名称 leave [group name]包括一个空格
            des_group_name = input[input.index("create") + 7:]
            sendMsg2Server(conn, "{0}:{1}".format(des_group_name, "create_type"), 2, DEFAULT_MSG_ENCODE_TYPE)
    # elif all(p in ["[", "]"] for p in input):
    #     # 截取群聊名称
    #     des_group_name = input[input.index("[") + 1:input.index("]")]
    #     print(des_group_name)
    #     sendMsg2Server(conn, "{0}:{1}".format(des_group_name, input[input.index(":") + 1:]), 2, DEFAULT_MSG_ENCODE_TYPE)
    else:
        sendMsg2Server(conn, input, 3, DEFAULT_MSG_ENCODE_TYPE)


def echoHelpInfo():
    print("Commands now supported in our system are:")
    print("[words]\t=>\tSay something on the public area.")
    print("@[username]:[something]\t=>\tSay something to the specific user in private way.")
    print("create [chat group name]\t=>\tCreate a chatting group to communicate.")
    print("join [chat group name]\t=>\tJoin a chatting group.")
    print("leave [chat group name]\t=>\tLeave a chatting group.")
    print("#[chat group name]:[something]\t=>\tSay something in the specific group.")
    print("quit \t=>\tQuit from this system.")


# 建立连接后 立马发送一个set name 的请求 修改自己的连接名
# 连接中，可以群发和私聊发送消息
def start_connection():
    global IS_CONN
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOSTNAME, PORT))
        except socket.error as e:
            print("Address-related error connecting to server: %s" % e)
            return
        sayHelloToUser()
        name = getUserInput("Your name:")

        # todo: 需要添加对用户 key in 的值的不同进行不同的响应。目前允许 用户 加入聊天大厅，聊天室，以及与用户进行私聊
        # 发送消息的部分是需要在主线程上一直进行的，所以不需要放在多线程上。
        sendMsg2Server(s, name, 0, DEFAULT_MSG_ENCODE_TYPE)

        try:
            msg = readFromServer(s, DEFAULT_MSG_ENCODE_TYPE)
        except error as e:
            msg = None
            print(system_output_format("system", e))
        if msg is None:
            pass
        else:
            '''
            客户端约定 发送给 server 的消息中:
            type = 0 表示 新用户登录 ，传入自己的姓名  独特的消息类型 唯一
            type = 1 表示 私聊消息，消息体内会包含目标用户信息
            type = 2 表示 群发消息，直接转发到用户当前所在的群聊中  当拓展为多群聊->单用户 时，需要引入 聊天室id 
            type = 3 表示 广播消息 
            type = 4 表示 此条消息是系统通知消息 例如 用户下线
            '''
            """
            服务器约定 返回给 client 的消息中:
            type = 10 表示 此条消息是用来提示用户出现错误  目前只规定了 用户名重复这单一 错误
            type = 11 表示 此条消息是私聊消息
            type = 12 表示 此条消息是群聊消息
            type = 13 表示 此条消息是系统广播消息
            type = 14 表示 系统消息 目前用于 确认server 已经清理完毕用户的在线信息
            type = 15 表示 用户的错误消息  系统无法返回对应的操作或服务
            """
            # todo: 限制用户错误尝试次数
            while None is msg or 10 == msg.get('type'):
                print(msg.get('msg'))
                name = getUserInput("Your name:")
                sendMsg2Server(s, name, 0, DEFAULT_MSG_ENCODE_TYPE)
                msg = readFromServer(s, DEFAULT_MSG_ENCODE_TYPE)

            if msg.get('type') == 12:
                # 成功进入聊天系统
                print("Welcome to chat lobby! %s" % name)
                echoHelpInfo()
                IS_CONN = True

                # 开新线程执行
                listen_thread = Thread(target=listenFromServer, args=(s,), daemon=True)
                listen_thread.start()
                # tid = start_new_thread(listenFromServer, (s,))
                # print("start to listen new message on thread:", tid)

                while True:
                    try:
                        user_input = input()
                        if user_input == "quit":
                            IS_CONN = False
                            print("leaving....")
                            sendMsg2Server(s, 'quit', 4, DEFAULT_MSG_ENCODE_TYPE)
                            # 确认服务端已经清除用户的在线信息
                            endACK = readFromServer(s, DEFAULT_MSG_ENCODE_TYPE)
                            while None is msg or endACK.get('type') != 14:
                                print("..")
                                endACK = readFromServer(s, DEFAULT_MSG_ENCODE_TYPE)
                            print("Bye!")
                            break
                        else:
                            handleUserInput(s, user_input)
                    except error as e:
                        print(system_output_format("system", e))

            else:
                pass


if __name__ == '__main__':
    start_connection()
