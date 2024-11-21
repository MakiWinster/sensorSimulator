# Linux应用开发课程设计：传感器数据采集与可视化系统

## 项目简介
本项目是"Linux应用开发"课程的系统设计实践，实现了一个基于PyQt5和Flask的传感器数据采集与可视化系统。系统包括客户端数据采集、服务端数据处理和Web实时可视化三个核心模块。

## 技术栈

|**服务端**|**客户端**|
|---|---|
|Python|Python|
|Flask|PyQt5|
|Flask-SocketIO|Requests 库|
|WebSocket||


## 主要功能
1. 客户端可随机产生 `温度` 和 `湿度` 数值，并且在首次 `开始收集` 时会向服务端发送online通知，支持多客户端。
2. 服务端实时展示从客户端收集的数据，并且使用折线图展示数据，同时还记录客户端的online、offline时间。
3. 心跳协议，服务端3秒一次轮回接收客户端的心跳，大于3个回合为感受到客户端心跳判断为offline

## 技术特点
- 使用UUID进行客户端唯一标识
- 实时WebSocket数据推送
- 支持多客户端数据上报
- 响应式Web数据展示

## 环境依赖
- Python 3.7+
- PyQt5
- Flask
- Flask-SocketIO
- Chart.js

## 安装与运行
### 安装依赖
```bash
pip install -r requirements.txt
```

### 服务端
```bash
python server.py
```

### 客户端
```bash
python SensorDataClient.py
```

## 使用说明
1. 启动服务端
2. 运行客户端程序
3. 点击"开始采集"按钮
4. 打开 http://localhost:5000/view 查看实时数据

## 作者
Maki Winster