/**
 * YouTube Blog Generator - Frontend Logic
 */

// State
let currentBlogId = null;
let selectedVideoUrl = null;

// DOM Elements
const elements = {
    apiStatus: document.getElementById('apiStatus'),
    channelUrl: document.getElementById('channelUrl'),
    videoCount: document.getElementById('videoCount'),
    fetchChannelBtn: document.getElementById('fetchChannelBtn'),
    videoList: document.getElementById('videoList'),
    videoUrl: document.getElementById('videoUrl'),
    processVideoBtn: document.getElementById('processVideoBtn'),
    audioPlayer: document.getElementById('audioPlayer'),
    audioElement: document.getElementById('audioElement'),
    blogContent: document.getElementById('blogContent'),
    downloadMdBtn: document.getElementById('downloadMdBtn'),
    downloadAudioBtn: document.getElementById('downloadAudioBtn'),
    historyList: document.getElementById('historyList'),
    refreshHistoryBtn: document.getElementById('refreshHistoryBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    toastContainer: document.getElementById('toastContainer'),
};

// Tab Switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;

        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${tabName}Tab`).classList.add('active');
    });
});

// Check API Status
async function checkApiStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        elements.apiStatus.classList.add('ready');
        // Display status based on actual summarizer being used
        const summarizer = data.summarizer;
        if (summarizer === 'openai' && data.has_openai) {
            elements.apiStatus.querySelector('.status-text').textContent = 'OpenAI 就绪';
        } else if (summarizer === 'gemini' && data.has_gemini) {
            elements.apiStatus.querySelector('.status-text').textContent = 'Gemini 就绪';
        } else if (summarizer === 'groq' && data.has_groq) {
            elements.apiStatus.querySelector('.status-text').textContent = 'Groq 就绪';
        } else if (data.has_openai || data.has_gemini || data.has_groq) {
            elements.apiStatus.querySelector('.status-text').textContent = `${summarizer.charAt(0).toUpperCase() + summarizer.slice(1)} 就绪`;
        } else {
            elements.apiStatus.querySelector('.status-text').textContent = 'Edge TTS 模式';
        }
    } catch (error) {
        elements.apiStatus.classList.add('error');
        elements.apiStatus.querySelector('.status-text').textContent = '连接失败';
    }
}

// Show Loading
function showLoading(text = '处理中...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.classList.remove('hidden');
}

// Hide Loading
function hideLoading() {
    elements.loadingOverlay.classList.add('hidden');
}

// Show Toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Format Duration
function formatDuration(seconds) {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Simple Markdown to HTML
function renderMarkdown(text) {
    if (!text) return '';

    return text
        // Headers
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        // Blockquotes
        .replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
        // Horizontal rules
        .replace(/^---$/gm, '<hr>')
        // Line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
}

// Fetch Channel Videos
elements.fetchChannelBtn.addEventListener('click', async () => {
    const url = elements.channelUrl.value.trim();
    const count = parseInt(elements.videoCount.value) || 5;

    if (!url) {
        showToast('请输入频道链接', 'error');
        return;
    }

    showLoading('正在获取视频列表...');

    try {
        const response = await fetch('/api/fetch-channel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, count })
        });

        const data = await response.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        renderVideoList(data.videos);
        showToast(`获取到 ${data.videos.length} 个视频`);

    } catch (error) {
        showToast('获取失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

// Render Video List
function renderVideoList(videos) {
    if (!videos || videos.length === 0) {
        elements.videoList.innerHTML = '<div class="placeholder"><p>未找到视频</p></div>';
        return;
    }

    elements.videoList.innerHTML = videos.map(video => `
        <div class="video-item" data-url="${video.url}">
            <img class="video-thumbnail" src="${video.thumbnail}" alt="" onerror="this.style.display='none'">
            <div class="video-info">
                <div class="video-title" title="${video.title}">${video.title}</div>
                <div class="video-duration">${formatDuration(video.duration)}</div>
            </div>
        </div>
    `).join('');

    // Add click handlers
    elements.videoList.querySelectorAll('.video-item').forEach(item => {
        item.addEventListener('click', () => {
            // Update selection UI
            elements.videoList.querySelectorAll('.video-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');

            selectedVideoUrl = item.dataset.url;
            processVideo(selectedVideoUrl);
        });
    });
}

// Process Single Video (from video tab)
elements.processVideoBtn.addEventListener('click', async () => {
    const url = elements.videoUrl.value.trim();

    if (!url) {
        showToast('请输入视频链接', 'error');
        return;
    }

    await processVideo(url);
});

// Process Video
async function processVideo(url) {
    showLoading('正在处理视频...\n（获取字幕 → AI总结 → 生成语音）');

    try {
        const response = await fetch('/api/process-video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        displayBlog(data.blog);
        refreshHistory();
        showToast('博客生成成功！');

    } catch (error) {
        showToast('处理失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display Blog
function displayBlog(blog) {
    currentBlogId = blog.id;

    // Build model info bar
    let modelInfo = '';
    if (blog.model_used || blog.transcript_length !== undefined) {
        const model = blog.model_used || '未知';
        const transcriptLen = blog.transcript_length !== undefined ? blog.transcript_length : '?';
        modelInfo = `<div class="blog-model-info">
            <span class="model-badge">🤖 ${model}</span>
            <span class="transcript-badge">📝 字幕: ${transcriptLen.toLocaleString()} 字符</span>
        </div>`;
    }

    // Update content
    elements.blogContent.innerHTML = `${modelInfo}<p>${renderMarkdown(blog.content)}</p>`;

    // Update audio player
    if (blog.has_audio) {
        elements.audioElement.src = `/api/audio/${blog.id}`;
        elements.audioPlayer.classList.remove('hidden');
        elements.downloadAudioBtn.disabled = false;
    } else {
        elements.audioPlayer.classList.add('hidden');
        elements.downloadAudioBtn.disabled = true;
    }

    // Enable download buttons
    elements.downloadMdBtn.disabled = false;
}

// Download handlers
elements.downloadMdBtn.addEventListener('click', () => {
    if (currentBlogId) {
        window.location.href = `/api/download/${currentBlogId}/markdown`;
    }
});

elements.downloadAudioBtn.addEventListener('click', () => {
    if (currentBlogId) {
        window.location.href = `/api/download/${currentBlogId}/audio`;
    }
});

// Refresh History
elements.refreshHistoryBtn.addEventListener('click', refreshHistory);

async function refreshHistory() {
    try {
        const response = await fetch('/api/blogs');
        const data = await response.json();

        renderHistory(data.blogs);
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Render History
function renderHistory(blogs) {
    if (!blogs || blogs.length === 0) {
        elements.historyList.innerHTML = '<div class="placeholder"><p>暂无历史记录</p></div>';
        return;
    }

    elements.historyList.innerHTML = blogs.map(blog => `
        <div class="history-item" data-id="${blog.id}">
            <img class="history-thumbnail" src="${blog.thumbnail}" alt="" onerror="this.style.display='none'">
            <div class="history-title" title="${blog.title}">${blog.title}</div>
            <div class="history-date">${new Date(blog.created_at).toLocaleDateString('zh-CN')}</div>
            <div class="history-actions">
                <button class="btn btn-secondary view-btn">查看</button>
                <button class="btn btn-secondary delete-btn">删除</button>
            </div>
        </div>
    `).join('');

    // Add click handlers
    elements.historyList.querySelectorAll('.history-item').forEach(item => {
        const blogId = item.dataset.id;

        item.querySelector('.view-btn').addEventListener('click', async (e) => {
            e.stopPropagation();
            const response = await fetch(`/api/blog/${blogId}`);
            const data = await response.json();
            if (data.blog) {
                displayBlog(data.blog);
            }
        });

        item.querySelector('.delete-btn').addEventListener('click', async (e) => {
            e.stopPropagation();
            if (confirm('确定删除这篇博客？')) {
                await fetch(`/api/blog/${blogId}`, { method: 'DELETE' });
                refreshHistory();
                showToast('已删除');
            }
        });
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkApiStatus();
    refreshHistory();
    initSettings();

    // Check for OAuth success redirect
    const params = new URLSearchParams(window.location.search);
    if (params.get('oauth') === 'success') {
        showToast('Google 登录成功！Gemini Pro 已就绪');
        window.history.replaceState({}, '', '/');
        checkApiStatus();
    }
});

// ============================================
// Settings Modal
// ============================================

function initSettings() {
    const modal = document.getElementById('settingsModal');
    const openBtn = document.getElementById('settingsBtn');
    const closeBtn = document.getElementById('settingsCloseBtn');
    const cancelBtn = document.getElementById('settingsCancelBtn');
    const saveBtn = document.getElementById('settingsSaveBtn');
    const loginBtn = document.getElementById('googleLoginBtn');
    const logoutBtn = document.getElementById('googleLogoutBtn');

    openBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
        loadSettings();
    });

    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));

    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    saveBtn.addEventListener('click', saveSettings);
    loginBtn.addEventListener('click', () => {
        window.location.href = '/api/oauth/google';
    });
    logoutBtn.addEventListener('click', async () => {
        await fetch('/api/oauth/logout', { method: 'POST' });
        showToast('已退出 Google 登录');
        loadSettings();
        checkApiStatus();
    });
}

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();

        // Set key placeholders (masked values)
        const openaiInput = document.getElementById('settingsOpenaiKey');
        const geminiInput = document.getElementById('settingsGeminiKey');
        const groqInput = document.getElementById('settingsGroqKey');

        openaiInput.value = '';
        geminiInput.value = '';
        groqInput.value = '';

        openaiInput.placeholder = data.openai_api_key || 'sk-...';
        geminiInput.placeholder = data.gemini_api_key || 'AIza...';
        groqInput.placeholder = data.groq_api_key || 'gsk_...';

        // Key status indicators
        document.getElementById('openaiKeyStatus').textContent = data.has_openai ? '✅' : '';
        document.getElementById('geminiKeyStatus').textContent = data.has_gemini ? '✅' : '';
        document.getElementById('groqKeyStatus').textContent = data.has_groq ? '✅' : '';

        // TTS engine
        document.getElementById('settingsTtsEngine').value = data.tts_engine || 'edge';

        // OAuth section
        const loggedOut = document.getElementById('oauthLoggedOut');
        const loggedIn = document.getElementById('oauthLoggedIn');
        const notConfigured = document.getElementById('oauthNotConfigured');

        loggedOut.classList.add('hidden');
        loggedIn.classList.add('hidden');
        notConfigured.classList.add('hidden');

        if (!data.has_google_oauth) {
            notConfigured.classList.remove('hidden');
        } else if (data.is_oauth_logged_in) {
            loggedIn.classList.remove('hidden');
        } else {
            loggedOut.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

async function saveSettings() {
    const data = {};

    const openaiKey = document.getElementById('settingsOpenaiKey').value.trim();
    const geminiKey = document.getElementById('settingsGeminiKey').value.trim();
    const groqKey = document.getElementById('settingsGroqKey').value.trim();
    const ttsEngine = document.getElementById('settingsTtsEngine').value;

    if (openaiKey) data.openai_api_key = openaiKey;
    if (geminiKey) data.gemini_api_key = geminiKey;
    if (groqKey) data.groq_api_key = groqKey;
    if (ttsEngine) data.tts_engine = ttsEngine;

    if (Object.keys(data).length === 0) {
        showToast('没有需要保存的更改', 'error');
        return;
    }

    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('设置已保存 ✅');
            document.getElementById('settingsModal').classList.add('hidden');
            checkApiStatus();
        } else {
            showToast('保存失败', 'error');
        }
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    }
}
