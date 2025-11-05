#!/usr/bin/env python3
"""
实时语音 Bash 智能体
基于 OpenAI Agents Python SDK 的语音管道实现，支持执行 bash 命令和文件操作
"""

import asyncio
import os
import sys
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

try:
    from agents import Agent
    from agents.voice import (
        AudioInput,
        VoicePipeline,
        SingleAgentVoiceWorkflow,
        VoicePipelineConfig,
        TTSModelSettings
    )
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


# 音频配置
SAMPLE_RATE = 24000  # 24kHz
CHANNELS = 1
DTYPE = np.int16


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

    # 创建 Agent
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


def record_audio_blocking(duration: int = 5) -> np.ndarray:
    """
    录制音频（阻塞式）

    Args:
        duration: 录音时长（秒）

    Returns:
        音频数据数组
    """
    print(f"🎤 开始录音（{duration} 秒）...")
    audio_data = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE
    )
    sd.wait()  # 等待录音完成
    print("✓ 录音完成")
    return audio_data.flatten()


def play_audio(audio_data: np.ndarray):
    """
    播放音频

    Args:
        audio_data: 音频数据数组
    """
    if len(audio_data) == 0:
        return

    print("🔊 播放回复...")
    sd.play(audio_data, samplerate=SAMPLE_RATE)
    sd.wait()  # 等待播放完成
    print("✓ 播放完成")


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

    # 创建 TTS 设置
    tts_settings = TTSModelSettings(
        voice=voice,
        instructions="保持语音回复简洁明了，避免冗长。"
    )

    # 创建配置
    config = VoicePipelineConfig(
        tts_settings=tts_settings
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
    print("  - 每轮对话会录音 5 秒")
    print("  - 例如：'列出当前目录', '执行 ls 命令', '读取 README 文件'")
    print("  - 按 Ctrl+C 退出")
    print()
    print("=" * 80)
    print()

    try:
        print("🎤 会话已开始！")
        print()

        # 主循环：录音 -> 处理 -> 播放回复
        round_num = 1
        while True:
            try:
                print(f"\n【第 {round_num} 轮对话】")
                print("-" * 80)

                # 录音
                audio_buffer = record_audio_blocking(duration=5)

                # 检查音频是否为空
                if np.max(np.abs(audio_buffer)) < 100:  # 音量太小
                    print("⚠️  未检测到明显的音频输入，请重试")
                    continue

                print(f"🔄 正在处理...")

                # 创建 AudioInput
                audio_input = AudioInput(
                    buffer=audio_buffer,  # 参数名是 buffer 而不是 audio
                    sample_rate=SAMPLE_RATE
                )

                # 处理音频并获取响应
                response_audio = []
                response_text = []

                async for event in pipeline.run(audio_input):
                    # 处理不同类型的事件
                    if event.type == "agent_start":
                        print(f"\n✓ 智能体启动: {event.agent.name}")

                    elif event.type == "agent_end":
                        print(f"✓ 智能体结束")

                    elif event.type == "tool_start":
                        print(f"\n🔧 开始执行工具: {event.tool.name}")

                    elif event.type == "tool_end":
                        print(f"✓ 工具执行完成: {event.tool.name}")

                    elif event.type == "text_delta":
                        # AI 的文本回复（流式）
                        if hasattr(event, 'delta') and event.delta:
                            response_text.append(event.delta)
                            print(event.delta, end='', flush=True)

                    elif event.type == "text_done":
                        print()  # 换行

                    elif event.type == "audio_delta":
                        # 收集音频数据
                        if hasattr(event, 'audio') and event.audio is not None:
                            response_audio.append(event.audio)

                    elif event.type == "error":
                        print(f"\n❌ 错误: {event.error}")
                        if "authentication" in str(event.error).lower():
                            print("   请检查您的 OPENAI_API_KEY 是否正确")
                            return

                # 如果有文本回复，显示完整文本
                if response_text:
                    full_text = ''.join(response_text)
                    print(f"\n🤖 AI 回复: {full_text}")

                # 播放音频回复
                if response_audio:
                    # 合并所有音频片段
                    full_audio = np.concatenate(response_audio)
                    play_audio(full_audio)
                else:
                    print("⚠️  未收到音频回复")

                print("\n" + "-" * 80)
                round_num += 1

            except KeyboardInterrupt:
                print("\n\n正在关闭会话...")
                break
            except Exception as e:
                print(f"\n处理时出错: {e}")
                import traceback
                traceback.print_exc()
                print("\n继续下一轮...")
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
