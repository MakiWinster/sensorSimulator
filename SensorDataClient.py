import sys
import random
import requests
import uuid
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import QTimer, Qt

# 服务端地址
SERVER_URL = "http://127.0.0.1:5000"  # 替换为实际服务端URL

class SensorDataClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client_id = str(uuid.uuid4())
        self.online_notified = False
        self.initUI()

    def initUI(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle("传感器数据采集客户端")
        self.setGeometry(100, 100, 400, 300)  # 调整窗口大小

        # 设置全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:disabled {
                background-color: #d3d3d3;
                color: #a0a0a0;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # 创建主控件和布局
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # 显示温度和湿度
        self.temp_label = QLabel("温度: N/A °C")
        self.humidity_label = QLabel("湿度: N/A %")
        self.temp_label.setFont(QFont("Arial", 16))
        self.humidity_label.setFont(QFont("Arial", 16))

        # 设置数据布局
        data_layout = QHBoxLayout()
        data_layout.addWidget(self.temp_label)
        data_layout.addWidget(self.humidity_label)

        # 开始采集按钮
        self.start_button = QPushButton("开始采集")
        self.start_button.clicked.connect(self.start_collecting)

        # 停止采集按钮
        self.stop_button = QPushButton("停止采集")
        self.stop_button.clicked.connect(self.stop_collecting)
        self.stop_button.setEnabled(False)

        # 设置按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        # 添加组件到主布局
        self.layout.addLayout(data_layout)
        self.layout.addLayout(button_layout)

        # 设置布局和中心控件
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)


        # 定时器，用于定时生成数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_sensor_data)


    def notify_server(self, action):
        """通知服务器客户端状态"""
        try:
            response = requests.post(SERVER_URL + "/status", 
                                    json={"action": action, "client_id": self.client_id},
                                    timeout=5)  # Add timeout
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f"{action}通知发送成功")
        except requests.exceptions.RequestException as e:
            print(f"{action}通知发送失败: {e}")
            print(f"错误详情: {e.response.text if hasattr(e, 'response') else ''}")

    def closeEvent(self, event):
        self.notify_server("offline")
        super().closeEvent(event)

    def start_collecting(self):
        if not self.online_notified:  # 检查是否已经发送过online通知
            self.notify_server("online")
            self.online_notified = True  # 更新标志位为已发送
        self.timer.start(1000)  # 毫秒为单位
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_collecting(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def generate_sensor_data(self):
        """随机生成温度和湿度数据"""
        temperature = round(random.uniform(20.0, 30.0), 2)
        humidity = round(random.uniform(30.0, 70.0), 2)
        return temperature, humidity

    def send_sensor_data(self):
        """发送采集数据到服务器"""
        temperature, humidity = self.generate_sensor_data()
        self.temp_label.setText(f"温度: {temperature} °C")
        self.humidity_label.setText(f"湿度: {humidity} %")

        # 构造请求数据
        data = {
            "temperature": temperature,
            "humidity": humidity
        }

        try:
            response = requests.post(f"{SERVER_URL}/data", json=data)  # 注意这里使用 /data
            if response.status_code == 200:
                print("数据发送成功:", data)
            else:
                print("数据发送失败:", response.status_code)
        except Exception as e:
            print("发送失败:", e)

def send_heartbeat(self):
    """发送心跳包到服务器"""
    try:
        response = requests.post(f"{SERVER_URL}/heartbeat", 
                                 json={"client_id": self.client_id},
                                 timeout=2)
        if response.status_code == 200:
            print("心跳包发送成功")
        else:
            print("心跳包发送失败")
    except Exception as e:
        print(f"心跳包发送异常: {e}")

def start_collecting(self):
    # 重置online通知标记
    self.online_notified = False
    
    if not self.online_notified:
        self.notify_server("online")
        self.online_notified = True
    
    # 启动数据采集定时器
    self.timer.start(1000)  # 每秒发送数据
    
    # 启动心跳定时器（每3秒发送一次心跳）
    self.heartbeat_timer = QTimer()
    self.heartbeat_timer.timeout.connect(self.send_heartbeat)
    self.heartbeat_timer.start(3000)  # 3秒发送一次心跳
    
    self.start_button.setEnabled(False)
    self.stop_button.setEnabled(True)

def stop_collecting(self):
    # 停止数据采集定时器
    self.timer.stop()
    
    # 停止心跳定时器
    if hasattr(self, 'heartbeat_timer'):
        self.heartbeat_timer.stop()
    
    self.start_button.setEnabled(True)
    self.stop_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = SensorDataClient()
    client.show()
    sys.exit(app.exec_())
