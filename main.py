from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
from pathlib import Path

app = Flask(__name__)
# 启用跨域支持
CORS(app)

@app.route('/file/rename', methods=['POST'])
def rename_file():
    """
    修改文件名的接口
    参数:
    - file_path: 原文件的完整路径
    - new_name: 新的文件名
    """
    try:
        # 获取请求参数
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空'
            }), 400
        
        file_path = data.get('file_path')
        new_name = data.get('new_name')
        
        # 验证必需参数
        if not file_path:
            return jsonify({
                'success': False,
                'message': 'file_path参数不能为空'
            }), 400
            
        if not new_name:
            return jsonify({
                'success': False,
                'message': 'new_name参数不能为空'
            }), 400
        
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
        
    except PermissionError:
        return jsonify({
            'success': False,
            'message': '权限不足，无法修改文件'
        }), 403
        
    except OSError as e:
        return jsonify({
            'success': False,
            'message': f'文件操作失败: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'未知错误: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '服务运行正常'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
