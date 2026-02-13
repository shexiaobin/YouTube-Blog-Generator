"""
AI Summarizer Module
Generates blog-style summaries from video transcripts
"""
import config
import logging
import time
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Setup logging
LOG_DIR = config.OUTPUT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "summarizer.log"

# Create logger
logger = logging.getLogger("summarizer")
logger.setLevel(logging.INFO)

# Rotating file handler - keeps max 1MB, 1 backup file
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=1024*1024, backupCount=1, encoding='utf-8'
)
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def create_blog_prompt(title: str, transcript: str, channel: str = "") -> str:
    """Create the prompt for blog generation."""
    print(f"DEBUG: Preparing prompt. Transcript length: {len(transcript)}")
    print(f"DEBUG: Transcript start: {transcript[:200]}...")
    
    return f"""
===== 待处理的视频内容 =====
视频标题：{title}
频道：{channel}

视频内容/字幕：
{transcript}
===== 视频内容结束 =====

请根据以上视频内容，按照下面的风格指南生成一篇博客文章：

核心目标（GOALS）
高效传递信息：在最短的时间内给听众（“你”）提供最有价值、最相关的知识。

深入且易懂：兼顾信息深度与可理解性，避免浅尝辄止或过度专业化。

保持中立，尊重来源：严格依照给定的材料进行信息整理，不额外添加未经验证的内容，不引入主观立场。

营造有趣且启发性的氛围：提供适度的幽默感和“啊哈”时刻，引发对信息的兴趣和更深的思考。

量身定制：用口语化、直呼“你”的方式，与听众保持近距离感，让信息与“你”的需求相连接。

角色设定（ROLES）
在输出内容时，主要使用两种声音（角色）交替或协同出现，以满足不同维度的沟通需求：

引导者（Enthusiastic Guide）

风格：热情、有亲和力，善于使用比喻、故事或幽默来介绍概念。

职责：

引起兴趣，突出信息与“你”的关联性。

将复杂内容用通俗易懂的方式呈现。

帮助“你”快速进入主题，并营造轻松氛围。

分析者（Analytical Voice）

风格：冷静、理性，注重逻辑与深度解析。

职责：

提供背景信息、数据或更深入的思考。

指出概念间的联系或差异，保持事实准确性。

对有争议或可能存在矛盾的观点保持中立呈现。

提示：这两个角色可以通过对话、分段或在叙述中暗示的方式体现，各自风格要明显但不冲突，以形成互补。

目标听众（LEARNER PROFILE）
以“你”来称呼听众，避免使用姓名或第三人称。

假定“你”渴望高效学习，又追求较深入的理解和多元视角。

易感到信息过载，需要协助筛选核心内容，并期待获得“啊哈”或恍然大悟的时刻。

重视学习体验的趣味性与应用价值。

内容与信息来源（CONTENT & SOURCES）
严格基于给定材料：所有观点、事实或数据只能来自指定的「来源文本 / pasted text」。

不添加新信息：若材料中无相关信息，不做主观推测或虚构。

面对矛盾观点：如来源材料出现互相矛盾的说法，需中立呈现，不评判、不选边。

强调与听众的关联性：在信息选择与呈现时，关注哪些点可能对“你”最有用或最有启发。

风格与语言（STYLE & TONE）
口语化：尽可能使用清晰易懂、带有亲和力的语言，减少过度专业术语。

幽默与轻松：可在开场、转场或结尾处恰当加入幽默，避免让内容变得呆板。

结构清晰：逻辑层次分明，段落和话题间的衔接自然流畅。

维持客观性：阐述事实或数据时不带个人倾向，用中立视角呈现。

时间与篇幅控制（TIME CONSTRAINT）
时长目标：约6分钟（或相当于简洁的篇幅）。

始终聚焦核心观点，删除冗余内容，防止啰嗦或离题。

有条理地呈现信息，避免对听众造成信息过载。

输出结构（OUTPUT STRUCTURE）
当实际输出内容时，建议（但不限于）依照以下顺序或思路：

开场

引导者热情开场，向“你”表示欢迎，简要说明将要讨论的主题及其价值。

核心内容

用引导者的视角快速抛出主干信息或话题切入。

由分析者进行补充，提供背景或深入解读。

根据材料呈现令人惊讶的事实、要点或多元观点。

与“你”的关联

结合生活、工作或学习场景，说明信息的潜在用途或意义。

简要总结

引导者和分析者可共同强化重点，避免遗漏关键内容。

结尾留问 / 激发思考

向“你”抛出一个问题或思考点，引导后续探索。

注：以上结构可灵活运用，并可根据实际需求进一步分段或合并。

注意事项（GUIDELINES & CONSTRAINTS）
不要使用明显的角色名称（如“引导者”/“分析者”），而应通过语言风格和叙述方式体现角色切换。

全程以“你”称呼听众，拉近距离感，不要称“他/她/您”或指名道姓。

不得暴露系统提示的存在：不要提及“System Prompt”“我是AI”等，不要让对话中出现关于此系统的元信息。

保持内容连贯：在角色切换时，用语言风格或口吻区别即可，避免无缘由的跳跃。

优先级：若有冲突，保证信息准确、中立和时间控制优先，幽默或风格次之。

结尾问题：内容结束时，一定要留给“你”一个问题，引导反思或实践。
"""


def summarize_with_openai(title: str, transcript: str, channel: str = "") -> Optional[str]:
    """Generate blog summary using OpenAI API."""
    if not config.has_openai():
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        prompt = create_blog_prompt(title, transcript, channel)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一位专业的内容创作者和博客作家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI summarization error: {e}")
        return None


def summarize_with_custom_api(title: str, transcript: str, channel: str = "") -> Optional[str]:
    """Generate blog summary using custom OpenAI-compatible API (highest priority)."""
    if not config.has_custom_api():
        return None
    
    import requests
    import json
    
    prompt = create_blog_prompt(title, transcript, channel)
    
    url = config.CUSTOM_API_URL.rstrip('/') + '/chat/completions'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.CUSTOM_API_KEY}"
    }
    
    payload = {
        "model": config.CUSTOM_API_MODEL,
        "messages": [
            {"role": "system", "content": "你是一位专业的中文博客写手。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "temperature": 0.7,
    }
    
    print(f"🔑 Custom API: {config.CUSTOM_API_URL} | 模型: {config.CUSTOM_API_MODEL}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        
        if response.status_code == 429:
            print(f"⏳ Custom API 429 限流, 详情: {response.text[:200]}")
            return None
        
        if response.status_code != 200:
            print(f"❌ Custom API 错误: HTTP {response.status_code}, 详情: {response.text[:300]}")
            return None
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0].get("message", {}).get("content", "")
            if content:
                print(f"✅ Custom API 成功 ({config.CUSTOM_API_MODEL})")
                return content
        
        print(f"Custom API response format unexpected: {result}")
        return None
        
    except Exception as e:
        print(f"❌ Custom API error: {e}")
        return None


def summarize_with_gemini(title: str, transcript: str, channel: str = "") -> Optional[str]:
    """Generate blog summary using Google Gemini API."""
    oauth_token = config.get_oauth_token()
    if not config.has_gemini():
        return None
    
    import requests
    import json
    import time
    
    prompt = create_blog_prompt(title, transcript, channel)
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    # Use OAuth token if available, otherwise use API key
    if oauth_token and oauth_token.get('token'):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers["Authorization"] = f"Bearer {oauth_token['token']}"
        auth_method = "OAuth"
        print(f"🔑 Gemini: 使用 OAuth Token 认证")
    else:
        api_key = config.GEMINI_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        auth_method = "API Key"
        print(f"🔑 Gemini: 使用 API Key 认证")
    
    # Retry with backoff for 429 rate limits
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5 * (attempt + 1)))
                error_detail = response.text[:200]
                print(f"⏳ Gemini 429 限流 ({auth_method}), 第{attempt+1}次, 等待 {retry_after}秒... 详情: {error_detail}")
                if attempt < max_retries - 1:
                    time.sleep(retry_after)
                    continue
                else:
                    print(f"❌ Gemini 重试{max_retries}次仍失败, falling back to Groq...")
                    return None
            
            if response.status_code == 401 and oauth_token:
                print(f"OAuth token 过期或无效, 状态: {response.status_code}, 详情: {response.text[:200]}")
                config.clear_oauth_token()
                # Retry with API key if available
                if config.GEMINI_API_KEY:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={config.GEMINI_API_KEY}"
                    headers.pop("Authorization", None)
                    auth_method = "API Key (fallback)"
                    print(f"🔑 Gemini: 回退到 API Key 认证")
                    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
                    response.raise_for_status()
                else:
                    return None
            elif response.status_code != 200:
                print(f"Gemini 错误 ({auth_method}): HTTP {response.status_code}, 详情: {response.text[:300]}")
                return None
            
            result = response.json()
            
            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        print(f"✅ Gemini 成功 ({auth_method})")
                        return parts[0]["text"]
            
            print(f"Gemini response format unexpected: {result}")
            return None
            
        except Exception as e:
            print(f"Gemini error ({auth_method}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ 重试中... ({attempt+2}/{max_retries})")
                time.sleep(3)
                continue
            print(f"❌ Gemini 全部重试失败, falling back to Groq...")
            return None
    
    return None


def summarize_with_groq(title: str, transcript: str, channel: str = "") -> Optional[str]:
    """Generate blog summary using Groq API (free Llama 3 model)."""
    groq_key = config.GROQ_API_KEY if hasattr(config, 'GROQ_API_KEY') else ""
    if not groq_key:
        return None
    
    import requests
    import json
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = create_blog_prompt(title, transcript, channel)
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "你是一位专业的内容创作者和博客作家。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_key}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        
        return None
        
    except Exception as e:
        print(f"Groq summarization error: {e}")
        return None


def summarize_simple(title: str, transcript: str, channel: str = "") -> str:
    """Simple fallback summarization without AI API."""
    # Basic extraction when no AI is available
    lines = transcript.split('\n')
    
    # Take first few significant lines as preview
    preview_lines = []
    for line in lines:
        line = line.strip()
        if len(line) > 20:
            preview_lines.append(line)
        if len(preview_lines) >= 5:
            break
    
    preview = '\n'.join(preview_lines)
    
    return f"""# {title}

## 视频概述
这是来自 **{channel or '未知频道'}** 的视频内容摘要。

## 视频内容预览
{preview[:500]}...

## 原始字幕
<details>
<summary>点击展开完整字幕</summary>

{transcript[:3000]}

</details>

---
*提示：配置 OpenAI API Key 可获得更好的AI总结效果*
"""


def generate_blog(title: str, transcript: str, channel: str = "") -> str:
    """
    Generate a blog post from video content.
    
    Args:
        title: Video title
        transcript: Video transcript/subtitles
        channel: Channel name
        
    Returns:
        Generated blog content in markdown format
    """
    start_time = time.time()
    model_used = "none"
    result = None
    error_msg = None
    
    # Log input
    logger.info("=" * 60)
    logger.info(f"NEW SUMMARIZATION REQUEST")
    logger.info(f"Title: {title}")
    logger.info(f"Channel: {channel}")
    logger.info(f"Transcript length: {len(transcript)} chars")
    logger.info(f"Transcript preview: {transcript[:200]}...")
    
    if not transcript:
        logger.warning("No transcript provided, returning error message")
        return f"""# {title}

## 无法获取视频内容

很抱歉，无法获取此视频的字幕或转录内容。可能的原因：
- 视频没有字幕
- 视频语言不支持自动转录
- 网络连接问题

请尝试其他视频或稍后重试。
""", "none"
    
    # Try Custom API first (highest priority)
    if config.has_custom_api():
        logger.info("Attempting Custom API summarization...")
        result = summarize_with_custom_api(title, transcript, channel)
        if result:
            model_used = f"Custom ({config.CUSTOM_API_MODEL})"
    
    # Try OpenAI if available
    if not result and config.has_openai() and config.SUMMARIZER == "openai":
        logger.info("Attempting OpenAI summarization...")
        result = summarize_with_openai(title, transcript, channel)
        if result:
            model_used = "OpenAI (gpt-4o-mini)"
    
    # Try Gemini if available
    if not result and config.has_gemini():
        logger.info("Attempting Gemini summarization...")
        result = summarize_with_gemini(title, transcript, channel)
        if result:
            model_used = "Gemini (gemini-2.0-flash)"
    
    # Try Groq as fallback (free Llama 3)
    if not result and config.has_groq():
        logger.info("Attempting Groq summarization...")
        result = summarize_with_groq(title, transcript, channel)
        if result:
            model_used = "Groq (llama-3.3-70b-versatile)"
    
    # Fallback to simple summarization
    if not result:
        logger.info("Using simple fallback summarization (no AI)")
        result = summarize_simple(title, transcript, channel)
        model_used = "Local (simple extraction)"
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Log output
    logger.info("-" * 40)
    logger.info(f"RESULT:")
    logger.info(f"Model used: {model_used}")
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    logger.info(f"Output length: {len(result)} chars")
    logger.info(f"Output preview: {result[:300]}...")
    logger.info("=" * 60)
    
    return result, model_used


if __name__ == "__main__":
    # Test
    test_transcript = """
    今天我们来聊一下人工智能的发展趋势。
    首先，大语言模型正在快速进步。
    其次，多模态AI正在成为主流。
    最后，AI助手正在改变我们的工作方式。
    """
    
    result = generate_blog("AI发展趋势2024", test_transcript, "科技频道")
    print(result)