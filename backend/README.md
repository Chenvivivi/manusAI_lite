# ManusAI Backend

基于 FastAPI 和 DeepSeek API 的后端服务

## 配置 API Key

1. 复制 `.env.example` 为 `.env`：
```bash
copy .env.example .env
```

2. 编辑 `.env` 文件，填入你的 DeepSeek API Key：
```env
DEEPSEEK_API_KEY=your_actual_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner
```

## 安装依赖

```bash
# 安装依赖（已自动安装到用户目录）
pip install -r requirements.txt
```

## 运行服务

```bash
python main.py
```

或者直接双击 `start.bat`（Windows）

服务将在 http://localhost:8000 启动

## API 接口

### POST /api/chat

接收前端消息，调用 DeepSeek Reasoner 模型，返回 AI 回复

**请求体：**
```json
{
    "text": "用户消息内容",
    "taskId": 1
}
```

**响应：**
```json
{
    "text": "DeepSeek 模型的回复内容",
    "time": "14:30",
    "reasoning": "模型的思维链内容",
    "files": []
}
```

### DELETE /api/chat/history/{task_id}

清除指定任务的对话历史

## 功能特性

- ✅ 接入 DeepSeek Reasoner 模型
- ✅ 支持多轮对话上下文管理
- ✅ 后端控制台打印模型返回结果
- ✅ 返回思维链内容（reasoning_content）
- ✅ 自动处理对话历史拼接
- ✅ CORS 跨域支持

## 访问文档

启动服务后访问：
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## 调试信息

后端控制台会打印：
- 收到的用户消息
- DeepSeek 模型的思维链（前 200 字符）
- DeepSeek 模型的完整回复
