"""
搜索工具实现
支持多种搜索引擎：Tavily、Serper、百度千帆
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class SearchToolError(Exception):
    """搜索工具异常"""
    pass


class TavilySearch:
    """Tavily 搜索工具 - 专为 AI 优化的搜索引擎"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.base_url = "https://api.tavily.com"
        
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行 Tavily 搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: 搜索深度 (basic/advanced)
            include_domains: 包含的域名列表
            exclude_domains: 排除的域名列表
        
        Returns:
            搜索结果字典
        """
        if not self.api_key:
            raise SearchToolError("Tavily API key not found. Please set TAVILY_API_KEY environment variable.")
        
        url = f"{self.base_url}/search"
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise SearchToolError(f"Tavily API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "engine": "Tavily",
                        "query": query,
                        "answer": data.get("answer", ""),
                        "results": [
                            {
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "content": result.get("content", ""),
                                "score": result.get("score", 0)
                            }
                            for result in data.get("results", [])
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
        
        except asyncio.TimeoutError:
            raise SearchToolError("Tavily search timeout")
        except Exception as e:
            raise SearchToolError(f"Tavily search failed: {str(e)}")


class SerperSearch:
    """Serper 搜索工具 - Google 搜索 API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev"
        
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_type: str = "search"
    ) -> Dict[str, Any]:
        """
        执行 Serper 搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_type: 搜索类型 (search/news/images等)
        
        Returns:
            搜索结果字典
        """
        if not self.api_key:
            raise SearchToolError("Serper API key not found. Please set SERPER_API_KEY environment variable.")
        
        url = f"{self.base_url}/{search_type}"
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": max_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise SearchToolError(f"Serper API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    organic_results = data.get("organic", [])
                    
                    return {
                        "success": True,
                        "engine": "Serper",
                        "query": query,
                        "answer": data.get("answerBox", {}).get("answer", ""),
                        "results": [
                            {
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "content": result.get("snippet", ""),
                                "position": result.get("position", 0)
                            }
                            for result in organic_results[:max_results]
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
        
        except asyncio.TimeoutError:
            raise SearchToolError("Serper search timeout")
        except Exception as e:
            raise SearchToolError(f"Serper search failed: {str(e)}")


class QianfanSearch:
    """百度千帆搜索工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('QIANFAN_API_KEY')
        self.base_url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
        
    async def search(
        self,
        query: str,
        max_results: int = 5,
        edition: str = "lite"
    ) -> Dict[str, Any]:
        """
        执行百度千帆搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            edition: 版本 (standard/lite)
        
        Returns:
            搜索结果字典
        """
        if not self.api_key:
            raise SearchToolError("Qianfan API key not found. Please set QIANFAN_API_KEY environment variable.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": query[:72]  # 限制 72 字符
                }
            ],
            "search_source": "baidu_search_v2",
            "edition": edition,
            "resource_type_filter": {
                "web": {"top_k": min(max_results, 50)}
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise SearchToolError(f"Qianfan API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    search_results = data.get("search_results", {}).get("web", [])
                    
                    return {
                        "success": True,
                        "engine": "Qianfan",
                        "query": query,
                        "answer": data.get("result", ""),
                        "results": [
                            {
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "content": result.get("abstract", ""),
                                "rank": result.get("rank", 0)
                            }
                            for result in search_results[:max_results]
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
        
        except asyncio.TimeoutError:
            raise SearchToolError("Qianfan search timeout")
        except Exception as e:
            raise SearchToolError(f"Qianfan search failed: {str(e)}")


class UnifiedSearchTool:
    """统一搜索工具 - 支持单引擎或多引擎并行搜索"""
    
    def __init__(self):
        self.tavily = TavilySearch()
        self.serper = SerperSearch()
        self.qianfan = QianfanSearch()
    
    def _get_engines(self):
        """动态获取引擎列表（每次调用时重新读取环境变量）"""
        return [
            ("Tavily", self.tavily, os.getenv('TAVILY_API_KEY')),
            ("Serper", self.serper, os.getenv('SERPER_API_KEY')),
            ("Qianfan", self.qianfan, os.getenv('QIANFAN_API_KEY'))
        ]
    
    async def search_parallel(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        **kwargs
    ) -> Dict[str, Any]:
        """
        并行调用所有可用的搜索引擎
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: 搜索深度
            **kwargs: 其他参数
        
        Returns:
            合并后的搜索结果字典
        """
        print(f"  → 开始并行搜索，使用所有可用引擎...")
        
        tasks = []
        engine_names = []
        
        for engine_name, engine, api_key in self._get_engines():
            if not api_key or api_key == f"your_{engine_name.lower()}_api_key_here":
                print(f"  ⚠ {engine_name} API Key 未配置，跳过")
                continue
            
            print(f"  → 启动 {engine_name} 搜索任务...")
            
            if engine_name == "Tavily":
                task = engine.search(
                    query=query,
                    max_results=max_results,
                    search_depth=search_depth,
                    **kwargs
                )
            elif engine_name == "Serper":
                task = engine.search(
                    query=query,
                    max_results=max_results
                )
            else:  # Qianfan
                task = engine.search(
                    query=query,
                    max_results=max_results
                )
            
            tasks.append(task)
            engine_names.append(engine_name)
        
        if not tasks:
            print("  ⚠ 没有可用的搜索引擎，返回模拟数据")
            return await self._mock_search(query, max_results)
        
        # 并行执行所有搜索任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整合结果
        successful_results = []
        failed_engines = []
        
        for engine_name, result in zip(engine_names, results):
            if isinstance(result, Exception):
                error_msg = str(result)
                print(f"  ✗ {engine_name} 搜索失败: {error_msg}")
                failed_engines.append(engine_name)
            else:
                print(f"  ✓ {engine_name} 搜索成功，返回 {len(result.get('results', []))} 条结果")
                successful_results.append(result)
        
        if not successful_results:
            print("  ⚠ 所有搜索引擎都失败，返回模拟数据")
            return await self._mock_search(query, max_results)
        
        # 合并所有成功的搜索结果
        merged_result = self._merge_results(successful_results, query)
        print(f"  ✓ 并行搜索完成，合并了 {len(successful_results)} 个引擎的结果")
        
        return merged_result
    
    def _merge_results(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        合并多个搜索引擎的结果
        
        Args:
            results: 搜索结果列表
            query: 搜索查询
        
        Returns:
            合并后的结果
        """
        merged = {
            "success": True,
            "engines": [r.get("engine", "Unknown") for r in results],
            "query": query,
            "answers": [],
            "results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 收集所有直接答案
        for result in results:
            if result.get("answer"):
                merged["answers"].append({
                    "engine": result.get("engine", "Unknown"),
                    "answer": result["answer"]
                })
        
        # 合并所有搜索结果，去重
        seen_urls = set()
        for result in results:
            engine = result.get("engine", "Unknown")
            for item in result.get("results", []):
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    # 添加来源引擎标记
                    item_with_source = item.copy()
                    item_with_source["source_engine"] = engine
                    merged["results"].append(item_with_source)
        
        # 按分数或位置排序（如果有的话）
        merged["results"].sort(
            key=lambda x: x.get("score", x.get("position", 999)),
            reverse=True
        )
        
        return merged
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        parallel: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: 搜索深度
            parallel: 是否并行搜索（True=并行，False=顺序）
            **kwargs: 其他参数
        
        Returns:
            搜索结果字典
        """
        if parallel:
            return await self.search_parallel(query, max_results, search_depth, **kwargs)
        else:
            return await self._search_sequential(query, max_results, search_depth, **kwargs)
    
    async def _search_sequential(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        **kwargs
    ) -> Dict[str, Any]:
        """
        顺序执行搜索（原有逻辑）
        """
        errors = []
        
        for engine_name, engine, api_key in self._get_engines():
            if not api_key or api_key == f"your_{engine_name.lower()}_api_key_here":
                continue
            
            try:
                print(f"  → 尝试使用 {engine_name} 搜索...")
                
                if engine_name == "Tavily":
                    result = await engine.search(
                        query=query,
                        max_results=max_results,
                        search_depth=search_depth,
                        **kwargs
                    )
                elif engine_name == "Serper":
                    result = await engine.search(
                        query=query,
                        max_results=max_results
                    )
                else:  # Qianfan
                    result = await engine.search(
                        query=query,
                        max_results=max_results
                    )
                
                print(f"  ✓ {engine_name} 搜索成功")
                return result
            
            except Exception as e:
                error_msg = f"{engine_name} failed: {str(e)}"
                errors.append(error_msg)
                print(f"  ✗ {error_msg}")
                continue
        
        # 如果所有引擎都失败，返回模拟数据
        print("  ⚠ 所有搜索引擎不可用，返回模拟数据")
        return await self._mock_search(query, max_results)
    
    async def _mock_search(self, query: str, max_results: int) -> Dict[str, Any]:
        """模拟搜索结果（用于开发测试）"""
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "engine": "Mock",
            "query": query,
            "answer": f"这是关于 '{query}' 的模拟搜索结果。实际使用时请配置搜索引擎 API Key。",
            "results": [
                {
                    "title": f"搜索结果 {i+1}: {query}",
                    "url": f"https://example.com/result-{i+1}",
                    "content": f"这是关于 '{query}' 的第 {i+1} 个搜索结果的摘要内容。包含了相关的信息和数据。",
                    "score": 0.9 - i * 0.1
                }
                for i in range(max_results)
            ],
            "timestamp": datetime.now().isoformat(),
            "note": "这是模拟数据，请配置真实的搜索引擎 API Key"
        }


# 导出统一搜索工具实例
unified_search = UnifiedSearchTool()
