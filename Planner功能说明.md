# 🎯 Planner 智能体功能说明

## ✅ 已完成的功能

### 1. 工具列表维护 🔧

**文件位置**: `backend/tools.py`

**当前工具**:

#### web_search（网络搜索工具）
- **工具名称**: `web_search`
- **工具描述**: 在互联网上搜索信息，获取最新的、实时的知识和数据
- **接收参数**:
  - `query` (必需): 搜索关键词或问题
  - `max_results` (可选): 返回的最大结果数量，默认 5

**工具定义示例**:
```python
{
    "name": "web_search",
    "description": "在互联网上搜索信息...",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词"
            },
            "max_results": {
                "type": "integer",
                "description": "返回的最大搜索结果数量",
                "default": 5
            }
        },
        "required": ["query"]
    }
}
```

### 2. Planner 提示词系统 📝

**文件位置**: `backend/prompts.py`

**核心内容**:
- `PLANNER_SYSTEM_PROMPT`: 完整的系统提示词
- `get_planner_prompt(user_query)`: 生成提示词的函数

**提示词包含**:
- Planner 的角色定义
- 可用工具列表（自动从 tools.py 读取）
- 子任务类型说明（tool_call 和 synthesis）
- 输出格式规范（JSON）
- 规划原则和示例

### 3. 子任务拆解逻辑 🧩

**Planner 不直接返回工具调用，而是返回子任务列表**

#### 示例：分析 Vue 和 React 的区别

**用户输入**:
```
分析 Vue 和 React 的区别
```

**Planner 返回的子任务**:
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
      "description": "对比分析 Vue 和 React 的区别，总结各自的优缺点和适用场景",
      "dependencies": [1, 2]
    }
  ]
}
```

**说明**:
- 子任务 1: 搜索 Vue
- 子任务 2: 搜索 React
- 子任务 3: 综合对比（依赖 1 和 2）

## 🎨 前端展示效果

### 子任务规划区域（绿色主题）

```
┌────────────────────────────────────────┐
│ 📋 任务规划 (3 个子任务) ▶            │
└────────────────────────────────────────┘
```

点击展开后：

```
┌────────────────────────────────────────┐
│ 📋 任务规划 (3 个子任务) ▼            │
├────────────────────────────────────────┤
│ ┌────────────────────────────────────┐ │
│ │ ① 🔧 工具调用                      │ │
│ │ 搜索 Vue.js 的特性和优势           │ │
│ │ 工具: web_search                   │ │
│ │ 参数: {"query": "Vue.js...", ...}  │ │
│ └────────────────────────────────────┘ │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ ② 🔧 工具调用                      │ │
│ │ 搜索 React 的特性和优势            │ │
│ │ 工具: web_search                   │ │
│ │ 参数: {"query": "React...", ...}   │ │
│ └────────────────────────────────────┘ │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │ ③ 🧠 综合分析                      │ │
│ │ 对比分析 Vue 和 React 的区别       │ │
│ │ 依赖: 子任务 1, 2                  │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## 🔄 完整工作流程

### 用户发送消息后

1. **显示加载动画**
   ```
   规划中 • • •
   ```

2. **Planner 规划子任务**
   - 调用 `deepseek-chat` 模型
   - 使用 Planner 提示词
   - 返回 JSON 格式的子任务列表

3. **展示子任务规划**
   - 绿色区域显示所有子任务
   - 可以展开/折叠查看详情

4. **执行推理和回答**
   - 调用 `deepseek-reasoner` 模型
   - 流式输出思考过程
   - 流式输出最终回答（Markdown 渲染）

5. **完成**
   - 显示时间戳
   - 可以继续对话

## 📊 后端控制台输出

```
==================================================
[2026-03-08 15:30:00] 收到用户消息:
任务ID: 1
消息内容: 分析 Vue 和 React 的区别
--------------------------------------------------
步骤 1: 调用 Planner 规划子任务...
Planner 规划: {
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

步骤 2: 调用 DeepSeek deepseek-reasoner 模型（流式）...
思维链内容: [包含特殊字符，长度 XXX]
模型回复: [包含特殊字符，长度 XXX]
==================================================
```

## 🎯 测试建议

试试这些问题，查看 Planner 的规划效果：

1. **简单问答**:
   - "什么是机器学习？"
   - 预期：1 个 synthesis 任务

2. **需要搜索**:
   - "2026年最新的 AI 技术有哪些？"
   - 预期：1 个 tool_call + 1 个 synthesis

3. **对比分析**:
   - "比较 Python 和 JavaScript"
   - 预期：2 个 tool_call + 1 个 synthesis

4. **复杂查询**:
   - "分析 Vue、React 和 Angular 三个框架的优缺点"
   - 预期：3 个 tool_call + 1 个 synthesis

## 📁 文件总结

| 文件 | 作用 | 内容 |
|------|------|------|
| `backend/tools.py` | 工具列表 | 定义所有可用工具（当前 1 个：web_search） |
| `backend/prompts.py` | Planner 提示词 | 系统提示词和提示词生成函数 |
| `backend/main.py` | 主程序 | 集成 Planner，实现流式输出 |
| `frontend/index.html` | 前端页面 | 添加子任务展示区域 |
| `frontend/app.js` | 前端逻辑 | 处理子任务数据，添加切换功能 |
| `frontend/style.css` | 样式文件 | 子任务区域样式（绿色主题） |

所有功能已完成，现在可以测试了！
