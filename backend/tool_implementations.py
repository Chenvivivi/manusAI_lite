"""
工具实现
实际执行工具调用的函数
"""

import asyncio
from typing import Dict, Any, List
from search_tools import unified_search

async def web_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    parallel: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    网络搜索工具实现
    支持多种搜索引擎：Tavily、Serper、百度千帆
    默认并行调用所有可用引擎
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量
        search_depth: 搜索深度 (basic/advanced)
        parallel: 是否并行搜索（默认 True）
        **kwargs: 其他参数
        
    Returns:
        搜索结果
    """
    print(f"  → 执行搜索: {query}")
    print(f"  → 最大结果数: {max_results}")
    print(f"  → 搜索深度: {search_depth}")
    print(f"  → 搜索模式: {'并行' if parallel else '顺序'}")
    
    try:
        result = await unified_search.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            parallel=parallel,
            **kwargs
        )
        
        # 根据是否并行显示不同的日志
        if result.get('engines'):
            # 并行搜索
            engines = result.get('engines', [])
            print(f"  ✓ 搜索完成，使用引擎: {', '.join(engines)}")
        else:
            # 单引擎搜索
            print(f"  ✓ 搜索完成，使用引擎: {result.get('engine', 'Unknown')}")
        
        print(f"  ✓ 返回结果数: {len(result.get('results', []))}")
        
        return result
    
    except Exception as e:
        print(f"  ✗ 搜索失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        }

TOOL_REGISTRY = {
    'web_search': web_search
}

def get_tool_function(tool_name: str):
    """
    获取工具执行函数
    
    Args:
        tool_name: 工具名称
        
    Returns:
        工具函数或 None
    """
    return TOOL_REGISTRY.get(tool_name)
