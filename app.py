"""
Flask Web Application for YouTube Blog Generator
"""
import os
import json
import uuid
import secrets
from datetime import datetime

# Allow OAuth over HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, redirect, session
from flask_cors import CORS

import config
from youtube_fetcher import get_channel_videos, get_video_info, get_video_transcript
from summarizer import generate_blog
from tts_engine import generate_audio, get_available_voices

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# In-memory storage for blogs (in production, use a database)
blogs_db = {}


def load_blogs():
    """Load existing blogs from disk."""
    global blogs_db
    blogs_file = config.OUTPUT_DIR / "blogs.json"
    if blogs_file.exists():
        try:
            with open(blogs_file, 'r', encoding='utf-8') as f:
                blogs_db = json.load(f)
        except:
            blogs_db = {}


def save_blogs():
    """Save blogs to disk."""
    blogs_file = config.OUTPUT_DIR / "blogs.json"
    with open(blogs_file, 'w', encoding='utf-8') as f:
        json.dump(blogs_db, f, ensure_ascii=False, indent=2)


# Load blogs on startup
load_blogs()


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/fetch-channel', methods=['POST'])
def fetch_channel():
    """Fetch videos from a YouTube channel."""
    data = request.get_json()
    url = data.get('url', '')
    count = data.get('count', 10)
    
    if not url:
        return jsonify({'error': '请提供频道链接'}), 400
    
    try:
        videos = get_channel_videos(url, count)
        if not videos:
            return jsonify({'error': '无法获取视频列表，请检查链接是否正确'}), 400
        
        return jsonify({'videos': videos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-info', methods=['POST'])
def video_info():
    """Get info for a single video."""
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': '请提供视频链接'}), 400
    
    try:
        info = get_video_info(url)
        if not info:
            return jsonify({'error': '无法获取视频信息'}), 400
        
        return jsonify({'video': info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-video', methods=['POST'])
def process_video():
    """Process a video: extract transcript, generate blog, and create audio."""
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': '请提供视频链接'}), 400
    
    try:
        # Get video info
        info = get_video_info(url)
        if not info:
            return jsonify({'error': '无法获取视频信息'}), 400
        
        # Get transcript
        transcript = get_video_transcript(url)
        
        # Generate blog
        blog_content, model_used = generate_blog(
            title=info.get('title', 'Unknown'),
            transcript=transcript or '',
            channel=info.get('channel', '')
        )
        
        # Generate unique ID
        blog_id = str(uuid.uuid4())[:8]
        
        # Save blog content
        blog_file = config.BLOGS_DIR / f"{blog_id}.md"
        with open(blog_file, 'w', encoding='utf-8') as f:
            f.write(blog_content)
        
        # Generate audio
        audio_file = config.AUDIO_DIR / f"{blog_id}.mp3"
        audio_success = generate_audio(blog_content, str(audio_file))
        
        # Store blog metadata
        blog_data = {
            'id': blog_id,
            'title': info.get('title', 'Unknown'),
            'channel': info.get('channel', ''),
            'video_url': url,
            'thumbnail': info.get('thumbnail', ''),
            'content': blog_content,
            'has_audio': audio_success,
            'model_used': model_used,
            'transcript_length': len(transcript or ''),
            'created_at': datetime.now().isoformat(),
        }
        blogs_db[blog_id] = blog_data
        save_blogs()
        
        return jsonify({'blog': blog_data})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/blogs', methods=['GET'])
def list_blogs():
    """List all generated blogs."""
    blogs = list(blogs_db.values())
    blogs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({'blogs': blogs})


@app.route('/api/blog/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    """Get a specific blog."""
    if blog_id not in blogs_db:
        return jsonify({'error': '博客不存在'}), 404
    return jsonify({'blog': blogs_db[blog_id]})


@app.route('/api/blog/<blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    """Delete a blog."""
    if blog_id not in blogs_db:
        return jsonify({'error': '博客不存在'}), 404
    
    # Delete files
    blog_file = config.BLOGS_DIR / f"{blog_id}.md"
    audio_file = config.AUDIO_DIR / f"{blog_id}.mp3"
    
    if blog_file.exists():
        blog_file.unlink()
    if audio_file.exists():
        audio_file.unlink()
    
    del blogs_db[blog_id]
    save_blogs()
    
    return jsonify({'success': True})


@app.route('/api/download/<blog_id>/audio', methods=['GET'])
def download_audio(blog_id):
    """Download blog audio file."""
    audio_file = config.AUDIO_DIR / f"{blog_id}.mp3"
    
    if not audio_file.exists():
        return jsonify({'error': '音频文件不存在'}), 404
    
    blog = blogs_db.get(blog_id, {})
    filename = f"{blog.get('title', 'blog')}.mp3"
    
    return send_file(
        audio_file,
        mimetype='audio/mpeg',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/download/<blog_id>/markdown', methods=['GET'])
def download_markdown(blog_id):
    """Download blog markdown file."""
    blog_file = config.BLOGS_DIR / f"{blog_id}.md"
    
    if not blog_file.exists():
        return jsonify({'error': '博客文件不存在'}), 404
    
    blog = blogs_db.get(blog_id, {})
    filename = f"{blog.get('title', 'blog')}.md"
    
    return send_file(
        blog_file,
        mimetype='text/markdown',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/audio/<blog_id>', methods=['GET'])
def serve_audio(blog_id):
    """Serve audio file for streaming."""
    audio_file = config.AUDIO_DIR / f"{blog_id}.mp3"
    
    if not audio_file.exists():
        return jsonify({'error': '音频文件不存在'}), 404
    
    return send_file(audio_file, mimetype='audio/mpeg')


@app.route('/api/voices', methods=['GET'])
def list_voices():
    """List available TTS voices."""
    return jsonify({'voices': get_available_voices()})


@app.route('/api/status', methods=['GET'])
def status():
    """Get API status."""
    return jsonify({
        'status': 'ok',
        'has_openai': config.has_openai(),
        'has_gemini': config.has_gemini(),
        'has_groq': config.has_groq(),
        'tts_engine': config.TTS_ENGINE,
        'summarizer': config.SUMMARIZER,
        'has_google_oauth': config.has_google_oauth(),
        'is_oauth_logged_in': config.is_oauth_logged_in(),
    })


# ============================================
# Settings API
# ============================================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings (masked keys)."""
    return jsonify({
        'openai_api_key': config.mask_key(config.OPENAI_API_KEY),
        'gemini_api_key': config.mask_key(config.GEMINI_API_KEY),
        'groq_api_key': config.mask_key(config.GROQ_API_KEY),
        'custom_api_url': config.CUSTOM_API_URL if config.CUSTOM_API_URL else '',
        'custom_api_key': config.mask_key(config.CUSTOM_API_KEY),
        'custom_api_model': config.CUSTOM_API_MODEL if config.CUSTOM_API_MODEL else '',
        'tts_engine': config.TTS_ENGINE,
        'tts_voice': config.TTS_VOICE,
        'summarizer': config.SUMMARIZER,
        'has_custom_api': config.has_custom_api(),
        'has_openai': config.has_openai(),
        'has_gemini': config.has_gemini(),
        'has_groq': config.has_groq(),
        'has_google_oauth': config.has_google_oauth(),
        'is_oauth_logged_in': config.is_oauth_logged_in(),
    })


@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save API keys and settings to .env file."""
    data = request.get_json()

    updates = {}
    # Only update keys that were provided (non-empty)
    if data.get('openai_api_key'):
        updates['OPENAI_API_KEY'] = data['openai_api_key']
    if data.get('gemini_api_key'):
        updates['GEMINI_API_KEY'] = data['gemini_api_key']
    if data.get('groq_api_key'):
        updates['GROQ_API_KEY'] = data['groq_api_key']
    if data.get('custom_api_url'):
        updates['CUSTOM_API_URL'] = data['custom_api_url']
    if data.get('custom_api_key'):
        updates['CUSTOM_API_KEY'] = data['custom_api_key']
    if data.get('custom_api_model'):
        updates['CUSTOM_API_MODEL'] = data['custom_api_model']
    if data.get('tts_engine'):
        updates['TTS_ENGINE'] = data['tts_engine']
    if data.get('tts_voice'):
        updates['TTS_VOICE'] = data['tts_voice']

    if updates:
        config.update_env_file(updates)
        config.reload_config()

    return jsonify({
        'success': True,
        'message': '设置已保存',
        'summarizer': config.SUMMARIZER,
        'has_custom_api': config.has_custom_api(),
        'has_openai': config.has_openai(),
        'has_gemini': config.has_gemini(),
        'has_groq': config.has_groq(),
    })


# ============================================
# Google OAuth
# ============================================

@app.route('/api/oauth/google', methods=['GET'])
def oauth_google_login():
    """Start Google OAuth flow."""
    if not config.has_google_oauth():
        return jsonify({'error': '未配置 Google OAuth (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)'}), 400

    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        {
            'web': {
                'client_id': config.GOOGLE_CLIENT_ID,
                'client_secret': config.GOOGLE_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
            }
        },
        scopes=[
            'https://www.googleapis.com/auth/generative-language.retriever',
            'https://www.googleapis.com/auth/cloud-platform',
        ],
        redirect_uri=request.host_url.rstrip('/') + '/api/oauth/callback'
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/api/oauth/callback', methods=['GET'])
def oauth_callback():
    """Handle Google OAuth callback."""
    # Check for error in callback (e.g. user denied access)
    error = request.args.get('error')
    if error:
        return redirect(f'/?oauth_error={error}')

    if not config.has_google_oauth():
        return redirect('/?oauth_error=not_configured')

    from google_auth_oauthlib.flow import Flow

    try:
        flow = Flow.from_client_config(
            {
                'web': {
                    'client_id': config.GOOGLE_CLIENT_ID,
                    'client_secret': config.GOOGLE_CLIENT_SECRET,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/generative-language.retriever',
                'https://www.googleapis.com/auth/cloud-platform',
            ],
            redirect_uri=request.host_url.rstrip('/') + '/api/oauth/callback',
            state=session.get('oauth_state')
        )

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        config.set_oauth_token({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'client_id': config.GOOGLE_CLIENT_ID,
            'client_secret': config.GOOGLE_CLIENT_SECRET,
        })

        return redirect('/?oauth=success')
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return redirect('/?oauth_error=callback_failed')


@app.route('/api/oauth/logout', methods=['POST'])
def oauth_logout():
    """Clear OAuth session."""
    config.clear_oauth_token()
    return jsonify({'success': True, 'message': 'Google 账号已退出'})


if __name__ == '__main__':
    print("=" * 50)
    print("YouTube Blog Generator")
    print("=" * 50)
    print(f"Custom API: {'已配置 (' + config.CUSTOM_API_MODEL + ')' if config.has_custom_api() else '未配置'}")
    print(f"OpenAI API: {'已配置' if config.has_openai() else '未配置'}")
    print(f"Gemini API: {'已配置' if config.has_gemini() else '未配置'}")
    print(f"Groq API: {'已配置' if config.has_groq() else '未配置'}")
    print(f"TTS 引擎: {config.TTS_ENGINE}")
    print(f"总结器: {config.SUMMARIZER}")
    print("=" * 50)
    print("启动服务器: http://localhost:5001")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
