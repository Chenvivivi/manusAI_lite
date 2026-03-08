const { createApp } = Vue;

createApp({
    data() {
        return {
            inputText: '',
            currentTaskId: 1,
            isGenerating: false,
            abortController: null,
            sidebarCollapsed: false,
            currentFile: null,
            tasks: [
                {
                    id: 1,
                    title: '欢迎使用 ManusAI',
                    time: '刚刚',
                    messages: [
                        {
                            id: 1,
                            type: 'ai',
                            text: '你好！我是 **ManusAI**，很高兴为你服务。\n\n我可以帮助你：\n\n- 回答各种问题\n- 生成代码和文件\n- 进行深度推理和分析\n\n有什么可以帮助你的吗？',
                            time: '14:30',
                            reasoning: '',
                            showReasoning: false,
                            files: []
                        }
                    ]
                },
                {
                    id: 2,
                    title: '创建项目文档',
                    time: '10分钟前',
                    messages: [
                        {
                            id: 1,
                            type: 'user',
                            text: '帮我创建一个项目的 README 文档',
                            time: '14:20',
                            files: []
                        },
                        {
                            id: 2,
                            type: 'ai',
                            text: '好的，我已经为你创建了 **README.md** 文档。\n\n## 包含内容\n\n- 项目介绍\n- 安装步骤\n- 使用说明\n\n请点击下方文件查看详情。',
                            time: '14:21',
                            reasoning: '用户需要创建项目文档。我应该生成一个标准的 README.md 文件，包含项目的基本信息、安装说明和使用方法。',
                            showReasoning: false,
                            files: [
                                {
                                    id: 1,
                                    name: 'README.md',
                                    content: `# 项目名称

## 简介
这是一个示例项目，展示了如何使用现代化的技术栈构建应用。

## 安装

\`\`\`bash
npm install
\`\`\`

## 使用

\`\`\`bash
npm start
\`\`\`

## 功能特性

- 功能 1：用户认证
- 功能 2：数据管理
- 功能 3：实时通信

## 技术栈

- Vue.js 3
- Node.js
- Express
- MongoDB

## 贡献

欢迎提交 Pull Request！

## 许可证

MIT License`
                                }
                            ]
                        }
                    ]
                },
                {
                    id: 3,
                    title: '代码优化建议',
                    time: '1小时前',
                    messages: [
                        {
                            id: 1,
                            type: 'user',
                            text: '请帮我优化这段代码的性能',
                            time: '13:15',
                            files: []
                        },
                        {
                            id: 2,
                            type: 'ai',
                            text: '我已经分析了你的代码，并提供了优化建议。\n\n## 主要优化点\n\n1. **使用 Map 数据结构**\n   - 提高查找效率，从 O(n) 降到 O(1)\n\n2. **添加缓存机制**\n   - 避免重复计算\n\n3. **代码结构优化**\n   - 提取 `formatItem` 函数，提高可读性\n\n请查看重构后的代码文件。',
                            time: '13:16',
                            reasoning: '用户想要优化代码性能。我需要分析代码中的性能瓶颈，主要是重复查找的问题。可以使用 Map 来缓存结果，避免重复计算。',
                            showReasoning: false,
                            files: [
                                {
                                    id: 1,
                                    name: 'optimized-code.js',
                                    content: `// 优化后的代码
function processData(data) {
    // 使用 Map 提高查找效率
    const cache = new Map();
    
    return data.map(item => {
        if (cache.has(item.id)) {
            return cache.get(item.id);
        }
        
        const processed = {
            ...item,
            timestamp: Date.now(),
            formatted: formatItem(item)
        };
        
        cache.set(item.id, processed);
        return processed;
    });
}

function formatItem(item) {
    return \`\${item.name} - \${item.value}\`;
}

export { processData };`
                                }
                            ]
                        }
                    ]
                }
            ],
            filePanel: {
                isOpen: false,
                fileName: '',
                content: ''
            }
        };
    },
    computed: {
        currentMessages() {
            const task = this.tasks.find(t => t.id === this.currentTaskId);
            return task ? task.messages : [];
        }
    },
    methods: {
        async sendMessage() {
            if (!this.inputText.trim()) return;

            const task = this.tasks.find(t => t.id === this.currentTaskId);
            if (!task) return;

            const messageText = this.inputText;
            const userMessage = {
                id: Date.now(),
                type: 'user',
                text: messageText,
                time: this.getCurrentTime(),
                files: []
            };

            task.messages.push(userMessage);

            this.inputText = '';
            this.autoResizeTextarea();

            this.$nextTick(() => {
                this.scrollToBottom();
            });

            const loadingMessageId = Date.now() + 1;
            
            task.messages.push({
                id: loadingMessageId,
                type: 'ai',
                text: '',
                time: this.getCurrentTime(),
                reasoning: '',
                showReasoning: false,
                isLoading: true,
                subtasks: [],
                showSubtasks: true,
                files: []
            });

            this.$nextTick(() => {
                this.scrollToBottom();
            });

            this.isGenerating = true;
            this.abortController = new AbortController();

            try {
                const response = await fetch('http://localhost:8000/api/chat/stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: messageText,
                        taskId: this.currentTaskId
                    }),
                    signal: this.abortController.signal
                });

                if (!response.ok) {
                    throw new Error('网络请求失败');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                
                const getMessage = () => {
                    return task.messages.find(m => m.id === loadingMessageId);
                };

                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                const currentMessage = getMessage();
                                
                                if (!currentMessage) continue;
                                
                                if (data.type === 'plan') {
                                    const subtasks = data.content.subtasks || [];
                                    currentMessage.subtasks = subtasks.map(st => ({
                                        ...st,
                                        status: 'pending'
                                    }));
                                    currentMessage.isLoading = false;
                                    currentMessage.showSubtasks = true;
                                    
                                } else if (data.type === 'task_update') {
                                    const subtaskIndex = currentMessage.subtasks.findIndex(st => st.id === data.task_id);
                                    if (subtaskIndex !== -1) {
                                        currentMessage.subtasks[subtaskIndex] = {
                                            ...currentMessage.subtasks[subtaskIndex],
                                            status: data.status
                                        };
                                    }
                                    
                                } else if (data.type === 'reasoning') {
                                    currentMessage.reasoning += data.content;
                                    currentMessage.isLoading = false;
                                    
                                } else if (data.type === 'content') {
                                    currentMessage.text += data.content;
                                    currentMessage.isLoading = false;
                                    
                                } else if (data.type === 'file') {
                                    // 添加文件
                                    if (!currentMessage.files) {
                                        currentMessage.files = [];
                                    }
                                    currentMessage.files.push(data.file);
                                    
                                } else if (data.type === 'done') {
                                    currentMessage.time = data.time;
                                    currentMessage.isLoading = false;
                                    this.isGenerating = false;
                                    
                                } else if (data.type === 'error') {
                                    currentMessage.text = data.content;
                                    currentMessage.isLoading = false;
                                    this.isGenerating = false;
                                }

                                this.$nextTick(() => {
                                    this.scrollToBottom();
                                });
                                
                            } catch (parseError) {
                                console.error('解析 SSE 数据失败:', parseError, line);
                            }
                        }
                    }
                }

            } catch (error) {
                this.isGenerating = false;
                
                const messageIndex = task.messages.findIndex(m => m.id === loadingMessageId);
                if (messageIndex !== -1) {
                    if (error.name === 'AbortError') {
                        task.messages[messageIndex].text = '⚠️ **回答已暂停**\n\n用户主动停止了回答生成。';
                    } else {
                        console.error('发送消息失败:', error);
                        task.messages[messageIndex].text = '抱歉，连接后端服务失败。请确保后端服务已启动（运行 python main.py）';
                    }
                    task.messages[messageIndex].isLoading = false;
                }

                this.$nextTick(() => {
                    this.scrollToBottom();
                });
            }
        },

        handleEnter(e) {
            if (!e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        },

        selectTask(taskId) {
            this.currentTaskId = taskId;
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        },

        createNewTask() {
            const newTask = {
                id: Date.now(),
                title: `新任务 ${this.tasks.length + 1}`,
                time: '刚刚',
                messages: [
                    {
                        id: Date.now(),
                        type: 'ai',
                        text: '你好！有什么我可以帮助你的吗？',
                        time: this.getCurrentTime(),
                        reasoning: '',
                        showReasoning: false,
                        files: []
                    }
                ]
            };

            this.tasks.unshift(newTask);
            this.currentTaskId = newTask.id;
        },

        stopGenerating() {
            if (this.abortController) {
                this.abortController.abort();
                this.isGenerating = false;
            }
        },
        
        copyMessage(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showCopyToast();
            }).catch(err => {
                console.error('复制失败:', err);
            });
        },
        
        showCopyToast() {
            const toast = document.createElement('div');
            toast.className = 'copy-toast';
            toast.textContent = '✓ 已复制';
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.classList.add('show');
            }, 10);
            
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            }, 2000);
        },
        
        toggleSidebar() {
            this.sidebarCollapsed = !this.sidebarCollapsed;
        },
        
        openFile(file) {
            this.currentFile = file;
        },

        closeFile() {
            this.currentFile = null;
        },

        getCurrentTime() {
            const now = new Date();
            return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        },

        scrollToBottom() {
            const container = this.$refs.chatMessages;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        },

        autoResizeTextarea() {
            this.$nextTick(() => {
                const textarea = this.$refs.inputTextarea;
                if (textarea) {
                    textarea.style.height = 'auto';
                    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
                }
            });
        },

        toggleReasoning(messageId) {
            const task = this.tasks.find(t => t.id === this.currentTaskId);
            if (!task) return;
            
            const message = task.messages.find(m => m.id === messageId);
            if (message) {
                message.showReasoning = !message.showReasoning;
            }
        },

        toggleSubtasks(messageId) {
            const task = this.tasks.find(t => t.id === this.currentTaskId);
            if (!task) return;
            
            const message = task.messages.find(m => m.id === messageId);
            if (message) {
                message.showSubtasks = !message.showSubtasks;
            }
        },

        renderMarkdown(text) {
            if (!text) return '';
            
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {}
                    }
                    return hljs.highlightAuto(code).value;
                },
                breaks: true,
                gfm: true
            });
            
            return marked.parse(text);
        },

        getCompletedCount(message) {
            if (!message.subtasks) return 0;
            return message.subtasks.filter(st => st.status === 'completed').length;
        },

        getStatusText(status) {
            const statusMap = {
                'pending': '等待中',
                'running': '执行中',
                'completed': '已完成',
                'failed': '失败'
            };
            return statusMap[status] || status;
        }
    },
    mounted() {
        this.scrollToBottom();
        
        this.$watch('inputText', () => {
            this.autoResizeTextarea();
        });
    }
}).mount('#app');
