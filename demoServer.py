import socket
from _thread import *

from main.Model.ChatRoom import ChatRoom
from main.Tools.OutputFormater import OutputFormater
from main.serverlib import clientSocket
from main.Model.User import User

# 服务端的基本配置细腻些
HOSTNAME = "localhost"
PORT = 12345
# 最大连接数
DEFAULT_CONNECTION_NUM = 20

# 当前连接的数量
clients = []
names = []
rooms = list()


# 线程里执行的方法
# 用户发送的消息的格式 {msg:'',type:0}
# todo: 用户强制终止客户端应用时，需要在服务端检测到异样并及时清理
def handle_new_client_come_in(c):
    new_user = User(clientSocket(c))
    new_client_socket = clientSocket(c)

    # while true 这个方法真的有点儿蠢....
    while True:
        # 针对接收的消息进行不同的处理
        data = new_user.socket.read('utf8')
        if data is not None:
            '''
            客户端约定 发送给 server 的消息中:
            type = 0 表示 新用户登录 ，传入自己的姓名  独特的消息类型 唯一
            type = 1 表示 私聊消息，消息体内会包含目标用户信息
            type = 2 表示 群发消息，直接转发到用户当前所在的群聊中  当拓展为多群聊->单用户 时，需要引入 聊天室id 
            type = 3 表示 广播消息 
            type = 4 表示 此条消息是系统通知消息 例如 用户下线
            '''
            '''
            服务器约定 返回给 client 的消息中:
            type = 10 表示 此条消息是用来提示用户出现错误  目前只规定了 用户名重复这单一 错误
            type = 11 表示 此条消息是其他消息传递过来的消息
            type = 12 表示 此条消息是群聊消息
            type = 13 表示 此条消息是系统广播消息
            type = 14 表示 系统消息 目前用于 确认server 已经清理完毕用户的在线信息
            '''
            # 操作指令的消息 新用户传送自己的名字 提供给服务器
            if 0 == data.get('type'):
                # todo: 判断重名这里出现了bug  发现于 2020/04/10 1:12 重名登录成功
                new_username = data.get('msg')
                if new_username in names:
                    # todo: 错误次数应该设置上限 然后达到上限阻止用户继续填写名字
                    # 发送消息提醒用户重新填写名称
                    print('duplicate name!')
                    new_user.socket.write('name duplicate!', 10, 'utf8')
                else:
                    # 将用户放入在线用户的列表中
                    new_name = data.get('msg')
                    new_user.username = new_username
                    new_user.socket.write('Success!', 12, 'utf8')
                    names.append(new_username)

                    # 广播通知所有的用户 有用户进场
                    if 0 != len(clients):
                        for client in clients:
                            client.socket.write('new user %s join our chat system, welcome!' % new_name, 13, 'utf8')
                    clients.append(new_user)
                    # server端打印当前的用户信息
                    print(OutputFormater.get_format_output('Broadcast', 'new user %s join chat system' % new_name))
                    print(OutputFormater.get_format_output('Broadcast', '%d users are now online' % len(clients)))
                    # print('[%s] %d users are online! %d \t rooms have been created!' % new_name)
            # 接收用户私信消息
            elif 1 == data.get('type'):
                msg_content = data.get('msg')
                des_user = msg_content[:msg_content.index(":")]
                # 将消息发送给对应的用户 并且在内容里标识出是 用户XX发送的消息
                if des_user in names:
                    for client in clients:
                        if client.username == des_user:
                            client.socket.write(
                                '[User:{0}]:{1}'.format(new_user.username, msg_content[msg_content.index(":") + 1:]),
                                11, 'utf8')
                            print(OutputFormater.get_format_output("Private",
                                                                   '[User:{0}]:{1}'.format(new_user.username,
                                                                                           msg_content[
                                                                                           msg_content.index(
                                                                                               ":") + 1:])))
                else:
                    print(OutputFormater.get_format_output("system",
                                                           "{0} user is trying to communicate with a offline user {1}".format(
                                                               new_user.username, des_user)))
                    new_user.socket.write("User is not online, please try to communicate with him/her later!", 15)
            # 接收群聊消息 todo: 当前只支持用户加入一个群聊中
            elif 2 == data.get('type'):
                text = data.get('msg')
                msg_content = text[text.index(":") + 1:]
                group_name = text[:text.index(":")]
                if "leave_type" == msg_content:
                    # 用户请求离开此聊天室
                    is_exist = False
                    for r in rooms:
                        if r.chat_room_name == group_name:
                            is_exist = True
                            new_user.leave_room(r)
                            print(OutputFormater.get_format_output("Group Chat|{0}".format(group_name),
                                                                   '[User:{0}]:{1}'.format(new_user.username,
                                                                                           "leave this chat room")))
                    if not is_exist:
                        print(OutputFormater.get_format_output("system",
                                                               "{0} user is trying to leave an invalid chat room {1}".format(
                                                                   new_user.username, group_name)))
                        new_user.socket.write("Room is not valid ! ", 15)
                elif "join_type" == msg_content:
                    is_exist = False
                    for r in rooms:
                        if r.chat_room_name == group_name:
                            is_exist = True
                            new_user.join_room(r)
                    if not is_exist:
                        print(OutputFormater.get_format_output("system",
                                                               "{0} user is trying to leave an invalid chat room {1}".format(
                                                                   new_user.username, group_name)))
                        new_user.socket.write("Room is not valid ! ", 15)
                elif "create_type" == msg_content:
                    room = ChatRoom(group_name, new_user)
                    rooms.append(room)
                    new_user.join_room(room)
                    print(OutputFormater.get_format_output("Group Chat|{0}".format(group_name),
                                                           '[User:{0}]:{1}'.format(new_user.username,
                                                                                   "I have created this group!")))
                else:
                    # 加入群聊的消息
                    # 检查群聊名称对应的房间是否存在
                    is_exist = False
                    for r in rooms:
                        if r.chat_room_name == group_name:
                            is_exist = True
                            r.send_room_msg(
                                '[{0}|User:{1}]:{2}'.format(group_name, new_user.username, msg_content))
                    if not is_exist:
                        print(OutputFormater.get_format_output("system",
                                                               "{0} user is trying to say something in an invalid chat room {1}".format(
                                                                   new_user.username, group_name)))
                        new_user.socket.write("Room is not valid ! ", 15)
            # 接收广播消息
            elif 3 == data.get('type'):
                msg = data.get('msg')
                # 广播通知所有的用户 有用户进场 todo: 之后可以考虑移除 新用户进场广播全场的功能
                if 0 != len(clients):
                    for client in clients:
                        client.socket.write('[User:{0}]:{1}'.format(new_user.username, msg), 13, 'utf8')
                    print(
                        OutputFormater.get_format_output('Broadcast', '[User:{0}]:{1}'.format(new_user.username, msg)))
                    # 接收群聊消息 todo: 当前只支持用户加入一个群聊中
            elif 4 == data.get('type'):
                # todo:清理用户的在线信息：退出加入的聊天组，
                clients.remove(new_user)  # 从在线用户的列表中移除 此用户
                names.remove(new_user.username)
                new_user.logout_system()  # 调用封装好的用户类的离开方法 清理用户在线信息
                print(OutputFormater.get_format_output('Broadcast',
                                                       'User %s have left the chat system' % new_user.username))
                break
            # 不合理的消息请求
            else:
                print()
        else:
            print('bye')


def Main2():
    # 一直监听是否有新的连接
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOSTNAME, PORT))
        print("server socket is binned to port", PORT)
        sock.listen(DEFAULT_CONNECTION_NUM)
        while True:
            c_sock, addr = sock.accept()  # 接收来自客户端的新连接的请求  --主线程应做的事情
            # 开新线程执行
            # todo: 这里改成使用线程池
            tid = start_new_thread(handle_new_client_come_in, (c_sock,))
            print("new connection prepare with thread:", tid, "is running")


if __name__ == '__main__':
    Main2()
