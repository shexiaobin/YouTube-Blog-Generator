# YouTube Blog Generator - Technical Documentation / 技术文档

## 📋 Overview / 项目概述

**YouTube Blog Generator** is a Flask Web Application that can:
**YouTube Blog Generator** 是一个 Flask Web 应用，能够：

1. Fetch YouTube video info and subtitles / 获取 YouTube 视频信息和字幕
2. Generate blog summaries using AI (OpenAI/Gemini/Custom) or local methods / 使用 AI（OpenAI/Gemini/Custom）或本地方式生成博客摘要
3. Convert blogs to speech using TTS (Edge TTS or OpenAI TTS) / 使用 TTS（Edge TTS 或 OpenAI TTS）将博客转换为语音

---

## 🏗️ Architecture / 项目架构

```
youtube-blog-generator/
├── app.py              # Flask Main App (Routes & API) / Flask 主应用（路由和 API）
├── config.py           # Configuration Management / 配置管理
├── youtube_fetcher.py  # YouTube Video Fetcher / YouTube 视频抓取模块
├── summarizer.py       # AI Summarizer / AI 摘要生成模块
├── tts_engine.py       # TTS Engine (Text-to-Speech) / 文字转语音模块
├── templates/
│   └── index.html      # Frontend HTML Template / 前端 HTML 模板
├── static/
│   ├── app.js          # Frontend Logic (JS) / 前端 JavaScript 逻辑
│   └── style.css       # Stylesheet / 样式表
├── output/
│   ├── blogs/          # Generated Markdown Blogs / 生成的 Markdown 博客文件
│   ├── audio/          # Generated MP3 Audio / 生成的 MP3 音频文件
│   └── blogs.json      # Blog Metadata DB / 博客元数据数据库
├── requirements.txt    # Python Dependencies / Python 依赖
├── Dockerfile          # Docker Configuration / Docker 配置
└── .env.example        # Env Example / 环境变量示例
```

---

## 🔄 Data Flow / 数据流程

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌─────────────┐
│  User Input │───▶│  youtube_fetcher │───▶│  summarizer │───▶│  tts_engine │
│  Video URL  │    │  Fetch Video +   │    │  Generate   │    │  Generate   │
│  视频链接   │    │  Subtitles       │    │  Blog       │    │  Audio      │
└─────────────┘    └──────────────────┘    └─────────────┘    └─────────────┘
                                                                      │
                                                                      ▼
                                                            ┌─────────────────┐
                                                            │  Return Blog +  │
                                                            │  Audio          │
                                                            │  Save to output/│
                                                            └─────────────────┘
```

---

## 📁 Core Modules / 核心模块详解

### 1. `config.py` - Configuration / 配置管理

Loads environment variables and manages global configuration.
负责加载环境变量和管理全局配置。

| Config / 配置项 | Description / 说明 | Default / 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key / 密钥 | None (from .env) |
| `CUSTOM_API_KEY` | Custom API Key / 自定义密钥 | None |
| `TTS_ENGINE` | TTS Engine / 引擎选择 | `"edge"` |
| `TTS_VOICE` | Edge TTS Voice / 声音 | `"zh-CN-XiaoxiaoNeural"` |
| `SUMMARIZER` | Summary Engine / 摘要引擎 | `"custom"` >> `"openai"` >> `"local"` |

**Key Functions / 关键函数：**
- `has_custom_api()` - Check if Custom API is configured / 检查是否配置了 Custom API
- `has_openai()` - Check if OpenAI is configured / 检查是否配置了 OpenAI

---

### 2. `youtube_fetcher.py` - Video Fetching / 视频抓取

Uses `yt-dlp` library to fetch video info and subtitles.
使用 `yt-dlp` 库获取视频信息和字幕。

#### Main Functions / 主要函数

| Function / 函数 | Purpose / 用途 | Returns / 返回值 |
|------|------|--------|
| `get_channel_videos(url, count)` | Fetch latest videos from channel / 获取频道最新视频列表 | `List[Dict]` Video List |
| `get_video_info(url)` | Get detailed video info / 获取单个视频详细信息 | `Dict` (Title, Desc, Thumbnail...) |
| `get_video_transcript(url, language)` | Extract subtitles / 提取视频字幕 | `str` or `None` |

#### Subtitle Priority / 字幕获取优先级
1. Manual subtitles / 手动上传的字幕 (`subtitles`)
2. Auto-generated captions / 自动生成字幕 (`automatic_captions`)
3. Video description (fallback) / 若无字幕，返回视频描述作为备选

#### Supported Formats / 支持格式
- VTT (WebVTT)
- JSON3
- SRV3

---

### 3. `summarizer.py` - AI Summarization / AI 摘要生成

Converts video transcripts into structured blog posts.
将视频字幕转换为结构化博客文章。

#### Main Functions / 主要函数

| Function / 函数 | Purpose / 用途 |
|------|------|
| `generate_blog(title, transcript, channel)` | Main entry, auto-selects best method / 主入口，自动选择最佳方式 |
| `summarize_with_custom_api(...)` | Use Custom API (Gemini 3 Pro etc) / 使用自定义 API 生成 |
| `summarize_with_openai(...)` | Use OpenAI GPT-4o-mini / 使用 OpenAI 生成 |
| `summarize_simple(...)` | Simple formatting (fallback) / 无 API 时的简单格式化 |

#### AI Blog Structure / AI 生成的博客结构
```markdown
# [Catchy Title / 吸引人的标题]
## Overview / 概述
## Key Points / 主要观点
### 1. [Point 1]
### 2. [Point 2]
### 3. [Point 3]
## Memorable Quotes / 精彩语录
## Summary / 总结
```

---

### 4. `tts_engine.py` - Text-to-Speech / 文字转语音

Supports two TTS engines:
支持两种 TTS 引擎：

| Engine / 引擎 | Features / 特点 | Dependencies / 依赖 |
|------|------|------|
| **Edge TTS** | Free, Microsoft / 免费，微软语音 | `edge-tts` |
| **OpenAI TTS** | Paid, High Quality / 付费，高质量 | `openai` |

#### Main Functions / 主要函数

| Function / 函数 | Purpose / 用途 |
|------|------|
| `generate_audio(text, output_path, engine)` | Main entry, generates audio file / 主入口，生成音频文件 |
| `clean_text_for_tts(text)` | Clean Markdown for reading / 清理 Markdown 格式，适合朗读 |
| `get_available_voices()` | List available voices / 返回可用的声音列表 |

#### Edge TTS Voices / 可用声音
- `zh-CN-XiaoxiaoNeural` - Xiaoxiao (Female) / 晓晓（女声）
- `zh-CN-YunxiNeural` - Yunxi (Male) / 云希（男声）
- `en-US-JennyNeural` - Jenny (English Female) / Jenny（英文女声）
- More...

---

### 5. `app.py` - Flask Main App / Flask 主应用

Web Server and API Routes.
Web 服务器和 API 路由。

#### API Endpoints / API 端点

| Endpoint / 端点 | Method / 方法 | Description / 功能 |
|------|------|------|
| `/` | GET | Homepage HTML / 返回主页 HTML |
| `/api/status` | GET | API Status / 返回 API 状态 |
| `/api/fetch-channel` | POST | Fetch Channel Videos / 获取频道视频列表 |
| `/api/video-info` | POST | Get Video Info / 获取单个视频信息 |
| `/api/process-video` | POST | **Core**: Generate Blog & Audio / **核心功能**：处理视频生成博客+音频 |
| `/api/blogs` | GET | List History / 列出所有历史博客 |
| `/api/blog/<id>` | GET/DELETE | Get/Delete Blog / 获取/删除指定博客 |
| `/api/audio/<id>` | GET | Stream Audio / 流式播放音频 |
| `/api/download/<id>/audio` | GET | Download Audio / 下载音频文件 |
| `/api/download/<id>/markdown` | GET | Download Markdown / 下载 Markdown 文件 |
| `/api/voices` | GET | List Voices / 获取可用 TTS 声音 |

#### Core Process (`/api/process-video`) / 核心处理流程
```python
1. get_video_info(url)       # Fetch Info / 获取视频信息
2. get_video_transcript(url) # Fetch Subtitles / 获取字幕
3. generate_blog(...)        # Generate Content / 生成博客内容
4. generate_audio(...)       # Generate Audio / 生成语音
5. Save to file & DB         # 保存到文件和数据库
```

---

### 6. Frontend / 前端 (index.html + app.js)

#### HTML Structure / HTML 结构
```
┌─────────────────────────────────────────────────┐
│                    Header                       │
│  Logo + API Status Indicator / 状态指示器       │
├──────────────────┬──────────────────────────────┤
│   Input Panel    │       Preview Panel          │
│   视频输入面板   │       博客预览面板           │
│  · Channel Tab   │  · Audio Player              │
│  · Video Tab     │  · Markdown Content          │
│  · Video List    │  · Download Buttons          │
├──────────────────┴──────────────────────────────┤
│                 History Panel                   │
│                 历史博客面板                    │
│  List all generated blogs / 显示所有已生成的博客│
└─────────────────────────────────────────────────┘
```

#### Key JS Functions / JavaScript 关键函数

| Function / 函数 | Purpose / 功能 |
|------|------|
| `processVideo(url)` | Call backend to process / 调用后端处理视频 |
| `displayBlog(blog)` | Show blog & audio player / 显示博客内容和音频播放器 |
| `renderMarkdown(text)` | Simple Markdown to HTML / 简单 Markdown 转 HTML |
| `refreshHistory()` | Refresh history list / 刷新历史博客列表 |

---

## 🚀 How to Run / 如何运行

### Install Dependencies / 安装依赖
```bash
pip3 install -r requirements.txt
```

### Configure Environment (Optional) / 配置环境变量（可选）
```bash
cp .env.example .env
# Edit .env to add API Keys / 编辑 .env 添加 API Key
```

### Start Server / 启动服务器
```bash
# Python
python3 app.py

# Docker
docker run -p 5001:5001 --env-file .env youtube-blog-gen
```

Visit / 访问 **http://localhost:5001**

---

## 📊 Feature Comparison / 模式对比

| Feature / 功能 | No API Key / 无 Key | With AI API Key / 有 Key |
|------|---------------|---------------|
| Video Fetching / 视频获取 | ✅ OK | ✅ OK |
| Subtitle Extraction / 字幕提取 | ✅ OK | ✅ OK |
| Blog Generation / 博客生成 | ⚠️ Simple Formatting / 简单格式化 | ✅ AI Summary / AI 智能摘要 |
| TTS / 语音合成 | ✅ Edge TTS (Free) | ✅ + OpenAI TTS (Paid) |

---

## 🔧 Extensions / 扩展建议

1. **Database** - Use SQLite/PostgreSQL instead of JSON / 使用数据库替代 JSON 文件
2. **Languages** - Support more subtitle languages / 支持更多语言
3. **Batch Processing** - Process multiple videos concurrently / 批量处理
4. **Scheduled Tasks** - Auto-fetch new videos / 定时自动抓取
5. **User System** - Login & Personal Library / 用户系统

---

## 📝 FAQ / 常见问题

### Q: Audio generation failed? / 音频无法生成？
**A:** Ensure `edge-tts` is installed / 确保安装了 `edge-tts` 包：`pip3 install edge-tts`

### Q: Failed to fetch subtitles? / 字幕获取失败？
**A:** Video might not have subtitles; description will be used as fallback / 该视频可能没有字幕，系统会使用视频描述作为替代

### Q: Blog content is too simple? / 博客内容很简单？
**A:** Configure `OPENAI_API_KEY` or `CUSTOM_API_KEY` for AI summarization / 配置 API Key 可获得 AI 智能摘要
