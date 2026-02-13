# YouTube 博客生成器 - 技术文档

## 📋 项目概述

**YouTube Blog Generator** 是一个 Flask Web 应用，能够：
1. 获取 YouTube 视频信息和字幕
2. 使用 AI（OpenAI）或本地方式生成博客摘要
3. 使用 TTS（Edge TTS 或 OpenAI TTS）将博客转换为语音

---

## 🏗️ 项目架构

```
youtube-blog-generator/
├── app.py              # Flask 主应用（路由和 API）
├── config.py           # 配置管理
├── youtube_fetcher.py  # YouTube 视频抓取模块
├── summarizer.py       # AI 摘要生成模块
├── tts_engine.py       # 文字转语音模块
├── templates/
│   └── index.html      # 前端 HTML 模板
├── static/
│   ├── app.js          # 前端 JavaScript 逻辑
│   └── style.css       # 样式表
├── output/
│   ├── blogs/          # 生成的 Markdown 博客文件
│   ├── audio/          # 生成的 MP3 音频文件
│   └── blogs.json      # 博客元数据数据库
├── requirements.txt    # Python 依赖
└── .env.example        # 环境变量示例
```

---

## 🔄 数据流程

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌─────────────┐
│  用户输入   │───▶│  youtube_fetcher │───▶│  summarizer │───▶│  tts_engine │
│  视频链接   │    │  获取视频+字幕   │    │  生成博客   │    │  生成音频   │
└─────────────┘    └──────────────────┘    └─────────────┘    └─────────────┘
                                                                     │
                                                                     ▼
                                                           ┌─────────────────┐
                                                           │  返回博客+音频  │
                                                           │  保存到 output/ │
                                                           └─────────────────┘
```

---

## 📁 核心模块详解

### 1. config.py - 配置管理

负责加载环境变量和管理全局配置。

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 空（从 .env 读取）|
| `TTS_ENGINE` | TTS 引擎选择 | `"edge"` |
| `TTS_VOICE` | Edge TTS 声音 | `"zh-CN-XiaoxiaoNeural"` |
| `SUMMARIZER` | 摘要引擎 | 有 API 时用 `"openai"`，否则 `"local"` |

**关键函数：**
- `has_openai()` - 检查是否配置了 OpenAI API Key

---

### 2. youtube_fetcher.py - YouTube 视频抓取

使用 `yt-dlp` 库获取视频信息和字幕。

#### 主要函数

| 函数 | 用途 | 返回值 |
|------|------|--------|
| `get_channel_videos(url, count)` | 获取频道最新视频列表 | `List[Dict]` 视频列表 |
| `get_video_info(url)` | 获取单个视频详细信息 | `Dict` 包含标题、描述、缩略图等 |
| `get_video_transcript(url, language)` | 提取视频字幕 | `str` 或 `None` |

#### 字幕获取优先级
1. 手动上传的字幕（subtitles）
2. 自动生成字幕（automatic_captions）
3. 若无字幕，返回视频描述作为备选

#### 支持的字幕格式
- VTT (WebVTT)
- JSON3
- SRV3

---

### 3. summarizer.py - AI 摘要生成

将视频字幕转换为结构化博客文章。

#### 主要函数

| 函数 | 用途 |
|------|------|
| `generate_blog(title, transcript, channel)` | 主入口，自动选择最佳方式 |
| `summarize_with_openai(...)` | 使用 OpenAI GPT-4o-mini 生成 |
| `summarize_simple(...)` | 无 API 时的简单格式化 |

#### AI 生成的博客结构
```markdown
# [吸引人的标题]
## 概述
## 主要观点
### 1. [关键点1]
### 2. [关键点2]
### 3. [关键点3]
## 精彩语录
## 总结
```

---

### 4. tts_engine.py - 文字转语音

支持两种 TTS 引擎：

| 引擎 | 特点 | 依赖 |
|------|------|------|
| **Edge TTS** | 免费，微软语音 | `edge-tts` |
| **OpenAI TTS** | 付费，高质量 | `openai` |

#### 主要函数

| 函数 | 用途 |
|------|------|
| `generate_audio(text, output_path, engine)` | 主入口，生成音频文件 |
| `clean_text_for_tts(text)` | 清理 Markdown 格式，适合朗读 |
| `get_available_voices()` | 返回可用的声音列表 |

#### Edge TTS 可用声音
- `zh-CN-XiaoxiaoNeural` - 晓晓（女声）
- `zh-CN-YunxiNeural` - 云希（男声）
- `en-US-JennyNeural` - Jenny（英文女声）
- 更多...

---

### 5. app.py - Flask 主应用

Web 服务器和 API 路由。

#### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 返回主页 HTML |
| `/api/status` | GET | 返回 API 状态（是否配置 OpenAI 等）|
| `/api/fetch-channel` | POST | 获取频道视频列表 |
| `/api/video-info` | POST | 获取单个视频信息 |
| `/api/process-video` | POST | **核心功能**：处理视频生成博客+音频 |
| `/api/blogs` | GET | 列出所有历史博客 |
| `/api/blog/<id>` | GET/DELETE | 获取/删除指定博客 |
| `/api/audio/<id>` | GET | 流式播放音频 |
| `/api/download/<id>/audio` | GET | 下载音频文件 |
| `/api/download/<id>/markdown` | GET | 下载 Markdown 文件 |
| `/api/voices` | GET | 获取可用 TTS 声音 |

#### 核心处理流程 (`/api/process-video`)
```python
1. get_video_info(url)      # 获取视频信息
2. get_video_transcript(url) # 获取字幕
3. generate_blog(...)        # 生成博客内容
4. generate_audio(...)       # 生成语音
5. 保存到文件和数据库
```

---

### 6. 前端 (index.html + app.js)

#### HTML 结构
```
┌─────────────────────────────────────────────────┐
│                    Header                       │
│  Logo + API 状态指示器                          │
├──────────────────┬──────────────────────────────┤
│   视频输入面板   │       博客预览面板           │
│  · 频道视频 Tab  │  · 音频播放器                │
│  · 单个视频 Tab  │  · Markdown 渲染内容         │
│  · 视频列表      │  · 下载按钮                  │
├──────────────────┴──────────────────────────────┤
│                 历史博客面板                    │
│  显示所有已生成的博客，可查看/删除              │
└─────────────────────────────────────────────────┘
```

#### JavaScript 关键函数

| 函数 | 功能 |
|------|------|
| `processVideo(url)` | 调用后端处理视频 |
| `displayBlog(blog)` | 显示博客内容和音频播放器 |
| `renderMarkdown(text)` | 简单 Markdown 转 HTML |
| `refreshHistory()` | 刷新历史博客列表 |

---

## 🚀 如何运行

### 安装依赖
```bash
pip3 install flask flask-cors yt-dlp youtube-transcript-api openai gtts python-dotenv edge-tts
```

### 配置环境变量（可选）
```bash
cp .env.example .env
# 编辑 .env 添加 OPENAI_API_KEY
```

### 启动服务器
```bash
python3 app.py
```

访问 **http://localhost:5001**

---

## 📊 模式对比

| 功能 | 无 OpenAI API | 有 OpenAI API |
|------|---------------|---------------|
| 视频获取 | ✅ 正常 | ✅ 正常 |
| 字幕提取 | ✅ 正常 | ✅ 正常 |
| 博客生成 | ⚠️ 简单格式化 | ✅ AI 智能摘要 |
| 语音合成 | ✅ Edge TTS（免费）| ✅ 可选 OpenAI TTS |

---

## 🔧 扩展建议

1. **添加数据库** - 目前使用 JSON 文件，可改为 SQLite/PostgreSQL
2. **支持更多语言** - 扩展字幕语言优先级
3. **批量处理** - 支持同时处理多个视频
4. **定时任务** - 自动获取新视频并生成博客
5. **用户系统** - 添加登录和个人博客库

---

## 📝 常见问题

### Q: 音频无法生成？
**A:** 确保安装了 `edge-tts` 包：`pip3 install edge-tts`

### Q: 字幕获取失败？
**A:** 该视频可能没有字幕，系统会使用视频描述作为替代

### Q: 博客内容很简单？
**A:** 配置 `OPENAI_API_KEY` 可获得 AI 智能摘要
