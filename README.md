# 文件重命名 Web 服务

这是一个基于 Flask 的 Python Web 服务，提供文件重命名功能。

## 功能

- 接收 `/file/move` POST 请求
- 根据提供的 `file_path` 和 `new_name` 参数重命名文件
- 提供健康检查接口 `/health`

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python main.py
```

服务将在 `http://localhost:5000` 启动。

## API 接口

### 重命名文件

**POST** `/file/move`

请求体 (JSON):
```json
{
    "file_path": "/path/to/old_file.txt",
    "new_name": "new_file.txt"
}
```

响应示例:
```json
{
    "success": true,
    "message": "文件重命名成功",
    "original_path": "/path/to/old_file.txt",
    "new_path": "/path/to/new_file.txt"
}
```

### 健康检查

**GET** `/health`

响应示例:
```json
{
    "status": "healthy",
    "message": "服务运行正常"
}
```

## 使用示例

使用 curl 测试:

```bash
# 重命名文件
curl -X POST http://localhost:5000/file/move \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/tmp/test.txt",
    "new_name": "renamed.txt"
  }'

# 健康检查
curl http://localhost:5000/health
```
