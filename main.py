from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
from pathlib import Path
from functools import wraps
import requests

app = Flask(__name__)
# 启用跨域支持
CORS(app)

def handle_api_errors(func):
    """统一的API错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError:
            return jsonify({
                'success': False,
                'message': '权限不足，无法执行操作'
            }), 403
        except OSError as e:
            return jsonify({
                'success': False,
                'message': f'系统操作失败: {str(e)}'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'未知错误: {str(e)}'
            }), 500
    return wrapper

def validate_request_data(required_fields=None):
    """验证请求数据的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求体不能为空'
                }), 400
            
            if required_fields:
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({
                            'success': False,
                            'message': f'{field}参数不能为空'
                        }), 400
            
            return func(data, *args, **kwargs)
        return wrapper
    return decorator

@app.route('/file/mv', methods=['POST'])
@handle_api_errors
@validate_request_data(['file_path', 'new_name'])
def rename_file(data):
    """
    修改文件名的接口
    参数:
    - file_path: 原文件的完整路径
    - new_name: 新的文件名
    """
    file_path = data.get('file_path')
    new_name = data.get('new_name')
    
    # 检查原文件是否存在
    if not os.path.exists(file_path):
        return jsonify({
            'success': False,
            'message': f'文件不存在: {file_path}'
        }), 404
    
    # 获取原文件所在目录
    original_path = Path(file_path)
    directory = original_path.parent
    new_file_path = directory / new_name
    
    # 检查新文件名是否已存在
    if os.path.exists(new_file_path):
        return jsonify({
            'success': False,
            'message': f'目标文件已存在: {new_file_path}'
        }), 409
    
    # 执行文件重命名
    os.rename(file_path, new_file_path)
    
    return jsonify({
        'success': True,
        'message': '文件重命名成功',
        'original_path': str(file_path),
        'new_path': str(new_file_path)
    })


@app.route('/file/ls', methods=['POST'])
@handle_api_errors
@validate_request_data(['dir'])
def list_files(data):
    """
    列出目录下所有文件和子文件的接口
    参数:
    - dir: 目录路径
    """
    dir_path = data.get('dir')
    
    # 检查目录是否存在
    if not os.path.exists(dir_path):
        return jsonify({
            'success': False,
            'message': f'目录不存在: {dir_path}'
        }), 404
    
    # 检查是否为目录
    if not os.path.isdir(dir_path):
        return jsonify({
            'success': False,
            'message': f'路径不是目录: {dir_path}'
        }), 400
    
    # 递归获取所有文件路径
    all_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    
    return jsonify({
        'success': True,
        'message': f'成功获取目录文件列表',
        'directory': dir_path,
        'total_files': len(all_files),
        'files': all_files
    })


@app.route('/file/upload', methods=['POST'])
@handle_api_errors
@validate_request_data(['url', 'filepath'])
def upload_file(data):
    """
    上传本地文件到指定URL的接口
    参数:
    - url: 目标上传URL
    - filepath: 本地文件路径
    - field_name: 文件字段名 (可选，默认为 'file')
    - headers: 额外的HTTP头 (可选)
    - timeout: 请求超时时间(秒) (可选，默认为 30)
    """
    url = data.get('url')
    filepath = data.get('filepath')
    field_name = data.get('field_name', 'file')
    headers = data.get('headers', {})
    timeout = data.get('timeout', 30)
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'message': f'文件不存在: {filepath}'
        }), 404
    
    # 检查是否为文件（不是目录）
    if not os.path.isfile(filepath):
        return jsonify({
            'success': False,
            'message': f'路径不是文件: {filepath}'
        }), 400
    
    # 获取文件信息
    file_path = Path(filepath)
    file_name = file_path.name
    file_size = os.path.getsize(filepath)
    
    try:
        # 打开文件并上传
        with open(filepath, 'rb') as file:
            files = {field_name: (file_name, file, 'application/octet-stream')}
            
            # 发送POST请求上传文件
            response = requests.post(
                url=url,
                files=files,
                headers=headers,
                timeout=timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 尝试解析JSON响应，如果失败则返回文本
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return jsonify({
                'success': True,
                'message': '文件上传成功',
                'filepath': filepath,
                'filename': file_name,
                'file_size': file_size,
                'upload_url': url,
                'status_code': response.status_code,
                'response': response_data
            })
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': f'上传超时 (超过{timeout}秒)'
        }), 408
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'message': f'连接失败，无法访问URL: {url}'
        }), 503
        
    except requests.exceptions.HTTPError as e:
        return jsonify({
            'success': False,
            'message': f'HTTP错误: {e.response.status_code} - {e.response.reason}',
            'status_code': e.response.status_code,
            'response': e.response.text
        }), e.response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'请求异常: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '服务运行正常'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=25000)
