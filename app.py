from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import os
import json
from compare import Compare
from recognize import Recognize
from model import Model

def sendToProcess(point):
    k = Recognize(point)
    Compare(point)
    return k

def sendToModel(inputText, history):
    print('输入:', inputText)
    print('历史:', history)
    outputText = Model(inputText)
    return outputText

app = Flask(__name__)

# 配置静态文件路径
app.static_folder = 'static'
app.template_folder = 'templates'

# 确保必要的目录存在
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/models', exist_ok=True)
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    """主页面路由"""
    return render_template('index.html')

@app.route('/layout_test.html')
def layout_test():
    """布局测试页面路由"""
    return send_from_directory('.', 'layout_test.html')

@app.route('/test_ajax.html')
def test_ajax():
    """AJAX测试页面路由"""
    return send_from_directory('.', 'test_ajax.html')

@app.route('/api/triggerpoint/structure')
def get_triggerpoint_structure():
    """获取触发点文件夹结构"""
    try:
        # 读取label.json文件
        label_path = os.path.join('static', 'models', 'triggerpoint', 'label.json')
        label_data = []
        if os.path.exists(label_path):
            with open(label_path, 'r', encoding='utf-8') as f:
                label_data = json.load(f)
        
        # 获取triggerpoint文件夹中的所有json文件
        triggerpoint_dir = os.path.join('static', 'models', 'triggerpoint')
        files = []
        if os.path.exists(triggerpoint_dir):
            for file in os.listdir(triggerpoint_dir):
                if file.endswith('.json') and file != 'label.json':
                    files.append(file)
        
        return jsonify({
            'files': files,
            'labelData': label_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/triggerpoint/<filename>')
def get_triggerpoint_file(filename):
    """获取触发点JSON文件内容"""
    try:
        file_path = os.path.join('static', 'models', 'triggerpoint', filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/acupoint')
def get_acupoint_data():
    """获取穴位数据"""
    try:
        acupoint_path = os.path.join('static', 'models', 'acupoint.json')
        if os.path.exists(acupoint_path):
            with open(acupoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children')
def get_children_data():
    """获取子节点数据"""
    try:
        children_path = os.path.join('static', 'models', 'children.json')
        if os.path.exists(children_path):
            with open(children_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-pointcloud', methods=['POST'])
def process_pointcloud():
    """处理点云数据（调用sendToProcess函数）"""
    try:
        data = request.get_json()
        # 调用sendToProcess函数处理点云数据
        result = sendToProcess(data)
        
        return jsonify({
            'success': True,
            'message': '点云数据处理成功',
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-to-model', methods=['POST'])
def send_to_model():
    """发送消息到模型（调用sendToModel函数，支持历史记录）"""
    try:
        data = request.get_json()
        input_text = data.get('message', '')
        history = data.get('history', [])
        # 调用sendToModel函数，传递历史记录
        result = sendToModel(input_text, history)
        return jsonify({
            'success': True,
            'message': '消息处理成功',
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/models/<path:filename>')
def serve_model(filename):
    """提供模型文件服务"""
    return send_from_directory('static/models', filename)

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    """提供JavaScript文件服务，确保正确的MIME类型"""
    response = send_from_directory('static/js', filename)
    response.headers['Content-Type'] = 'application/javascript'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 