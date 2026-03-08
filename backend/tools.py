"""
工具列表定义
维护所有可供模型调用的工具
"""

TOOLS = [
    {
        "name": "web_search",
        "description": "在互联网上搜索信息，获取最新的、实时的知识和数据。适用于需要查询当前信息、技术文档、新闻动态等场景。支持多种搜索引擎（Tavily、Serper、百度千帆）。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词或问题，应该清晰、具体，包含核心概念"
                },
                "max_results": {
                    "type": "integer",
                    "description": "返回的最大搜索结果数量，默认为 5",
                    "default": 5
                },
                "search_depth": {
                    "type": "string",
                    "description": "搜索深度: basic(快速), advanced(深度)",
                    "enum": ["basic", "advanced"],
                    "default": "basic"
                }
            },
            "required": ["query"]
        },
        "examples": [
            {
                "query": "Vue.js 3.0 新特性",
                "max_results": 5,
                "search_depth": "basic"
            },
            {
                "query": "React 18 性能优化",
                "max_results": 3,
                "search_depth": "advanced"
            }
        ]
    }
]

def get_tool_by_name(tool_name: str):
    """根据工具名称获取工具定义"""
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool
    return None

def get_all_tools():
    """获取所有工具列表"""
    return TOOLS

def format_tools_for_prompt():
    """将工具列表格式化为提示词中的描述"""
    tools_desc = []
    for tool in TOOLS:
        tool_info = f"""
工具名称: {tool['name']}
工具描述: {tool['description']}
参数说明: {tool['parameters']}
"""
        tools_desc.append(tool_info.strip())
    
    return "\n\n".join(tools_desc)
