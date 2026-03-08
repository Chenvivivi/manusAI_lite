# 🔑 API Key 获取指南

## 快速导航

- [Tavily](#1-tavily-推荐) - 最推荐，5分钟完成
- [Serper](#2-serper) - Google搜索，额度最多
- [百度千帆](#3-百度千帆) - 中文搜索优化

---

## 1. Tavily（推荐）

### ⭐ 为什么推荐
- ✅ 注册最简单（支持 Google/GitHub 登录）
- ✅ 专为 AI 优化，返回结果最适合
- ✅ 包含直接答案
- ✅ 免费额度充足（1000次/月）

### 📝 获取步骤

#### 步骤 1：访问官网
打开浏览器，访问：https://tavily.com/

#### 步骤 2：注册账号
1. 点击右上角 **"Sign Up"** 按钮
2. 选择注册方式：
   - **推荐**：使用 Google 账号登录（最快）
   - 或使用 GitHub 账号登录
   - 或使用邮箱注册

#### 步骤 3：获取 API Key
1. 登录后会自动跳转到 Dashboard
2. 在页面中间会显示你的 API Key
3. 格式类似：`tvly-xxxxxxxxxxxxxxxxxxxxxxxx`
4. 点击复制按钮

#### 步骤 4：配置到项目
1. 打开 `backend/.env` 文件
2. 找到这一行：
   ```bash
   TAVILY_API_KEY=your_tavily_api_key_here
   ```
3. 替换为你的实际 API Key：
   ```bash
   TAVILY_API_KEY=tvly-你复制的key
   ```
4. 保存文件

### ✅ 验证
重启后端服务，发送测试消息，查看日志应该显示：
```
→ 启动 Tavily 搜索任务...
✓ Tavily 搜索成功，返回 5 条结果
```

---

## 2. Serper

### ⭐ 特点
- ✅ 基于 Google 搜索
- ✅ 免费额度最多（2500次）
- ✅ 搜索结果质量高
- ✅ 响应速度快

### 📝 获取步骤

#### 步骤 1：访问官网
打开浏览器，访问：https://serper.dev/

#### 步骤 2：注册账号
1. 点击 **"Sign Up"** 按钮
2. 推荐使用 Google 账号登录（最快）
3. 或使用邮箱注册

#### 步骤 3：获取 API Key
1. 登录后，点击左侧菜单的 **"API Keys"**
2. 点击 **"Create API Key"** 按钮
3. 给 API Key 起个名字（比如 "ManusAI"）
4. 点击 **"Create"**
5. 复制生成的 API Key

#### 步骤 4：配置到项目
1. 打开 `backend/.env` 文件
2. 找到这一行：
   ```bash
   SERPER_API_KEY=your_serper_api_key_here
   ```
3. 替换为你的实际 API Key：
   ```bash
   SERPER_API_KEY=你复制的key
   ```
4. 保存文件

### ✅ 验证
重启后端服务，发送测试消息，查看日志应该显示：
```
→ 启动 Serper 搜索任务...
✓ Serper 搜索成功，返回 5 条结果
```

---

## 3. 百度千帆

### ⭐ 特点
- ✅ 中文搜索效果最好
- ✅ 百度生态集成
- ✅ 每日免费额度（100次/天）

### 📝 获取步骤

#### 步骤 1：访问官网
打开浏览器，访问：https://qianfan.cloud.baidu.com/

#### 步骤 2：登录百度账号
1. 点击 **"登录"** 按钮
2. 使用百度账号登录（如果没有需要先注册）

#### 步骤 3：创建应用
1. 进入 **"控制台"**
2. 点击 **"应用接入"** -> **"创建应用"**
3. 填写应用信息：
   - 应用名称：ManusAI
   - 应用描述：AI 搜索助手
4. 点击 **"确定"**

#### 步骤 4：获取 API Key
1. 在应用列表中找到刚创建的应用
2. 点击 **"查看"** 或 **"管理"**
3. 找到 **"API Key"** 和 **"Secret Key"**
4. 复制 **API Key**（注意：是 API Key，不是 Secret Key）

#### 步骤 5：配置到项目
1. 打开 `backend/.env` 文件
2. 找到这一行：
   ```bash
   QIANFAN_API_KEY=your_qianfan_api_key_here
   ```
3. 替换为你的实际 API Key：
   ```bash
   QIANFAN_API_KEY=你复制的key
   ```
4. 保存文件

### ✅ 验证
重启后端服务，发送测试消息，查看日志应该显示：
```
→ 启动 Qianfan 搜索任务...
✓ Qianfan 搜索成功，返回 5 条结果
```

---

## 📋 配置检查清单

完成后，你的 `backend/.env` 文件应该类似这样：

```bash
# DeepSeek API 配置（必需）
DEEPSEEK_API_KEY=sk-4fa2f742b78d44fab5c17030e6696246
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner

# 搜索引擎 API 配置
# Tavily - 专为 AI 优化的搜索引擎（推荐）
TAVILY_API_KEY=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

# Serper - Google 搜索 API
SERPER_API_KEY=xyz789uvw456rst123opq890lmn567

# 百度千帆搜索
QIANFAN_API_KEY=pqr456stu789vwx012yza345bcd678
```

### ✅ 检查要点

- [ ] 所有 API Key 都已替换（不再是 `your_xxx_api_key_here`）
- [ ] API Key 没有多余的空格
- [ ] API Key 没有加引号
- [ ] 文件已保存
- [ ] 后端服务已重启

---

## 🧪 测试配置

### 1. 重启后端服务

如果后端正在运行，先停止（Ctrl+C），然后重新启动：

```bash
cd backend
python main.py
```

### 2. 发送测试消息

打开前端页面 `frontend/index.html`，发送：

```
搜索 Python 3.12 新特性
```

### 3. 查看后端日志

应该看到类似这样的输出：

```
【步骤 2】Executor 开始执行子任务...
  → 执行搜索: Python 3.12 新特性
  → 搜索模式: 并行
  → 开始并行搜索，使用所有可用引擎...
  → 启动 Tavily 搜索任务...
  → 启动 Serper 搜索任务...
  → 启动 Qianfan 搜索任务...
  ✓ Tavily 搜索成功，返回 5 条结果
  ✓ Serper 搜索成功，返回 5 条结果
  ✓ Qianfan 搜索成功，返回 5 条结果
  ✓ 并行搜索完成，合并了 3 个引擎的结果
```

---

## ❓ 常见问题

### Q1: 我只想配置一个引擎可以吗？

**A**: 可以！至少配置一个即可。推荐配置 Tavily。

### Q2: API Key 在哪里找？

**A**: 
- **Tavily**: 登录后在 Dashboard 页面
- **Serper**: 左侧菜单 "API Keys" 页面
- **Qianfan**: 应用管理页面

### Q3: 配置后没有生效？

**A**: 
1. 确认 `.env` 文件在 `backend/` 目录下
2. 确认 API Key 已正确替换
3. 重启后端服务
4. 查看后端日志确认

### Q4: 显示 "API Key 未配置"？

**A**: 
检查 `.env` 文件中的 API Key 是否还是 `your_xxx_api_key_here`，需要替换为实际的 Key。

### Q5: 显示 "401 Unauthorized"？

**A**: 
API Key 无效或已过期，请：
1. 检查是否正确复制
2. 重新生成 API Key
3. 确认账号状态正常

---

## 💡 推荐配置

### 最佳配置（三个都配）
```bash
TAVILY_API_KEY=tvly-xxx
SERPER_API_KEY=xxx
QIANFAN_API_KEY=xxx
```
**优势**：最全面的搜索结果，自动故障切换

### 推荐配置（配两个）
```bash
TAVILY_API_KEY=tvly-xxx
SERPER_API_KEY=xxx
```
**优势**：平衡质量和额度，英文搜索最优

### 最小配置（只配一个）
```bash
TAVILY_API_KEY=tvly-xxx
```
**优势**：配置简单，AI 优化最好

---

## 🎉 配置完成

配置完成后，你的系统就可以：

1. ✅ 同时调用三个搜索引擎
2. ✅ 获取更全面的搜索结果
3. ✅ 自动合并去重
4. ✅ 生成更准确的回答

**开始使用吧！**🚀
