"""
Executor 智能体
负责执行 Planner 规划的子任务，调用相应的工具
"""

from typing import List, Dict, Any
from datetime import datetime
import json

class SubTask:
    """子任务数据结构"""
    def __init__(self, task_data: Dict[str, Any]):
        self.id = task_data.get('id')
        self.type = task_data.get('type')
        self.description = task_data.get('description')
        self.tool_name = task_data.get('tool_name')
        self.parameters = task_data.get('parameters', {})
        self.dependencies = task_data.get('dependencies', [])
        self.status = 'pending'
        self.result = None
        self.error = None

class Executor:
    """
    Executor 智能体
    分析子任务列表，调用相应的工具，管理执行状态
    """
    
    def __init__(self, tools_registry: Dict[str, Any]):
        """
        初始化 Executor
        
        Args:
            tools_registry: 工具注册表，key 为工具名称，value 为工具执行函数
        """
        self.tools_registry = tools_registry
        self.subtasks = []
        self.results = {}
    
    def load_plan(self, plan: Dict[str, Any]) -> List[SubTask]:
        """
        加载 Planner 的规划结果
        
        Args:
            plan: Planner 返回的规划 JSON
            
        Returns:
            子任务对象列表
        """
        subtasks_data = plan.get('subtasks', [])
        self.subtasks = [SubTask(task_data) for task_data in subtasks_data]
        return self.subtasks
    
    def analyze_task(self, subtask: SubTask) -> Dict[str, Any]:
        """
        分析单个子任务，确定需要调用的工具和参数
        
        Args:
            subtask: 子任务对象
            
        Returns:
            分析结果，包含工具名称和参数
        """
        analysis = {
            'task_id': subtask.id,
            'task_type': subtask.type,
            'description': subtask.description
        }
        
        if subtask.type == 'tool_call':
            analysis['tool_name'] = subtask.tool_name
            analysis['parameters'] = subtask.parameters
            analysis['action'] = 'call_tool'
            
            if subtask.tool_name not in self.tools_registry:
                analysis['error'] = f"工具 '{subtask.tool_name}' 未注册"
                analysis['action'] = 'error'
        
        elif subtask.type == 'synthesis':
            analysis['action'] = 'synthesize'
            analysis['dependencies'] = subtask.dependencies
            analysis['required_results'] = [
                self.results.get(dep_id) for dep_id in subtask.dependencies
            ]
        
        return analysis
    
    async def execute_task(self, subtask: SubTask, callback=None) -> Dict[str, Any]:
        """
        执行单个子任务
        
        Args:
            subtask: 子任务对象
            callback: 状态更新回调函数
            
        Returns:
            执行结果
        """
        print(f"\n执行子任务 {subtask.id}: {subtask.description}")
        
        subtask.status = 'running'
        if callback:
            await callback(subtask.id, 'running')
        
        try:
            analysis = self.analyze_task(subtask)
            
            print(f"  - 任务类型: {analysis['task_type']}")
            if analysis.get('tool_name'):
                print(f"  - 调用工具: {analysis['tool_name']}")
                print(f"  - 工具参数: {json.dumps(analysis['parameters'], ensure_ascii=False)}")
            
            if analysis['action'] == 'call_tool':
                tool_func = self.tools_registry.get(subtask.tool_name)
                if tool_func:
                    result = await tool_func(**subtask.parameters)
                    subtask.result = result
                    subtask.status = 'completed'
                    self.results[subtask.id] = result
                    
                    print(f"\n  ✓ 工具执行完成")
                    print(f"  【工具执行结果】")
                    
                    # 检查是否是并行搜索结果
                    if result.get('engines'):
                        # 并行搜索结果
                        engines = result.get('engines', [])
                        print(f"    - 搜索引擎: {', '.join(engines)} (并行)")
                        print(f"    - 查询: {result.get('query', 'N/A')}")
                        
                        # 显示每个引擎的直接答案
                        answers = result.get('answers', [])
                        if answers:
                            print(f"\n  【各引擎直接答案】")
                            for ans in answers:
                                print(f"    [{ans['engine']}] {ans['answer'][:200]}...")
                    else:
                        # 单引擎搜索结果
                        print(f"    - 引擎: {result.get('engine', 'N/A')}")
                        print(f"    - 查询: {result.get('query', 'N/A')}")
                        
                        if result.get('answer'):
                            print(f"    - 直接答案: {result['answer'][:200]}...")
                    
                    results_list = result.get('results', [])
                    print(f"    - 合并结果数量: {len(results_list)}")
                    
                    if results_list:
                        print(f"\n  【搜索结果详情】")
                        for idx, item in enumerate(results_list[:5], 1):
                            source = item.get('source_engine', '')
                            source_tag = f" [{source}]" if source else ""
                            print(f"    [{idx}]{source_tag} {item.get('title', 'N/A')}")
                            print(f"        URL: {item.get('url', 'N/A')}")
                            print(f"        摘要: {item.get('content', item.get('snippet', 'N/A'))[:150]}...")
                            if idx < len(results_list[:5]):
                                print()
                    
                    import sys
                    sys.stdout.flush()
                else:
                    raise Exception(f"工具 '{subtask.tool_name}' 未找到")
            
            elif analysis['action'] == 'synthesize':
                print(f"  - 综合分析任务，依赖: {analysis['dependencies']}")
                subtask.result = {
                    'type': 'synthesis',
                    'dependencies_results': analysis['required_results']
                }
                subtask.status = 'completed'
                self.results[subtask.id] = subtask.result
            
            elif analysis['action'] == 'error':
                raise Exception(analysis['error'])
            
            if callback:
                await callback(subtask.id, 'completed', subtask.result)
            
            print(f"  ✓ 子任务 {subtask.id} 完成")
            
            return {
                'task_id': subtask.id,
                'status': 'completed',
                'result': subtask.result
            }
        
        except Exception as e:
            subtask.status = 'failed'
            subtask.error = str(e)
            
            print(f"  ✗ 子任务 {subtask.id} 失败: {str(e)}")
            
            if callback:
                await callback(subtask.id, 'failed', str(e))
            
            return {
                'task_id': subtask.id,
                'status': 'failed',
                'error': str(e)
            }
    
    def check_dependencies(self, subtask: SubTask) -> bool:
        """
        检查子任务的依赖是否已完成
        
        Args:
            subtask: 子任务对象
            
        Returns:
            依赖是否满足
        """
        if not subtask.dependencies:
            return True
        
        for dep_id in subtask.dependencies:
            dep_task = next((t for t in self.subtasks if t.id == dep_id), None)
            if not dep_task or dep_task.status != 'completed':
                return False
        
        return True
    
    async def execute_all(self, callback=None) -> List[Dict[str, Any]]:
        """
        执行所有子任务（按依赖顺序）
        
        Args:
            callback: 状态更新回调函数
            
        Returns:
            所有任务的执行结果
        """
        results = []
        executed_ids = []
        
        print(f"\n开始执行 {len(self.subtasks)} 个子任务...")
        
        while len(executed_ids) < len(self.subtasks):
            executed_in_round = False
            
            for subtask in self.subtasks:
                if subtask.id in executed_ids:
                    continue
                
                if self.check_dependencies(subtask):
                    result = await self.execute_task(subtask, callback)
                    results.append(result)
                    executed_ids.append(subtask.id)
                    executed_in_round = True
            
            if not executed_in_round:
                print("\n警告: 存在循环依赖或无法满足的依赖")
                for subtask in self.subtasks:
                    if subtask.id not in executed_ids:
                        print(f"  - 未执行的任务 {subtask.id}: {subtask.description}")
                break
        
        print(f"\n所有子任务执行完成！")
        return results
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        获取执行状态摘要
        
        Returns:
            状态摘要
        """
        return {
            'total': len(self.subtasks),
            'completed': len([t for t in self.subtasks if t.status == 'completed']),
            'running': len([t for t in self.subtasks if t.status == 'running']),
            'failed': len([t for t in self.subtasks if t.status == 'failed']),
            'pending': len([t for t in self.subtasks if t.status == 'pending'])
        }
