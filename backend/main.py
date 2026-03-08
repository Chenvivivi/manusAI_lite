from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI
from config import settings
from prompts import get_planner_prompt
from tools import get_all_tools
from executor import Executor
from tool_implementations import TOOL_REGISTRY
from verify import verifier
import traceback
import json
import sys
import io
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = FastAPI(title="ManusAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_api_key_here":
    print("\n" + "!"*50)
    print("警告: 未配置 DEEPSEEK_API_KEY")
    print("请在 backend/.env 文件中设置你的 API Key")
    print("!"*50 + "\n")

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL
)

conversation_history = {}

class Message(BaseModel):
    text: str
    taskId: int

class MessageResponse(BaseModel):
    text: str
    time: str
    reasoning: str = ""
    files: list = []

@app.get("/")
async def root():
    return {
        "message": "ManusAI Backend API",
        "model": settings.DEEPSEEK_MODEL,
        "tools": len(get_all_tools())
    }

@app.get("/api/tools")
async def list_tools():
    """获取所有可用工具列表"""
    return {"tools": get_all_tools()}

def _generate_sources_file(subtasks, user_query):
    """生成来源文件内容"""
    print(f"\n  → 开始生成来源文件...")
    print(f"  → 子任务数量: {len(subtasks)}")
    sys.stdout.flush()
    
    content = f"""# 搜索来源汇总

**用户问题**: {user_query}

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
    
    has_search_results = False
    
    for idx, subtask in enumerate(subtasks, 1):
        print(f"  → 检查子任务 {idx}: type={subtask.type}, has_result={subtask.result is not None}")
        
        if subtask.type == 'tool_call' and subtask.result:
            print(f"    → 结果包含的键: {list(subtask.result.keys())}")
            
            if subtask.result.get('results'):
                has_search_results = True
                result = subtask.result
                content += f"## {subtask.description}\n\n"
                
                # 添加搜索结果（仅标题和链接）
                for idx, item in enumerate(result.get('results', []), 1):
                    source = item.get('source_engine', '')
                    source_tag = f" `[{source}]`" if source else ""
                    content += f"{idx}. **{item.get('title', 'N/A')}**{source_tag}\n"
                    content += f"   - [{item.get('url', 'N/A')}]({item.get('url', '#')})\n\n"
                
                content += "---\n\n"
                print(f"    ✓ 已添加子任务 {idx} 的搜索结果")
    
    sys.stdout.flush()
    
    if has_search_results:
        print(f"  ✓ 来源文件生成完成，总长度: {len(content)} 字符")
        return content
    else:
        print(f"  ⚠ 没有找到搜索结果，不生成来源文件")
        return None

@app.get("/api/test/stream")
async def test_stream():
    """测试流式输出是否正常工作"""
    async def generate():
        for i in range(5):
            yield f"data: {json.dumps({'type': 'test', 'message': f'测试消息 {i+1}'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/planner")
async def plan_tasks(message: Message):
    """
    Planner 智能体：将用户查询拆解为子任务
    """
    print("\n" + "="*50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Planner 收到查询:")
    print(f"任务ID: {message.taskId}")
    print(f"用户查询: {message.text}")
    print("-"*50)
    
    try:
        system_prompt, user_prompt = get_planner_prompt(message.text)
        
        print("调用 Planner 智能体...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=4000
        )
        
        plan_result = response.choices[0].message.content
        
        try:
            print(f"Planner 规划结果: {plan_result[:300]}..." if len(plan_result) > 300 else f"Planner 规划结果: {plan_result}")
        except UnicodeEncodeError:
            print(f"Planner 规划结果: [包含特殊字符，长度 {len(plan_result)}]")
        
        print("="*50 + "\n")
        
        plan_json = json.loads(plan_result)
        
        return {
            "success": True,
            "plan": plan_json,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Planner 错误: {str(e)}")
        print(traceback.format_exc())
        print("="*50 + "\n")
        
        raise HTTPException(
            status_code=500,
            detail=f"Planner 规划失败: {str(e)}"
        )

@app.post("/api/chat/stream")
async def chat_stream(message: Message):
    print("\n" + "="*50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 收到用户消息:")
    print(f"任务ID: {message.taskId}")
    print(f"消息内容: {message.text}")
    print("-"*50)
    
    async def generate():
        print("开始生成流式响应...")
        
        try:
            if message.taskId not in conversation_history:
                conversation_history[message.taskId] = []
            
            conversation_history[message.taskId].append({
                "role": "user",
                "content": message.text
            })
            
            print(f"\n【步骤 1】调用 Planner 规划子任务...")
            sys.stdout.flush()
            
            try:
                print("  → 准备 Planner 提示词...")
                sys.stdout.flush()
                
                system_prompt, user_prompt = get_planner_prompt(message.text)
                
                print(f"  → 调用 DeepSeek API (model: deepseek-chat)...")
                sys.stdout.flush()
                
                planner_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=4000,
                    timeout=30.0
                )
                
                print("  → 收到 Planner 响应，解析 JSON...")
                sys.stdout.flush()
                
                plan_result = planner_response.choices[0].message.content
                plan_json = json.loads(plan_result)
                
                print(f"\n✓ Planner 输出:")
                try:
                    print(json.dumps(plan_json, ensure_ascii=False, indent=2))
                except Exception as e:
                    print(f"[子任务数量: {len(plan_json.get('subtasks', []))}]")
                
                sys.stdout.flush()
                
                print(f"  → 发送 plan 事件到前端...")
                sys.stdout.flush()
                
                yield f"data: {json.dumps({'type': 'plan', 'content': plan_json}, ensure_ascii=False)}\n\n"
                
                print(f"  ✓ plan 事件已发送")
                sys.stdout.flush()
                
            except Exception as e:
                print(f"\n✗ Planner 失败: {str(e)}")
                print(traceback.format_exc())
                sys.stdout.flush()
                raise
            
            print(f"\n{'='*50}")
            print(f"【步骤 2】Executor 开始执行子任务...")
            print(f"{'='*50}")
            
            try:
                print("  → 初始化 Executor...")
                sys.stdout.flush()
                
                executor = Executor(TOOL_REGISTRY)
                executor.load_plan(plan_json)
                
                print(f"  → 已加载 {len(executor.subtasks)} 个子任务")
                sys.stdout.flush()
                
                for idx, subtask in enumerate(executor.subtasks, 1):
                    try:
                        print(f"\n  → 执行子任务 {idx}/{len(executor.subtasks)}: {subtask.description}")
                        sys.stdout.flush()
                        
                        await executor.execute_task(subtask, None)
                        
                        print(f"  ✓ 子任务 {subtask.id} 完成 (状态: {subtask.status})")
                        sys.stdout.flush()
                        
                        update_data = {
                            'type': 'task_update',
                            'task_id': subtask.id,
                            'status': subtask.status
                        }
                        yield f"data: {json.dumps(update_data, ensure_ascii=False)}\n\n"
                        
                    except Exception as task_error:
                        print(f"\n✗ 子任务 {subtask.id} 执行失败: {str(task_error)}")
                        print(traceback.format_exc())
                        sys.stdout.flush()
                        
                        subtask.status = 'failed'
                        
                        update_data = {
                            'type': 'task_update',
                            'task_id': subtask.id,
                            'status': 'failed'
                        }
                        yield f"data: {json.dumps(update_data, ensure_ascii=False)}\n\n"
                
                print(f"\n✓ Executor 输出:")
                print(f"  - 总任务数: {len(executor.subtasks)}")
                print(f"  - 已完成: {len([t for t in executor.subtasks if t.status == 'completed'])}")
                print(f"  - 失败: {len([t for t in executor.subtasks if t.status == 'failed'])}")
                sys.stdout.flush()
                
            except Exception as e:
                print(f"\n✗ Executor 执行失败: {str(e)}")
                print(traceback.format_exc())
                sys.stdout.flush()
                raise
            
            print(f"\n{'='*50}")
            print(f"【步骤 3】调用 DeepSeek Reasoner 生成最终回答...")
            print(f"{'='*50}\n")
            sys.stdout.flush()
            
            tool_results_content = []
            for subtask in executor.subtasks:
                if subtask.status == 'completed' and subtask.result:
                    result = subtask.result
                    
                    if subtask.type == 'tool_call' and result.get('results'):
                        tool_results_content.append(f"\n【子任务 {subtask.id}】{subtask.description}")
                        tool_results_content.append(f"工具: {subtask.tool_name}")
                        tool_results_content.append(f"查询: {result.get('query', 'N/A')}")
                        
                        # 检查是否是并行搜索结果
                        if result.get('engines'):
                            engines = result.get('engines', [])
                            tool_results_content.append(f"搜索引擎: {', '.join(engines)} (并行搜索)")
                            
                            # 添加各引擎的直接答案
                            answers = result.get('answers', [])
                            if answers:
                                tool_results_content.append(f"\n各引擎直接答案:")
                                for ans in answers:
                                    tool_results_content.append(f"\n[{ans['engine']}]")
                                    tool_results_content.append(ans['answer'])
                        else:
                            tool_results_content.append(f"搜索引擎: {result.get('engine', 'N/A')}")
                            
                            if result.get('answer'):
                                tool_results_content.append(f"\n直接答案:\n{result['answer']}")
                        
                        tool_results_content.append(f"\n合并搜索结果:")
                        for idx, item in enumerate(result.get('results', []), 1):
                            source = item.get('source_engine', '')
                            source_tag = f" [来源: {source}]" if source else ""
                            tool_results_content.append(f"\n[{idx}]{source_tag} {item.get('title', 'N/A')}")
                            tool_results_content.append(f"URL: {item.get('url', 'N/A')}")
                            content_text = item.get('content', item.get('snippet', 'N/A'))
                            tool_results_content.append(f"内容: {content_text}")
            
            tool_results_text = "\n".join(tool_results_content)
            
            context_message = f"""用户问题: {message.text}

【工具执行结果】
{tool_results_text}

请根据以上搜索结果，回答用户的问题。要求：
1. 综合所有搜索结果的信息
2. 提供准确、详细的回答
3. 如果有多个来源，请整合信息
4. 使用 Markdown 格式，结构清晰"""
            
            conversation_history[message.taskId].append({
                "role": "user",
                "content": context_message
            })
            
            # 打印传递给 Reasoner 的完整输入
            print(f"\n{'='*50}")
            print(f"【Reasoner 输入内容】")
            print(f"{'='*50}")
            print(f"\n用户原始问题: {message.text}")
            print(f"\n传递给模型的上下文消息:")
            print(f"{'-'*50}")
            print(context_message)
            print(f"{'-'*50}\n")
            
            print(f"  → 调用 DeepSeek API (model: {settings.DEEPSEEK_MODEL})...")
            print(f"  → 对话历史长度: {len(conversation_history[message.taskId])} 条消息")
            print(f"  → 已整合 {len(executor.subtasks)} 个子任务的执行结果")
            sys.stdout.flush()
            
            # 先完整获取 Reasoner 的响应（非流式）
            print(f"  → 调用 DeepSeek API (非流式模式)...")
            sys.stdout.flush()
            
            response = client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=conversation_history[message.taskId],
                max_tokens=8000,
                stream=False,
                timeout=60.0
            )
            
            full_reasoning = response.choices[0].message.reasoning_content or ""
            full_content = response.choices[0].message.content or ""
            
            print(f"  ✓ Reasoner 响应完成")
            print(f"  - 思维链长度: {len(full_reasoning)} 字符")
            print(f"  - 回复长度: {len(full_content)} 字符")
            
            if full_reasoning:
                print(f"\n【思维链内容】")
                print(full_reasoning)
                print(f"\n" + "-"*50)
            
            print(f"\n【Reasoner 原始回复内容】")
            print(full_content)
            
            sys.stdout.flush()
            print("\n" + "="*50 + "\n")
            
            # 调用 Verifier 校验和优化回答
            try:
                print(f"  → 开始调用 Verifier...")
                sys.stdout.flush()
                
                verify_result = await verifier.verify_and_optimize(
                    user_query=message.text,
                    tool_results=tool_results_text,
                    original_answer=full_content,
                    reasoning=full_reasoning
                )
                
                final_answer = verify_result['verified_answer']
                final_reasoning = full_reasoning
                
                print(f"  ✓ Verifier 完成")
                sys.stdout.flush()
                
            except Exception as verify_error:
                print(f"  ✗ Verifier 失败: {str(verify_error)}")
                print(traceback.format_exc())
                sys.stdout.flush()
                final_answer = full_content
                final_reasoning = full_reasoning
            
            # 生成来源文件
            try:
                sources_content = _generate_sources_file(executor.subtasks, message.text)
                if sources_content:
                    print(f"  ✓ 来源文件生成完成，长度: {len(sources_content)} 字符")
                sys.stdout.flush()
            except Exception as file_error:
                print(f"  ✗ 来源文件生成失败: {str(file_error)}")
                sys.stdout.flush()
                sources_content = None
            
            # 模拟流式输出思考过程
            print(f"  → 开始流式输出思考过程...")
            sys.stdout.flush()
            
            if final_reasoning:
                chunk_size = 50
                for i in range(0, len(final_reasoning), chunk_size):
                    chunk = final_reasoning[i:i+chunk_size]
                    yield f"data: {json.dumps({'type': 'reasoning', 'content': chunk}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)
            
            # 模拟流式输出最终答案
            print(f"  → 开始流式输出最终答案...")
            sys.stdout.flush()
            
            chunk_size = 30
            for i in range(0, len(final_answer), chunk_size):
                chunk = final_answer[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)
            
            # 发送来源文件信息
            if sources_content:
                file_info = {
                    'type': 'file',
                    'file': {
                        'name': f'来源_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
                        'content': sources_content,
                        'size': len(sources_content)
                    }
                }
                yield f"data: {json.dumps(file_info, ensure_ascii=False)}\n\n"
                print(f"  ✓ 来源文件已发送到前端")
                sys.stdout.flush()
            
            current_time = datetime.now().strftime("%H:%M")
            yield f"data: {json.dumps({'type': 'done', 'time': current_time}, ensure_ascii=False)}\n\n"
            
            print(f"  ✓ 所有数据已发送完成")
            sys.stdout.flush()
            
            conversation_history[message.taskId].append({
                "role": "assistant",
                "content": final_answer  # 保存优化后的回答
            })
            
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            print(f"\n✗ 错误: {error_msg}")
            print(traceback.format_exc())
            print("="*50 + "\n")
            
            error_data = {
                'type': 'error',
                'content': error_msg
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.delete("/api/chat/history/{task_id}")
async def clear_history(task_id: int):
    if task_id in conversation_history:
        del conversation_history[task_id]
        return {"message": f"任务 {task_id} 的对话历史已清除"}
    return {"message": "任务不存在"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
