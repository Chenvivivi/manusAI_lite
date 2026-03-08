# UI 优化 - 第二轮

**更新时间**: 2026-03-08

## 修改内容

### 1. 简化任务规划列表 ✓

**修改前**：
- 使用卡片形式展示每个子任务
- 显示任务ID、类型、状态、工具名称、参数等详细信息
- 占用较大空间

**修改后**：
- 简化为列表形式
- 只显示任务名称（描述）
- 完成的任务前显示 `✓`，未完成显示 `○`
- 标题显示进度：`任务规划 (2/4)`

**代码位置**：
- `frontend/index.html`: 第 62-88 行（简化的任务列表）
- `frontend/style.css`: 新增 `.subtasks-list`, `.subtask-simple-item` 等样式

---

### 2. 优化复制按钮样式 ✓

**修改前**：
- 只有一个 📋 emoji 图标
- 背景色较明显

**修改后**：
- 使用 SVG 图标 + "复制" 文字
- 更接近 DeepSeek 的简洁风格
- 透明背景，边框更细
- hover 时有微妙的背景色变化

**代码位置**：
- `frontend/index.html`: 第 129-136 行（新的按钮结构）
- `frontend/style.css`: 第 1058-1085 行（新的按钮样式）

---

### 3. 实现真正的流式输出 ✓

**问题**：
- 之前的实现是先流式输出 Reasoner 结果，然后用 Verifier 结果整体替换
- 导致用户看到的是"突然替换"，而不是逐字输出

**解决方案**：
- 改为先完整获取 Reasoner 的响应（非流式）
- 调用 Verifier 进行优化
- 然后**模拟流式输出** Verifier 的最终结果
- 思考过程：每次 50 字符，延迟 0.01 秒
- 最终答案：每次 30 字符，延迟 0.01 秒

**代码位置**：
- `backend/main.py`: 第 383-488 行（新的流式输出逻辑）
- `frontend/app.js`: 移除了 `verified_content` 事件的处理

---

### 4. 调整显示顺序 ✓

**修改前**：
- 子任务规划 → 思考过程 → 消息内容

**修改后**：
- 思考过程 → 子任务规划 → 消息内容

**代码位置**：
- `frontend/index.html`: 第 102-128 行（调整了元素顺序）

---

### 5. 简化来源文件内容 ✓

**修改前**：
- 包含搜索引擎信息
- 包含各引擎的直接答案
- 包含详细摘要

**修改后**：
- 只显示标题和链接
- 格式更简洁清晰

**代码位置**：
- `backend/main.py`: 第 68-130 行（`_generate_sources_file` 函数）

---

## 技术细节

### 流式输出实现

```python
# 模拟流式输出思考过程
if final_reasoning:
    chunk_size = 50
    for i in range(0, len(final_reasoning), chunk_size):
        chunk = final_reasoning[i:i+chunk_size]
        yield f"data: {json.dumps({'type': 'reasoning', 'content': chunk}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.01)

# 模拟流式输出最终答案
chunk_size = 30
for i in range(0, len(final_answer), chunk_size):
    chunk = final_answer[i:i+chunk_size]
    yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"
    await asyncio.sleep(0.01)
```

### 简化任务列表样式

```css
.subtask-simple-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
}

.check-mark {
    color: #4ade80;  /* 绿色对勾 */
}

.check-placeholder {
    color: rgba(255, 255, 255, 0.3);  /* 灰色圆圈 */
}
```

---

## 测试步骤

1. **刷新前端页面**（Ctrl + F5）
2. **发送测试消息**
3. **观察效果**：
   - 思考过程逐字出现
   - 任务规划以简洁列表形式显示
   - 答案逐字出现（流式输出）
   - 复制按钮样式更简洁
   - 点击来源文件查看简化的内容

---

## 性能优化

- 流式输出延迟设置为 0.01 秒，在流畅度和速度之间取得平衡
- 思考过程 chunk 大小为 50 字符
- 答案 chunk 大小为 30 字符（更细腻的打字效果）

---

## 后续优化建议

1. 可以根据用户反馈调整流式输出的速度
2. 可以添加"跳过动画"按钮，直接显示完整内容
3. 可以为复制按钮添加复制成功后的图标变化（✓）
