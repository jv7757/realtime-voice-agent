"""
工具函数模块 - 提供 bash 命令执行和文件操作功能
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any

try:
    from agents import function_tool
except ImportError:
    print("错误: 未找到 openai-agents 库")
    print("请运行: pip install 'openai-agents[voice]'")
    import sys
    sys.exit(1)


@function_tool
def execute_bash_command(command: str) -> str:
    """
    执行 bash 命令并返回结果。命令的完整输出会在终端显示。

    Args:
        command: 要执行的 bash 命令

    Returns:
        执行结果的摘要，包括成功状态和关键信息
    """
    try:
        # 使用 subprocess 执行命令
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
            cwd=os.getcwd()
        )

        # 在终端显示命令执行结果
        print(f"\n{'='*60}")
        print(f"执行命令: {command}")
        print(f"{'='*60}")
        if result.stdout:
            print(f"输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误:\n{result.stderr}")
        print(f"返回码: {result.returncode}")
        print(f"{'='*60}\n")

        # 返回简洁的文本摘要
        if result.returncode == 0:
            output_preview = result.stdout.strip()[:200] if result.stdout else ""
            return f"命令执行成功。返回码: 0。输出: {output_preview}{'...' if len(result.stdout or '') > 200 else ''}"
        else:
            error_preview = result.stderr.strip()[:200] if result.stderr else ""
            return f"命令执行失败。返回码: {result.returncode}。错误: {error_preview}{'...' if len(result.stderr or '') > 200 else ''}"

    except subprocess.TimeoutExpired:
        error_msg = f"命令执行超时（超过30秒）: {command}"
        print(f"\n错误: {error_msg}\n")
        return error_msg
    except Exception as e:
        error_msg = f"命令执行失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return error_msg


@function_tool
def read_file(file_path: str, max_lines: int = 1000) -> str:
    """
    读取文件内容。适用于需要查看文件内容的场景。

    Args:
        file_path: 文件路径
        max_lines: 最大读取行数（默认1000行）

    Returns:
        文件内容或错误信息
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            error_msg = f"文件不存在: {file_path}"
            print(f"\n错误: {error_msg}\n")
            return error_msg

        if not path.is_file():
            error_msg = f"路径不是文件: {file_path}"
            print(f"\n错误: {error_msg}\n")
            return error_msg

        # 读取文件内容
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

            # 限制读取行数
            if len(lines) > max_lines:
                content = ''.join(lines[:max_lines])
                truncated = True
                total_lines = len(lines)
            else:
                content = ''.join(lines)
                truncated = False
                total_lines = len(lines)

        # 在终端显示读取信息
        print(f"\n{'='*60}")
        print(f"读取文件: {file_path}")
        print(f"总行数: {total_lines}")
        if truncated:
            print(f"（已截断到前 {max_lines} 行）")
        print(f"文件内容:\n{content[:500]}...")  # 显示前500字符
        print(f"{'='*60}\n")

        # 返回文件内容和元信息
        result = f"成功读取文件 {file_path}，共 {total_lines} 行"
        if truncated:
            result += f"（已截断到前 {max_lines} 行）"
        result += f"。内容：\n\n{content}"
        return result

    except Exception as e:
        error_msg = f"读取文件失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return error_msg


@function_tool
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """
    写入内容到文件。可以创建新文件或覆盖/追加现有文件。

    Args:
        file_path: 文件路径
        content: 要写入的内容
        append: 是否追加模式（默认False，覆盖写入）

    Returns:
        操作结果的描述
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        mode = 'a' if append else 'w'
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)

        # 在终端显示写入信息
        print(f"\n{'='*60}")
        print(f"{'追加' if append else '写入'}文件: {file_path}")
        print(f"内容长度: {len(content)} 字符")
        print(f"内容预览: {content[:100]}...")
        print(f"{'='*60}\n")

        mode_str = "追加" if append else "写入"
        return f"成功{mode_str}文件 {file_path}，共写入 {len(content)} 字符（{len(content.encode('utf-8'))} 字节）"

    except Exception as e:
        error_msg = f"写入文件失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return error_msg


@function_tool
def list_directory(directory_path: str = ".") -> str:
    """
    列出目录内容，显示文件和子目录信息。

    Args:
        directory_path: 目录路径（默认为当前目录）

    Returns:
        目录内容的描述
    """
    try:
        path = Path(directory_path).expanduser().resolve()

        if not path.exists():
            error_msg = f"目录不存在: {directory_path}"
            print(f"\n错误: {error_msg}\n")
            return error_msg

        if not path.is_dir():
            error_msg = f"路径不是目录: {directory_path}"
            print(f"\n错误: {error_msg}\n")
            return error_msg

        # 获取目录内容
        files = []
        directories = []

        for item in sorted(path.iterdir()):
            if item.is_file():
                files.append({
                    "name": item.name,
                    "size": item.stat().st_size,
                    "path": str(item)
                })
            elif item.is_dir():
                directories.append({
                    "name": item.name,
                    "path": str(item)
                })

        # 在终端显示目录信息
        print(f"\n{'='*60}")
        print(f"目录内容: {directory_path}")
        print(f"文件数: {len(files)}, 目录数: {len(directories)}")

        print(f"\n子目录:")
        for d in directories[:10]:  # 显示前10个
            print(f"  📁 {d['name']}")
        if len(directories) > 10:
            print(f"  ... 还有 {len(directories) - 10} 个目录")

        print(f"\n文件:")
        for f in files[:10]:  # 显示前10个
            size_kb = f['size'] / 1024
            print(f"  📄 {f['name']} ({size_kb:.1f} KB)")
        if len(files) > 10:
            print(f"  ... 还有 {len(files) - 10} 个文件")

        print(f"{'='*60}\n")

        # 构建结果文本
        result = f"目录 {directory_path} 包含 {len(directories)} 个子目录和 {len(files)} 个文件。\n\n"

        if directories:
            result += "子目录:\n"
            for d in directories[:5]:
                result += f"  - {d['name']}/\n"
            if len(directories) > 5:
                result += f"  ... 还有 {len(directories) - 5} 个目录\n"

        if files:
            result += "\n文件:\n"
            for f in files[:5]:
                size_kb = f['size'] / 1024
                result += f"  - {f['name']} ({size_kb:.1f} KB)\n"
            if len(files) > 5:
                result += f"  ... 还有 {len(files) - 5} 个文件\n"

        return result

    except Exception as e:
        error_msg = f"列出目录失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return error_msg
