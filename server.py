import threading
import time
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from threading import Lock
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 全局数据存储
data_store = []
clients_status_dict = {}
data_lock = Lock()
status_lock = Lock()
client_status_log = []
client_heartbeat_status = {}

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        # 从请求中解析 JSON 数据
        data = request.json
        if not data or 'temperature' not in data or 'humidity' not in data:
            return jsonify({"error": "Invalid data format"}), 400
        
        # 将数据存入全局存储
        with data_lock:
            data_store.append(data)
        
        # 实时广播新数据
        socketio.emit('new_data', data)

        print("接收到数据:", data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/view')
def view_data():
    with data_lock, status_lock:
        return render_template('view.html',
                               data=data_store,
                               client_status=clients_status_dict,  # 使用新变量名
                               client_status_log=client_status_log)

def heartbeat_monitor():
    while True:
        current_time = datetime.now()
        with status_lock:
            for client_id, status in list(clients_status_dict.items()):
                # 如果超过3个轮回（9秒）没有收到心跳
                if (current_time - status.get('last_heartbeat', current_time)) > timedelta(seconds=9):
                    # 将客户端状态设为离线
                    clients_status_dict[client_id]['status'] = 'offline'
                    
                    # 重置online通知标记
                    client_heartbeat_status[client_id] = {
                        'online_notified': False
                    }
                    
                    # 记录日志
                    log_entry = {
                        "client_id": client_id,
                        "action": "offline_by_heartbeat",
                        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "details": f"客户端 {client_id} 心跳超时，自动下线"
                    }
                    client_status_log.append(log_entry)

                    # 新增这段代码
                    socketio.emit('client_status_update', {
                        "client_id": client_id, 
                        "status": "offline", 
                        "action": "offline_by_heartbeat", 
                        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"), 
                        "last_seen": current_time.strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        # 每3秒检查一次
        time.sleep(3)

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    try:
        data = request.json
        client_id = data.get("client_id", "")
        
        if not client_id:
            return jsonify({"error": "Missing client_id"}), 400
        
        current_time = datetime.now()
        
        with status_lock:
            # 更新最后心跳时间
            if client_id in clients_status_dict:
                clients_status_dict[client_id]['last_heartbeat'] = current_time
                clients_status_dict[client_id]['status'] = 'online'
            else:
                # 如果客户端不存在，可以选择忽略或添加
                clients_status_dict[client_id] = {
                    'status': 'online', 
                    'last_heartbeat': current_time,
                    'last_seen': current_time
                }
        
            socketio.emit('client_status_update', {
                "client_id": client_id,
                "status": "online",
                "action": "heartbeat",
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_seen": current_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({"status": "heartbeat received"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/status', methods=['POST'])
def client_status():
    try:
        data = request.json
        client_id = data.get("client_id", "")
        action = data.get("action", "")

        if not client_id or not action:
            return jsonify({"error": "Missing client_id or action"}), 400

        current_time = datetime.now()
        status_entry = {
            "client_id": client_id,
            "action": action,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "details": f"客户端 {client_id} 已 {action}"  # 增加详细描述
        }

        with status_lock:
            if action == "online":
                clients_status_dict[client_id] = {"status": "online", "last_seen": current_time}
            elif action == "offline":
                clients_status_dict[client_id] = {"status": "offline", "last_seen": current_time}
            
            client_status_log.append(status_entry)


            socketio.emit('client_status_update', {
                "client_id": client_id,
                "status": "online" if action == "online" else "offline",
                "action": action,
                "timestamp": status_entry['timestamp'],
                "last_seen": current_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return jsonify({"status": f"client {action}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
heartbeat_thread.start()

@app.route('/clients', methods=['GET'])
def view_clients():
    with status_lock:
        return jsonify(client_status), 200



if __name__ == "__main__":
    socketio.run(app, debug=True)
