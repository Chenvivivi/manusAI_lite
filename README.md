# ManusAI 项目

一个类似 ManusAI 的聊天应用，包含前端和后端。

## 项目结构

```
manus/
├── frontend/          # 前端代码
│   ├── index.html    # 主页面
│   ├── style.css     # 样式文件
│   └── app.js        # Vue 应用逻辑
└── backend/          # 后端代码
    ├── venv/         # Python 虚拟环境
    ├── main.py       # FastAPI 应用
    ├── requirements.txt
    ├── start.bat     # Windows 启动脚本
    └── README.md
```

## 快速开始

### 1. 配置 DeepSeek API Key

编辑 `backend/.env` 文件，填入你的 API Key：

```env
DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 2. 启动后端服务

```bash
cd backend
python main.py
```

或者在 Windows 上双击 `backend/start.bat`

后端服务将在 http://localhost:8000 启动

### 3. 打开前端页面

直接在浏览器中打开 `frontend/index.html` 文件

## 功能特性

- ✅ 左侧任务列表，支持切换和创建新任务
- ✅ 中间聊天区域，用户消息显示在右边
- ✅ 底部输入框，支持发送消息到后端
- ✅ 右侧文件预览面板，点击文件标签弹出
- ✅ 接入 DeepSeek Reasoner 模型
- ✅ 支持多轮对话上下文
- ✅ 后端控制台打印模型返回结果
- ✅ 显示模型思维链内容

## API 接口

### POST /api/chat

接收前端消息，调用 DeepSeek Reasoner 模型，返回 AI 回复

**请求：**
```json
{
    "text": "用户消息",
    "taskId": 1
}
```

**响应：**
```json
{
    "text": "DeepSeek 模型的回复",
    "time": "14:30",
    "reasoning": "模型的思维链内容",
    "files": []
}
```

### DELETE /api/chat/history/{task_id}

清除指定任务的对话历史

## 技术栈

**前端：**
- HTML5
- CSS3
- Vue.js 3 (CDN)

**后端：**
- Python 3
- FastAPI
- Uvicorn
- Pydantic

## 开发说明

后端服务启动后，会在控制台打印：
- 收到的用户消息
- DeepSeek 模型的思维链内容（前 200 字符）
- DeepSeek 模型的完整回复

前端发送消息时会自动调用后端接口，后端通过 DeepSeek Reasoner 模型生成回复，并将结果显示在聊天区域左侧。

## 注意事项

1. **必须配置 API Key**：在 `backend/.env` 文件中设置你的 DeepSeek API Key
2. 如果没有 API Key，可以访问 [DeepSeek 平台](https://platform.deepseek.com/) 注册获取
3. 每个任务会保持独立的对话上下文
4. 模型会自动处理多轮对话历史
