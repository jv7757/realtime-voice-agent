#!/usr/bin/env python3
"""
实时语音 Bash 智能体
基于 OpenAI Agents Python SDK 的语音管道实现，支持执行 bash 命令和文件操作
"""

import asyncio
import os
import sys
import numpy as np
from dotenv import load_dotenv

try:
    from agents import Agent
    from agents.voice import VoicePipeline, SingleAgentVoiceWorkflow, VoicePipelineConfig
    from agents.extensions.audio_player import AudioPlayer
    from agents.extensions.audio_input import AudioInput, record_audio
except ImportError as e:
    print(f"错误: 未找到 openai-agents 库或其依赖: {e}")
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


def create_bash_agent() -> Agent:
    """
    创建实时语音 bash 智能体

    Returns:
        配置好的 Agent 实例
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

    # 创建 Agent（使用 Agent 而不是 RealtimeAgent）
    agent = Agent(
        name="Bash Assistant",
        instructions=instructions,
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        tools=[
            execute_bash_command,
            read_file,
            write_file,
            list_directory
        ]
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

    # 配置语音管道
    voice = os.getenv("VOICE", "alloy")

    config = VoicePipelineConfig(
        tts_voice=voice
    )

    # 创建 VoicePipeline
    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(agent),
        stt_model="gpt-4o-mini-transcribe",
        tts_model="gpt-4o-mini-tts",
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

    # 创建音频播放器
    audio_player = AudioPlayer()

    try:
        print("🎤 会话已开始，请开始说话...")
        print()

        # 主循环：录音 -> 处理 -> 播放回复
        while True:
            try:
                # 录音
                print("🎤 正在录音... (说完话后会自动检测并处理)")
                audio_input = await record_audio()

                if audio_input is None or len(audio_input.audio) == 0:
                    print("⚠️  未检测到音频输入，请重试")
                    continue

                print(f"✓ 录音完成，时长: {len(audio_input.audio) / audio_input.sample_rate:.1f} 秒")
                print("🔄 正在处理...")

                # 处理音频并获取响应
                async for event in pipeline.run(audio_input):
                    # 处理不同类型的事件
                    if event.type == "agent_start":
                        print(f"\n✓ 智能体启动: {event.agent.name}")

                    elif event.type == "agent_end":
                        print(f"✓ 智能体结束: {event.agent.name}")

                    elif event.type == "tool_start":
                        print(f"\n🔧 开始执行工具: {event.tool.name}")
                        if hasattr(event, 'arguments'):
                            # 显示工具参数（简化显示）
                            args_str = str(event.arguments)[:100]
                            print(f"   参数: {args_str}...")

                    elif event.type == "tool_end":
                        print(f"✓ 工具执行完成: {event.tool.name}")

                    elif event.type == "text_delta":
                        # AI 的文本回复（流式）
                        if hasattr(event, 'delta') and event.delta:
                            print(event.delta, end='', flush=True)

                    elif event.type == "text_done":
                        print()  # 换行

                    elif event.type == "audio":
                        # 播放音频响应
                        if hasattr(event, 'audio') and event.audio is not None:
                            audio_player.play(event.audio)

                    elif event.type == "error":
                        print(f"\n❌ 错误: {event.error}")
                        if "authentication" in str(event.error).lower():
                            print("   请检查您的 OPENAI_API_KEY 是否正确")
                            return

                # 等待音频播放完成
                await audio_player.wait()
                print("\n" + "-" * 80 + "\n")

            except KeyboardInterrupt:
                print("\n\n正在关闭会话...")
                break
            except Exception as e:
                print(f"\n处理时出错: {e}")
                import traceback
                traceback.print_exc()
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
