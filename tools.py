"""
工具函数模块 - 提供 bash 命令执行和文件操作功能
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any


def execute_bash_command(command: str) -> Dict[str, Any]:
    """
    执行 bash 命令并返回结果

    Args:
        command: 要执行的 bash 命令

    Returns:
        包含执行结果的字典，包括 stdout, stderr, return_code
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

        output = {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "command": command
        }

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

        return output

    except subprocess.TimeoutExpired:
        error_msg = f"命令执行超时（超过30秒）: {command}"
        print(f"\n错误: {error_msg}\n")
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": error_msg,
            "command": command
        }
    except Exception as e:
        error_msg = f"命令执行失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": error_msg,
            "command": command
        }


def read_file(file_path: str, max_lines: int = 1000) -> Dict[str, Any]:
    """
    读取文件内容

    Args:
        file_path: 文件路径
        max_lines: 最大读取行数（默认1000行）

    Returns:
        包含文件内容的字典
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            error_msg = f"文件不存在: {file_path}"
            print(f"\n错误: {error_msg}\n")
            return {
                "success": False,
                "content": "",
                "error": error_msg,
                "file_path": file_path
            }

        if not path.is_file():
            error_msg = f"路径不是文件: {file_path}"
            print(f"\n错误: {error_msg}\n")
            return {
                "success": False,
                "content": "",
                "error": error_msg,
                "file_path": file_path
            }

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
        print(f"{'='*60}\n")

        return {
            "success": True,
            "content": content,
            "file_path": str(path),
            "total_lines": total_lines,
            "truncated": truncated
        }

    except Exception as e:
        error_msg = f"读取文件失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return {
            "success": False,
            "content": "",
            "error": error_msg,
            "file_path": file_path
        }


def write_file(file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
    """
    写入内容到文件

    Args:
        file_path: 文件路径
        content: 要写入的内容
        append: 是否追加模式（默认False，覆盖写入）

    Returns:
        包含操作结果的字典
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
        print(f"{'='*60}\n")

        return {
            "success": True,
            "file_path": str(path),
            "bytes_written": len(content.encode('utf-8')),
            "mode": "append" if append else "overwrite"
        }

    except Exception as e:
        error_msg = f"写入文件失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return {
            "success": False,
            "error": error_msg,
            "file_path": file_path
        }


def list_directory(directory_path: str = ".") -> Dict[str, Any]:
    """
    列出目录内容

    Args:
        directory_path: 目录路径（默认为当前目录）

    Returns:
        包含目录内容的字典
    """
    try:
        path = Path(directory_path).expanduser().resolve()

        if not path.exists():
            error_msg = f"目录不存在: {directory_path}"
            print(f"\n错误: {error_msg}\n")
            return {
                "success": False,
                "files": [],
                "directories": [],
                "error": error_msg,
                "directory_path": directory_path
            }

        if not path.is_dir():
            error_msg = f"路径不是目录: {directory_path}"
            print(f"\n错误: {error_msg}\n")
            return {
                "success": False,
                "files": [],
                "directories": [],
                "error": error_msg,
                "directory_path": directory_path
            }

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
        print(f"{'='*60}\n")

        return {
            "success": True,
            "directory_path": str(path),
            "files": files,
            "directories": directories,
            "total_items": len(files) + len(directories)
        }

    except Exception as e:
        error_msg = f"列出目录失败: {str(e)}"
        print(f"\n错误: {error_msg}\n")
        return {
            "success": False,
            "files": [],
            "directories": [],
            "error": error_msg,
            "directory_path": directory_path
        }
