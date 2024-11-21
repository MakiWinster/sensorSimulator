from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from threading import Lock
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 全局数据存储
data_store = []
clients_status_dict = {}
data_lock = Lock()
status_lock = Lock()
client_status_log = []

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

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    # 处理心跳包
    try:
        data = request.json
        print("收到心跳包:", data)
        return jsonify({"status": "alive"}), 200
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
        
        return jsonify({"status": f"client {action}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/clients', methods=['GET'])
def view_clients():
    with status_lock:
        return jsonify(client_status), 200



if __name__ == "__main__":
    socketio.run(app, debug=True)
