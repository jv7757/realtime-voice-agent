# 实时语音 Bash 智能体

基于 OpenAI Agents Python SDK 构建的实时语音 bash 智能体，支持通过语音交互执行 bash 命令、读写文件等操作。

## 功能特性

- 🎤 **实时语音交互**：使用 OpenAI Realtime API 实现低延迟语音对话
- 💻 **Bash 命令执行**：通过语音指令执行 bash 命令
- 📁 **文件操作**：支持读取、写入文件和列出目录内容
- 📺 **终端输出**：命令执行结果在终端显示，AI 语音总结重点信息
- 🔊 **语音活动检测**：支持自然的对话打断和交互
- 🛡️ **安全机制**：命令执行超时保护（30秒）

## 工具函数

### 1. execute_bash_command
执行 bash 命令并返回结果

**参数**：
- `command` (string): 要执行的 bash 命令

**示例**：
- "执行 ls -la 命令"
- "运行 pwd 命令"
- "查看系统信息 uname -a"

### 2. read_file
读取文件内容

**参数**：
- `file_path` (string): 文件路径
- `max_lines` (integer, 可选): 最大读取行数（默认 1000）

**示例**：
- "读取 config.txt 文件"
- "查看 README.md 的内容"

### 3. write_file
写入内容到文件

**参数**：
- `file_path` (string): 文件路径
- `content` (string): 要写入的内容
- `append` (boolean, 可选): 是否追加模式（默认 false）

**示例**：
- "创建一个新文件 test.txt，内容是 Hello World"
- "在 log.txt 文件末尾追加一行日志"

### 4. list_directory
列出目录内容

**参数**：
- `directory_path` (string, 可选): 目录路径（默认当前目录）

**示例**：
- "列出当前目录的文件"
- "查看 /home/user 目录下有什么"

## 安装

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd realtime-voice-agent
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 OpenAI API Key：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

可选配置：

```env
# 模型名称（默认: gpt-4o-realtime-preview）
MODEL_NAME=gpt-4o-realtime-preview

# 语音类型（可选: alloy, echo, fable, onyx, nova, shimmer）
VOICE=alloy
```

## 使用方法

### 启动智能体

```bash
python voice_agent.py
```

### 语音交互示例

启动后，直接用语音说出你的需求：

**基础命令**：
- "你好" / "开始" - AI 会介绍自己的功能
- "列出当前目录" - 列出当前目录的文件
- "执行 ls -la 命令" - 执行 ls 命令并显示详细信息
- "运行 pwd 命令" - 显示当前工作目录

**文件操作**：
- "读取 README.md 文件" - 读取并总结文件内容
- "创建一个文件 test.txt，内容是 Hello World" - 创建新文件
- "在 log.txt 末尾追加一行：任务完成" - 追加内容到文件

**目录操作**：
- "查看当前目录下有什么文件" - 列出目录内容
- "列出 /tmp 目录" - 查看指定目录

**退出**：
- 按 `Ctrl+C` 退出程序

## 系统要求

- Python 3.8+
- 麦克风和扬声器（用于语音交互）
- OpenAI API Key（需要访问 Realtime API）
- Linux/Mac/Windows（已测试）

## 依赖库

- `openai-agents[voice]` - OpenAI Agents SDK with voice support
- `sounddevice` - 音频输入输出
- `numpy` - 数值计算
- `python-dotenv` - 环境变量管理

## 项目结构

```
realtime-voice-agent/
├── voice_agent.py      # 主程序 - 实时语音智能体
├── tools.py            # 工具函数 - bash 命令、文件操作
├── requirements.txt    # 项目依赖
├── .env.example        # 环境变量示例
├── .gitignore         # Git 忽略文件
└── README.md          # 项目文档
```

## 工作原理

1. **语音输入**：用户通过麦克风说话，使用 `record_audio()` 录制音频
2. **语音识别**：使用 `gpt-4o-mini-transcribe` 模型将语音转为文字
3. **意图理解**：Agent 理解用户意图，决定是否需要调用工具函数
4. **工具执行**：如果需要，Agent 调用相应的工具函数（bash 命令、文件操作等）
   - 工具函数使用 `@function_tool` 装饰器定义
   - SDK 自动从函数签名和文档字符串提取工具信息
5. **结果显示**：
   - 命令执行的完整输出在终端显示
   - AI 语音总结重点信息，避免冗长朗读
6. **文本转语音**：使用 `gpt-4o-mini-tts` 模型生成语音回复
7. **语音播放**：通过 `AudioPlayer` 播放 AI 的语音回复

### 技术架构

- **VoicePipeline**：管理完整的语音交互流程（STT -> Agent -> TTS）
- **SingleAgentVoiceWorkflow**：将单个 Agent 封装为语音工作流
- **Agent**：处理用户请求和工具调用的核心逻辑
- **@function_tool**：装饰器，自动将 Python 函数转换为 Agent 可用的工具

## 安全注意事项

- ⚠️ **命令执行风险**：智能体可以执行任意 bash 命令，请谨慎使用
- 🔒 **超时保护**：命令执行设有 30 秒超时限制
- 🛡️ **确认机制**：AI 会在执行潜在危险命令前向用户确认
- 🔑 **API Key 安全**：不要将 `.env` 文件提交到版本控制系统

## 故障排除

### 1. 导入错误 "No module named 'agents'"

```bash
pip install 'openai-agents[voice]'
```

### 2. 音频设备错误

确保系统有可用的麦克风和扬声器，并检查权限设置。

### 3. API 认证错误

检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确设置。

### 4. 网络连接问题

Realtime API 需要稳定的网络连接，请检查网络状态。

## 参考资料

- [OpenAI Agents Python SDK 文档](https://openai.github.io/openai-agents-python/)
- [Voice Agents Quickstart](https://openai.github.io/openai-agents-python/voice/quickstart/)
- [OpenAI Agents GitHub 仓库](https://github.com/openai/openai-agents-python)
- [Tools 文档](https://openai.github.io/openai-agents-python/tools/)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

本项目基于 OpenAI Agents Python SDK 实现，参考了官方 voice quickstart 文档和示例代码。
