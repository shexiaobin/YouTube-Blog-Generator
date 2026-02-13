<p align="center">
  <h1 align="center">🎬 YouTube Blog Generator</h1>
  <p align="center">
    将 YouTube 视频自动转化为精美博客文章 + 语音播客
    <br />
    Transform YouTube videos into blog posts & audio podcasts with AI
  </p>
  <p align="center">
    <a href="#-快速开始--quick-start">快速开始 Quick Start</a> •
    <a href="#-功能特性--features">功能 Features</a> •
    <a href="#-技术架构--architecture">架构 Architecture</a> •
    <a href="#-api-文档--api-docs">API Docs</a> •
    <a href="#-贡献指南--contributing">贡献 Contributing</a>
  </p>
</p> 

---

## ✨ 功能特性 / Features

- 🔗 **YouTube 视频抓取 / Video Fetching** — 支持频道批量抓取或单个视频处理 / Batch fetch from channels or process individual videos
- 🤖 **多模态 AI 模型 / Multi-Modal AI** — 支持 **Custom API** (Gemini 3 Pro 等)、OpenAI、Google Gemini、Groq 等多级回退策略
- ⚙️ **Web 设置界面 / Settings UI** — 现代化配置面板，无需手动编辑 `.env`，支持热重载
- 🔐 **Google OAuth 集成** — 一键登录 Google 账号，解决 API Key 配额限制问题
- 📝 **AI 智能摘要 / AI Summarization** — 深度内容分析，自动生成高质量中文博客
- 🎤 **语音合成 / Text-to-Speech** — 博客一键转播客，支持 Edge TTS（免费）和 OpenAI TTS
- 📥 **多格式导出 / Export** — Markdown 博客 + MP3 音频下载
-  **零成本可用 / Zero-Cost Mode** — 无需任何 API Key 也能使用基础功能

## 🖥️ 界面预览 / UI Preview

```
┌─────────────────────────────────────────────────┐
│              Header + ⚙️ Settings                │
│  Logo + API Status (Custom/OAuth/Key)           │
├──────────────────┬──────────────────────────────┤
│   Video Input    │       Blog Preview           │
│  · Channel Tab   │  · Audio Player              │
│  · Video Tab     │  · Markdown Content           │
│  · Video List    │  · Model used info            │
├──────────────────┴──────────────────────────────┤
│              History / 历史博客                  │
└─────────────────────────────────────────────────┘
```

## 🚀 快速开始 / Quick Start

### 前置条件 / Prerequisites

- Python 3.9+
- pip

### 安装 / Installation

```bash
# 1. Clone the repo / 克隆仓库
git clone https://github.com/your-username/youtube-blog-generator.git
cd youtube-blog-generator

# 2. Create virtual environment (recommended) / 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies / 安装依赖
pip install -r requirements.txt
```

### 配置 / Configuration

推荐直接在 Web 界面点击右上角 **⚙️ 设置** 按钮进行配置。

或者手动编辑 `.env` 文件：

```bash
cp .env.example .env
```

| Variable / 变量 | Description / 说明 | Required / 必填 |
|---------|------|:----:|
| `CUSTOM_API_URL` | Custom API Endpoint (e.g. mttieeo) | ❌ |
| `CUSTOM_API_KEY` | Custom API Key | ❌ |
| `CUSTOM_API_MODEL`| Model name (e.g. `[O]gemini-3-pro-preview`) | ❌ |
| `OpenAI / Gemini` | Official API Keys | ❌ |
| `GOOGLE_CLIENT_ID`| For OAuth Login | ❌ |

**AI 引擎优先级 / Priority：** 
1. **Custom API** (最高优先级 / Highest)
2. **OpenAI**
3. **Gemini** (OAuth > API Key)
4. **Groq**
5. **Local** (Fallback)

### 启动 / Run

**方式一：Python 直接运行**

```bash
python3 app.py
```

**方式二：Docker 运行 (推荐)**

```bash
# Build image
docker build -t youtube-blog-gen .

# Run container
docker run -p 5001:5001 --env-file .env youtube-blog-gen
```

Visit / 访问 **http://localhost:5001** 🎉

## 🏗️ 技术架构 / Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌─────────────┐
│  User Input │───▶│  youtube_fetcher │───▶│  summarizer │───▶│  tts_engine │
│  视频链接   │    │  Fetch video +   │    │  AI blog    │    │  Generate   │
│  Video URL  │    │  subtitles       │    │  generation │    │  audio      │
└─────────────┘    └──────────────────┘    └─────────────┘    └─────────────┘
```

### 项目结构 / Project Structure

```
youtube-blog-generator/
├── app.py                # Flask app — Web server & API routes
├── config.py             # Config management & Priority Logic
├── youtube_fetcher.py    # YouTube video & subtitle fetching
├── summarizer.py         # AI summarization (Custom/OpenAI/Gemini/Groq)
├── tts_engine.py         # Text-to-Speech (Edge TTS / OpenAI)
├── templates/
│   └── index.html        # Frontend page with Settings Modal
├── static/
│   ├── app.js            # Frontend logic & OAuth handling
│   └── style.css         # Styles
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

### 技术栈 / Tech Stack

| Layer / 层级 | Technology / 技术 |
|-----|------|
| **Backend / 后端** | Python, Flask, `requests` |
| **Frontend / 前端** | HTML5, CSS3, Vanilla JS |
| **Video Fetching / 视频抓取** | `yt-dlp`, `youtube-transcript-api` |
| **AI Models / 模型** | **Gemini 3 Pro**, GPT-4o, Llama 3 (Groq) |
| **Auth / 认证** | Google OAuth 2.0 |
| **TTS / 语音合成** | Microsoft Edge TTS, OpenAI TTS |

## 📡 API 文档 / API Docs

All APIs are prefixed with `/api/` and return JSON.
所有 API 以 `/api/` 为前缀，返回 JSON 格式。

| Endpoint / 端点 | Method / 方法 | Description / 功能 |
|------|------|------|
| `/api/status` | GET | System status / 系统状态 |
| `/api/fetch-channel` | POST | Fetch channel video list / 获取频道视频列表 |
| `/api/video-info` | POST | Get video info / 获取视频信息 |
| `/api/process-video` | POST | **Core** — Process video, generate blog + audio / 处理视频生成博客+音频 |
| `/api/blogs` | GET | List all blogs / 列出所有博客 |
| `/api/blog/<id>` | GET | Get blog detail / 获取博客详情 |
| `/api/blog/<id>` | DELETE | Delete blog / 删除博客 |
| `/api/audio/<id>` | GET | Stream audio / 流式播放音频 |
| `/api/download/<id>/audio` | GET | Download audio / 下载音频 |
| `/api/download/<id>/markdown` | GET | Download Markdown / 下载 Markdown |
| `/api/voices` | GET | List TTS voices / 获取 TTS 声音列表 |

### 示例 / Examples

```bash
# Process a video / 处理单个视频
curl -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# Fetch channel videos / 获取频道视频列表
curl -X POST http://localhost:5001/api/fetch-channel \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/@channel", "count": 5}'
```

## 📊 功能对比 / Feature Comparison

| Feature / 功能 | No API Key / 无 Key | With AI API Key / 有 Key |
|------|:----------:|:-------------:|
| YouTube fetching / 视频抓取 | ✅ | ✅ |
| Subtitle extraction / 字幕提取 | ✅ | ✅ |
| Blog generation / 博客生成 | ⚠️ Simple / 简单格式化 | ✅ AI Summary / AI 智能摘要 |
| TTS / 语音合成 | ✅ Edge TTS (free / 免费) | ✅ + OpenAI TTS |
| Audio transcription / 音频转录 | ❌ | ✅ Requires Groq / 需要 Groq |

## 🤝 贡献指南 / Contributing

Contributions are welcome! 欢迎贡献！

1. **Fork** this repo / Fork 本仓库
2. Create a feature branch / 创建功能分支：`git checkout -b feature/amazing-feature`
3. Commit your changes / 提交更改：`git commit -m 'Add amazing feature'`
4. Push to branch / 推送：`git push origin feature/amazing-feature`
5. Open a **Pull Request** / 提交 PR

### 开发建议 / Development Tips

- 📖 Read [TECHNICAL_DOC.md](TECHNICAL_DOC.md) for detailed architecture / 阅读技术文档了解详细架构
- 🧪 Make sure the app starts after your changes / 修改后请确保应用能正常启动
- 📝 Include doc updates with new features / 新功能请附带文档更新

### 改进方向 / Roadmap

- 🗄️ Database storage (SQLite/PostgreSQL) / 数据库存储
- 🌍 Multi-language UI / 多语言界面
- 📦 Batch video processing / 批量处理
- ⏰ Scheduled auto-fetch / 定时自动抓取
- 👤 User accounts & personal blog library / 用户系统
- 🐳 Docker deployment / Docker 部署

## 📄 License

[MIT License](LICENSE)

---

<p align="center">
  ⭐ Star this repo if you find it useful! / 觉得有用请点 Star 支持！
</p>
