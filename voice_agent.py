#!/usr/bin/env python3
"""
实时语音 Bash 智能体
基于 OpenAI Agents Python SDK 实现的实时语音助手，支持执行 bash 命令和文件操作
"""

import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

try:
    from agents.realtime import RealtimeAgent, RealtimeRunner
except ImportError:
    print("错误: 未找到 openai-agents 库")
    print("请运行: pip install 'openai-agents[voice]'")
    sys.exit(1)

from tools import (
    execute_bash_command,
    read_file,
    write_file,
    list_directory
)


# 加载环境变量
load_dotenv()


def create_bash_agent() -> RealtimeAgent:
    """
    创建实时语音 bash 智能体

    Returns:
        配置好的 RealtimeAgent 实例
    """
    # Agent 指令
    instructions = """你是一个实时语音 Bash 智能体助手。

你的能力包括：
1. 执行 bash 命令（execute_bash_command）
2. 读取文件内容（read_file）
3. 写入文件内容（write_file）
4. 列出目录内容（list_directory）

工作原则：
- 当用户要求执行命令时，使用 execute_bash_command 工具
- 命令执行结果会在终端显示，你需要用语音总结重点信息
- 对于复杂的输出，只语音回复最关键的信息，不要逐字朗读所有内容
- 确保在执行潜在危险的命令前，向用户确认
- 保持语音回复简洁明了，避免冗长
- 当用户说"你好"或"开始"时，友好地介绍你的功能

示例对话：
用户: "列出当前目录的文件"
你: [使用 list_directory 工具] "当前目录有3个文件和2个目录，主要文件包括..."

用户: "读取 config.txt 文件"
你: [使用 read_file 工具] "已读取 config.txt，文件包含配置信息..."

用户: "执行 ls -la 命令"
你: [使用 execute_bash_command 工具] "命令执行成功，找到了5个文件，详细信息已在终端显示"
"""

    # 创建工具定义
    tools = [
        {
            "type": "function",
            "name": "execute_bash_command",
            "description": "执行 bash 命令。命令的完整输出会在终端显示，你只需要语音总结关键信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的 bash 命令，例如: 'ls -la', 'pwd', 'cat file.txt'"
                    }
                },
                "required": ["command"]
            },
            "function": execute_bash_command
        },
        {
            "type": "function",
            "name": "read_file",
            "description": "读取文件内容。适用于需要查看文件内容的场景。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径"
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "最大读取行数（可选，默认1000）",
                        "default": 1000
                    }
                },
                "required": ["file_path"]
            },
            "function": read_file
        },
        {
            "type": "function",
            "name": "write_file",
            "description": "写入内容到文件。可以创建新文件或覆盖/追加现有文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要写入的文件路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的内容"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "是否追加模式（true=追加，false=覆盖，默认false）",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            },
            "function": write_file
        },
        {
            "type": "function",
            "name": "list_directory",
            "description": "列出目录内容，显示文件和子目录信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "目录路径（可选，默认当前目录）",
                        "default": "."
                    }
                },
                "required": []
            },
            "function": list_directory
        }
    ]

    # 创建 RealtimeAgent
    agent = RealtimeAgent(
        name="Bash Assistant",
        instructions=instructions,
        tools=tools
    )

    return agent


async def run_voice_agent():
    """
    运行实时语音 bash 智能体
    """
    # 检查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("错误: 未设置 OPENAI_API_KEY 环境变量")
        print("请在 .env 文件中设置或运行: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)

    print("=" * 80)
    print("实时语音 Bash 智能体")
    print("=" * 80)
    print("正在初始化语音助手...")
    print()

    # 创建智能体
    agent = create_bash_agent()

    # 配置 RealtimeRunner
    # 使用推荐的配置参数
    model_name = os.getenv("MODEL_NAME", "gpt-4o-realtime-preview")
    voice = os.getenv("VOICE", "alloy")

    config = {
        "model_settings": {
            "model_name": model_name,
            "voice": voice,
            "modalities": ["audio", "text"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        }
    }

    runner = RealtimeRunner(
        starting_agent=agent,
        config=config
    )

    print("语音助手已启动！")
    print()
    print("功能说明：")
    print("  - 执行 bash 命令")
    print("  - 读取/写入文件")
    print("  - 列出目录内容")
    print("  - 命令输出会在终端显示，AI 会语音总结重点信息")
    print()
    print("使用说明：")
    print("  - 直接用语音说出你的需求")
    print("  - 例如：'列出当前目录', '执行 ls 命令', '读取 README 文件'")
    print("  - 按 Ctrl+C 退出")
    print()
    print("=" * 80)
    print()

    try:
        # 启动会话
        session = await runner.run()

        async with session:
            print("🎤 会话已开始，请开始说话...")
            print()

            # 处理事件循环
            async for event in session:
                try:
                    # 根据事件类型处理
                    if event.type == "agent_start":
                        print(f"✓ 智能体启动: {event.agent.name}")

                    elif event.type == "agent_end":
                        print(f"✓ 智能体结束: {event.agent.name}")

                    elif event.type == "tool_start":
                        print(f"\n🔧 开始执行工具: {event.tool.name}")
                        # 如果有参数，显示参数信息
                        if hasattr(event, 'arguments'):
                            print(f"   参数: {event.arguments}")

                    elif event.type == "tool_end":
                        print(f"✓ 工具执行完成: {event.tool.name}")
                        # 输出已在工具函数中显示在终端

                    elif event.type == "response_audio_transcript":
                        # 显示 AI 的语音转录文本
                        if hasattr(event, 'transcript') and event.transcript:
                            print(f"\n🤖 AI 语音回复: {event.transcript}")

                    elif event.type == "input_audio_transcript":
                        # 显示用户的语音转录文本
                        if hasattr(event, 'transcript') and event.transcript:
                            print(f"\n👤 用户输入: {event.transcript}")

                    elif event.type == "error":
                        print(f"\n❌ 错误: {event.error}")
                        if "authentication" in str(event.error).lower():
                            print("   请检查您的 OPENAI_API_KEY 是否正确")
                            break

                    elif event.type == "interruption":
                        print("\n⚡ 检测到打断")

                except KeyboardInterrupt:
                    print("\n\n正在关闭会话...")
                    break
                except Exception as e:
                    print(f"\n处理事件时出错: {e}")
                    continue

    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
    except Exception as e:
        print(f"\n运行时错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n会话已结束")
        print("=" * 80)


def main():
    """
    主入口函数
    """
    try:
        asyncio.run(run_voice_agent())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
