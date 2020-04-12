## SimpleChatSys：

基于命令行，python3的简易聊天小应用，进满足了学校的作业需求！

基于Socket TCP通讯 ，C/S 端到端对话

目前还是处于一个简单的模板状态。



#### 截图:

---------

- 服务器端效果:

  ![server_part_example](/screenshot/server_part.png)

- 客户端效果:

  - 进入系统：

    ![welcome_example](/screenshot/login.png)

  - 其他新用户进入此聊天系统：

    ![new_user_come_in_example](/screenshot/new_user_join_system.png)

  - 进入系统：

    - 用户发送私聊消息给其他用户：

      ![private_talk_example](/screenshot/private_talk_1.PNG)

    - 接收私聊消息：

      ![private_talk_example2](/screenshot/private_talk_2.PNG)

    - 参与群聊消息 用户A视角：

      ![group_talk_example](/screenshot/group_talk1.PNG)

    - 参与群聊消息 用户B消息：

      ![group_talk_example2](/screenshot/group_talk2.PNG)

### 实现的功能:

-------
```
注: 下方的[内容] 表示要输入对应的内容，[]是不需要的
```

1. 简易的私聊模式：用户通过 `@用户名:私聊内容` 即可与在线用户进行沟通
2. 简易的广播内容：用户直接在命令行敲击的内容都会视为 广播内容
3. 简易的群聊模式：create [群聊名称]|join [群聊名称]|leave [群聊名称]|#[群聊名称]:[消息]



### 等待改善的部分:

------

1. 修复 客户端 quit 的时候会触发异常
2. 重构用户和服务器监听新消息的代码  采用监管者发布者模式
3. 用户下线的功能的引入
4. 用户在线传送文件的功能引入
5. 可以引入消息队列处理 优化服务端处理消息的部分