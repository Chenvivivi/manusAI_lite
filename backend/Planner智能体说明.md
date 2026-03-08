# Planner 智能体说明文档

## 📋 概述

Planner 智能体负责将用户的复杂查询拆解为可执行的子任务序列，是 ManusAI 的任务规划核心。

## 📂 文件位置

### 1. 工具列表
**文件**: `backend/tools.py`

**内容**:
- 维护所有可用工具的定义
- 当前包含 1 个工具：`web_search`（网络搜索工具）

**工具定义**:
```python
{
    "name": "web_search",
    "description": "在互联网上搜索信息，获取最新的、实时的知识和数据",
    "parameters": {
        "query": "搜索关键词",
        "max_results": "返回结果数量（默认 5）"
    }
}
```

### 2. Planner 提示词
**文件**: `backend/prompts.py`

**内容**:
- `PLANNER_SYSTEM_PROMPT`: Planner 的系统提示词
- `get_planner_prompt()`: 生成完整提示词的函数

**提示词功能**:
- 定义 Planner 的角色和职责
- 说明可用工具列表
- 规定子任务的类型和格式
- 提供规划示例和原则

## 🎯 Planner 工作流程

### 输入
用户的原始查询，例如：
- "分析 Vue 和 React 的区别"
- "2026年最流行的前端框架有哪些？"

### 处理
1. 接收用户查询
2. 调用 DeepSeek Chat 模型（使用 Planner 提示词）
3. 模型分析查询意图
4. 规划子任务序列

### 输出
JSON 格式的子任务列表：

```json
{
  "subtasks": [
    {
      "id": 1,
      "type": "tool_call",
      "tool_name": "web_search",
      "description": "搜索 Vue.js 的特性和优势",
      "parameters": {
        "query": "Vue.js 特性 优势 2026",
        "max_results": 5
      }
    },
    {
      "id": 2,
      "type": "tool_call",
      "tool_name": "web_search",
      "description": "搜索 React 的特性和优势",
      "parameters": {
        "query": "React 特性 优势 2026",
        "max_results": 5
      }
    },
    {
      "id": 3,
      "type": "synthesis",
      "description": "对比分析 Vue 和 React 的区别",
      "dependencies": [1, 2]
    }
  ]
}
```

## 📝 子任务类型

### 1. tool_call（工具调用）
**用途**: 需要调用外部工具获取信息

**字段**:
- `id`: 子任务唯一标识
- `type`: "tool_call"
- `tool_name`: 要调用的工具名称
- `description`: 任务描述
- `parameters`: 工具参数

**示例**:
```json
{
  "id": 1,
  "type": "tool_call",
  "tool_name": "web_search",
  "description": "搜索 Python 最新版本信息",
  "parameters": {
    "query": "Python 3.14 新特性 2026",
    "max_results": 5
  }
}
```

### 2. synthesis（综合分析）
**用途**: 基于前面任务的结果进行分析、总结、对比

**字段**:
- `id`: 子任务唯一标识
- `type`: "synthesis"
- `description`: 任务描述
- `dependencies`: 依赖的前置任务 ID 列表

**示例**:
```json
{
  "id": 3,
  "type": "synthesis",
  "description": "综合分析并总结前端框架的发展趋势",
  "dependencies": [1, 2]
}
```

## 🧪 测试示例

### 示例 1: 简单问答
**用户输入**: "什么是 Python？"

**Planner 规划**:
```json
{
  "subtasks": [
    {
      "id": 1,
      "type": "synthesis",
      "description": "解释 Python 编程语言的定义、特点和应用",
      "dependencies": []
    }
  ]
}
```

### 示例 2: 需要搜索
**用户输入**: "2026年最流行的前端框架有哪些？"

**Planner 规划**:
```json
{
  "subtasks": [
    {
      "id": 1,
      "type": "tool_call",
      "tool_name": "web_search",
      "description": "搜索 2026 年最流行的前端框架",
      "parameters": {
        "query": "2026 最流行前端框架排名",
        "max_results": 5
      }
    },
    {
      "id": 2,
      "type": "synthesis",
      "description": "总结 2026 年最流行的前端框架及其特点",
      "dependencies": [1]
    }
  ]
}
```

### 示例 3: 对比分析（你的例子）
**用户输入**: "分析 Vue 和 React 的区别"

**Planner 规划**:
```json
{
  "subtasks": [
    {
      "id": 1,
      "type": "tool_call",
      "tool_name": "web_search",
      "description": "搜索 Vue.js 的特性和优势",
      "parameters": {
        "query": "Vue.js 特性 优势 应用场景 2026",
        "max_results": 5
      }
    },
    {
      "id": 2,
      "type": "tool_call",
      "tool_name": "web_search",
      "description": "搜索 React 的特性和优势",
      "parameters": {
        "query": "React 特性 优势 应用场景 2026",
        "max_results": 5
      }
    },
    {
      "id": 3,
      "type": "synthesis",
      "description": "综合对比 Vue 和 React 的区别，总结各自优缺点",
      "dependencies": [1, 2]
    }
  ]
}
```

## 🔧 API 接口

### GET /api/tools
获取所有可用工具列表

**响应**:
```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "...",
      "parameters": {...}
    }
  ]
}
```

### POST /api/planner
调用 Planner 规划子任务

**请求**:
```json
{
  "text": "用户查询",
  "taskId": 1
}
```

**响应**:
```json
{
  "success": true,
  "plan": {
    "subtasks": [...]
  },
  "timestamp": "2026-03-08T15:30:00"
}
```

### POST /api/chat/stream
流式对话接口（已集成 Planner）

**流程**:
1. 调用 Planner 规划子任务
2. 推送 `plan` 类型的数据
3. 调用 DeepSeek Reasoner 生成回答
4. 流式推送 `reasoning` 和 `content`

## 🎨 前端展示

### 子任务规划区域
- 绿色主题（区别于思考过程的紫色）
- 显示"📋 任务规划 (X 个子任务)"
- 可折叠/展开
- 每个子任务显示：
  - 序号（圆形徽章）
  - 类型（工具调用 🔧 / 综合分析 🧠）
  - 描述
  - 工具名称和参数（如果是 tool_call）
  - 依赖关系（如果是 synthesis）

### 视觉效果
```
┌─────────────────────────────────┐
│ 📋 任务规划 (3 个子任务) ▼     │
├─────────────────────────────────┤
│ ① 🔧 工具调用                   │
│   搜索 Vue.js 的特性和优势      │
│   工具: web_search              │
│   参数: {"query": "Vue.js..."}  │
├─────────────────────────────────┤
│ ② 🔧 工具调用                   │
│   搜索 React 的特性和优势       │
│   工具: web_search              │
│   参数: {"query": "React..."}   │
├─────────────────────────────────┤
│ ③ 🧠 综合分析                   │
│   对比分析 Vue 和 React 的区别  │
│   依赖: 子任务 1, 2             │
└─────────────────────────────────┘
```

## 🚀 使用方式

### 后端
```python
from prompts import get_planner_prompt
from tools import get_all_tools

# 获取 Planner 提示词
system_prompt, user_prompt = get_planner_prompt(user_query)

# 调用模型
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"}
)

# 解析结果
plan = json.loads(response.choices[0].message.content)
```

### 前端
子任务会自动显示在 AI 回复的顶部，用户可以：
- 查看完整的任务规划
- 了解 AI 如何拆解问题
- 看到每个子任务的具体内容

## 📊 规划原则

1. **简单优先**: 简单问题不需要工具，直接 synthesis
2. **信息收集**: 需要最新信息时，使用 web_search
3. **独立搜索**: 对比多个对象时，为每个对象独立搜索
4. **综合分析**: 最后整合所有信息
5. **避免冗余**: 不创建重复的搜索任务
6. **顺序合理**: 先收集信息，再分析综合

## 💡 扩展建议

未来可以添加更多工具：
- `code_search`: 搜索代码示例
- `document_query`: 查询文档数据库
- `calculator`: 数学计算
- `file_generator`: 生成文件
- `image_search`: 搜索图片

每个工具都需要在 `tools.py` 中定义名称、描述和参数。
