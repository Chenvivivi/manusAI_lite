"""
Verify 智能体
负责校验和优化 Reasoner 生成的回答
"""

from typing import Dict, Any
from openai import OpenAI
from config import settings

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL
)


class Verifier:
    """Verify 智能体 - 校验和优化回答"""
    
    def __init__(self):
        self.model = "deepseek-chat"  # 使用 chat 模型进行校验
    
    def get_verify_prompt(self, user_query: str, tool_results: str, original_answer: str) -> str:
        """
        构建 Verify 提示词
        
        Args:
            user_query: 用户原始问题
            tool_results: 工具执行结果
            original_answer: Reasoner 生成的原始回答
        
        Returns:
            校验提示词
        """
        prompt = f"""你是一个专业的答案校验和优化助手（Verifier），负责对 AI 生成的回答进行质量检查和优化。

# 用户原始问题
{user_query}

# 工具执行结果（搜索引擎返回的真实数据）
{tool_results}

# AI 生成的原始回答
{original_answer}

# 你的任务
请仔细检查上述回答，并完成以下任务：

## 1. 事实准确性检查
- 检查回答中的事实是否与工具执行结果一致
- 标记任何与搜索结果不符的信息
- 确保没有编造或臆测的内容

## 2. 完整性检查
- 检查是否充分利用了所有搜索结果
- 确认是否遗漏了重要信息
- 验证是否完整回答了用户的问题

## 3. 逻辑性检查
- 检查论述是否有逻辑漏洞
- 确认结论是否有充分支撑
- 验证因果关系是否合理

## 4. 格式和可读性
- 检查 Markdown 格式是否正确
- 确保结构清晰、层次分明
- 优化表达，使其更易理解

## 5. 来源标注
- 如果回答中引用了具体信息，建议添加来源标注
- 提高回答的可信度

# 输出要求
请直接输出优化后的最终回答，要求：
1. 保持 Markdown 格式
2. 修正所有发现的问题
3. 如果原回答已经很好，可以保持不变或微调
4. 不要输出"检查报告"或"问题列表"，直接输出优化后的回答
5. 确保回答专业、准确、易懂

请开始校验和优化："""
        
        return prompt
    
    async def verify_and_optimize(
        self,
        user_query: str,
        tool_results: str,
        original_answer: str,
        reasoning: str = ""
    ) -> Dict[str, Any]:
        """
        校验和优化回答
        
        Args:
            user_query: 用户原始问题
            tool_results: 工具执行结果
            original_answer: Reasoner 生成的原始回答
            reasoning: Reasoner 的思维链（可选）
        
        Returns:
            校验结果字典
        """
        print(f"\n{'='*50}")
        print(f"【步骤 4】Verifier 校验和优化回答...")
        print(f"{'='*50}\n")
        print(f"  → 原始回答长度: {len(original_answer)} 字符")
        print(f"  → 工具结果长度: {len(tool_results)} 字符")
        
        try:
            verify_prompt = self.get_verify_prompt(user_query, tool_results, original_answer)
            
            print(f"  → 调用 DeepSeek API (model: {self.model}) 进行校验...")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": verify_prompt}
                ],
                max_tokens=8000,
                temperature=0.3  # 较低的温度，保持校验的严谨性
            )
            
            verified_answer = response.choices[0].message.content
            
            print(f"  ✓ Verifier 校验完成")
            print(f"  → 优化后回答长度: {len(verified_answer)} 字符")
            
            # 计算变化
            length_change = len(verified_answer) - len(original_answer)
            change_percent = (length_change / len(original_answer) * 100) if original_answer else 0
            
            print(f"  → 长度变化: {length_change:+d} 字符 ({change_percent:+.1f}%)")
            
            print(f"\n✓ Verifier 输出:")
            print(f"  - 校验状态: 完成")
            print(f"  - 原始长度: {len(original_answer)} 字符")
            print(f"  - 优化后长度: {len(verified_answer)} 字符")
            print(f"  - 变化幅度: {abs(change_percent):.1f}%")
            
            print(f"\n【Verifier 优化后的回答】")
            print(verified_answer)
            print(f"\n{'='*50}\n")
            
            return {
                "success": True,
                "original_answer": original_answer,
                "verified_answer": verified_answer,
                "original_length": len(original_answer),
                "verified_length": len(verified_answer),
                "length_change": length_change,
                "change_percent": change_percent,
                "reasoning": reasoning
            }
        
        except Exception as e:
            print(f"  ✗ Verifier 校验失败: {str(e)}")
            print(f"  → 返回原始回答")
            
            # 如果校验失败，返回原始回答
            return {
                "success": False,
                "error": str(e),
                "original_answer": original_answer,
                "verified_answer": original_answer,  # 失败时返回原始回答
                "original_length": len(original_answer),
                "verified_length": len(original_answer),
                "length_change": 0,
                "change_percent": 0,
                "reasoning": reasoning
            }


# 导出 Verifier 实例
verifier = Verifier()
