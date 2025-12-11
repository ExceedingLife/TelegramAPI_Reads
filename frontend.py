from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Telegram Channel Frontend", version="1.0.0")

# API endpoint (running on port 8000)
API_BASE_URL = "http://localhost:8000"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Channel Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0e1621;
            color: #e4e6eb;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #17212b;
            padding: 15px 20px;
            border-bottom: 1px solid #242f3d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .header h1 {
            font-size: 18px;
            font-weight: 500;
            color: #e4e6eb;
        }

        .channel-selector {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .channel-selector select {
            background: #242f3d;
            color: #e4e6eb;
            border: 1px solid #2b5278;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
            min-width: 200px;
        }

        .channel-selector select:focus {
            outline: none;
            border-color: #5288c1;
        }

        .refresh-btn {
            background: #5288c1;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .refresh-btn:hover {
            background: #5a95d1;
        }

        .refresh-btn:active {
            background: #4a7ab1;
        }

        .refresh-btn.stop {
            background: #d32f2f;
        }

        .refresh-btn.stop:hover {
            background: #e53935;
        }

        .refresh-controls {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .mode-select {
            background: #242f3d;
            color: #e4e6eb;
            border: 1px solid #2b5278;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
        }

        .mode-select:focus {
            outline: none;
            border-color: #5288c1;
        }

        .refresh-interval {
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .refresh-interval label {
            font-size: 12px;
            color: #8e9297;
        }

        .refresh-interval input {
            background: #242f3d;
            color: #e4e6eb;
            border: 1px solid #2b5278;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
            width: 60px;
            text-align: center;
        }

        .refresh-interval input:focus {
            outline: none;
            border-color: #5288c1;
        }

        .container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        .sidebar {
            width: 300px;
            background: #17212b;
            border-right: 1px solid #242f3d;
            overflow-y: auto;
            padding: 10px;
        }

        .channel-item {
            padding: 12px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .channel-item:hover {
            background: #242f3d;
        }

        .channel-item.active {
            background: #2b5278;
        }

        .channel-item h3 {
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 4px;
            color: #e4e6eb;
        }

        .channel-item p {
            font-size: 12px;
            color: #8e9297;
        }

        .messages-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background: #0e1621;
        }

        .messages-list {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message-bubble {
            max-width: 65%;
            padding: 8px 12px;
            border-radius: 12px;
            word-wrap: break-word;
            position: relative;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-bubble.sent {
            background: #5288c1;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .message-bubble.received {
            background: #242f3d;
            color: #e4e6eb;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
            font-size: 12px;
        }

        .message-sender {
            font-weight: 600;
            opacity: 0.9;
        }

        .message-time {
            opacity: 0.7;
            font-size: 11px;
            margin-left: 8px;
        }

        .message-text {
            font-size: 14px;
            line-height: 1.4;
        }

        .message-reactions {
            display: flex;
            gap: 6px;
            margin-top: 8px;
            flex-wrap: wrap;
        }

        .reaction-button {
            display: flex;
            align-items: center;
            gap: 4px;
            background: #242f3d;
            border: 1px solid #2b5278;
            border-radius: 12px;
            padding: 4px 8px;
            font-size: 13px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .reaction-button:hover {
            background: #2b5278;
        }

        .reaction-emoji {
            font-size: 16px;
        }

        .reaction-count {
            color: #8e9297;
            font-weight: 500;
        }

        .message-stats {
            display: flex;
            gap: 12px;
            margin-top: 6px;
            font-size: 11px;
            opacity: 0.7;
        }

        /* Translator view */
        .translator-container {
            flex: 1;
            display: none;
            flex-direction: column;
            padding: 20px;
            gap: 16px;
            background: #0e1621;
        }

        .translator-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        .translator-card {
            background: #17212b;
            border: 1px solid #242f3d;
            border-radius: 12px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .translator-card h3 {
            margin: 0;
            font-size: 14px;
            color: #e4e6eb;
        }

        .translator-textarea {
            width: 100%;
            min-height: 180px;
            background: #0e1621;
            color: #e4e6eb;
            border: 1px solid #2b5278;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            resize: vertical;
        }

        .translator-textarea:focus {
            outline: none;
            border-color: #5288c1;
        }

        .translate-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }

        .translate-btn {
            background: #5288c1;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .translate-btn:hover {
            background: #5a95d1;
        }

        .translator-status {
            font-size: 13px;
            color: #8e9297;
        }

        .translator-error {
            font-size: 13px;
            color: #ff6b6b;
        }

        .translator-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-bottom: 8px;
        }

        .translator-mode-select {
            background: #242f3d;
            color: #e4e6eb;
            border: 1px solid #2b5278;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
        }

        .translator-mode-select:focus {
            outline: none;
            border-color: #5288c1;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #8e9297;
        }

        .error {
            background: #d32f2f;
            color: white;
            padding: 12px;
            margin: 10px;
            border-radius: 8px;
            text-align: center;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #8e9297;
        }

        .empty-state h2 {
            font-size: 18px;
            margin-bottom: 8px;
        }

        .empty-state p {
            font-size: 14px;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #17212b;
        }

        ::-webkit-scrollbar-thumb {
            background: #242f3d;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #2b5278;
        }
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; align-items: center; gap: 10px;">
            <select id="modeSelect" class="mode-select">
                <option value="viewer">📱 Telegram Channel Viewer</option>
                <option value="translator">🌐 Translator</option>
            </select>
        </div>
        <div class="channel-selector">
            <select id="channelSelect">
                <option value="">Select a channel...</option>
            </select>
            <div class="refresh-controls">
                <div class="refresh-interval">
                    <label for="refreshInterval">Refresh (sec):</label>
                    <input type="number" id="refreshInterval" value="30" min="5" max="3600" step="5">
                </div>
                <button class="refresh-btn" id="autoRefreshBtn" onclick="toggleAutoRefresh()">⏸️ Stop Auto-Refresh</button>
                <button class="refresh-btn" onclick="refreshMessages()">🔄 Refresh</button>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="sidebar" id="sidebar">
            <div class="loading">Loading channels...</div>
        </div>

        <div class="messages-container">
            <div class="messages-list" id="messagesList">
                <div class="empty-state" id="viewerEmptyState">
                    <h2>Select a channel to view messages</h2>
                    <p>Choose a channel from the dropdown or sidebar</p>
                </div>
            </div>

            <div class="translator-container" id="translatorContainer">
                <div class="translator-controls">
                    <div>
                        <label for="translatorModeSelect">Translator:</label>
                        <select id="translatorModeSelect" class="translator-mode-select">
                            <option value="online">Online (Google)</option>
                            <option value="offline">Offline (Argos)</option>
                        </select>
                    </div>
                    <div class="translator-status" id="translateCharCount">0 / 5000</div>
                    <div class="translator-error" id="translateError"></div>
                </div>
                <div class="translator-grid">
                    <div class="translator-card">
                        <h3>Input</h3>
                        <textarea id="translateInput" class="translator-textarea" placeholder="Enter text to translate..." oninput="handleTranslateInput()"></textarea>
                    </div>
                    <div class="translator-card">
                        <h3>Output</h3>
                        <textarea id="translateOutput" class="translator-textarea" placeholder="Translation will appear here..." readonly></textarea>
                        <div class="translator-status" id="translateStatus"></div>
                    </div>
                </div>
                <div class="translate-actions">
                    <button class="translate-btn" id="translateBtn" onclick="translateText()">Translate</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE_URL = 'http://127.0.0.1:8000';
        const TRANSLATE_CHAR_LIMIT = 5000;
        const languages = [
            { id: 'ru', name: 'Russian → English', source: 'ru', target: 'en' },
            { id: 'uk', name: 'Ukrainian → English', source: 'uk', target: 'en' }
        ];
        let channels = [];
        let currentChannelId = null;
        let currentMode = 'viewer';
        let selectedLanguage = languages[0].id;
        let autoRefreshInterval = null;
        let autoRefreshEnabled = true;
        let translatorMode = 'online'; // online | offline

        // Format date to Telegram-like format
        function formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (minutes < 1) return 'just now';
            if (minutes < 60) return `${minutes}m ago`;
            if (hours < 24) return `${hours}h ago`;
            if (days < 7) return `${days}d ago`;
            
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        }

        // Load channels
        async function loadChannels() {
            if (currentMode !== 'viewer') {
                return;
            }
            try {
                const response = await fetch(`${API_BASE_URL}/channels`);
                if (!response.ok) throw new Error('Failed to fetch channels');
                
                channels = await response.json();
                
                // Update dropdown
                const select = document.getElementById('channelSelect');
                select.innerHTML = '<option value="">Select a channel...</option>';
                channels.forEach(channel => {
                    const option = document.createElement('option');
                    option.value = channel.id;
                    option.textContent = channel.title + (channel.username ? ` (@${channel.username})` : '');
                    select.appendChild(option);
                });

                // Update sidebar
                const sidebar = document.getElementById('sidebar');
                sidebar.innerHTML = '';
                channels.forEach(channel => {
                    const item = document.createElement('div');
                    item.className = 'channel-item';
                    item.onclick = () => selectChannel(channel.id);
                    item.innerHTML = `
                        <h3>${channel.title}</h3>
                        <p>${channel.username ? '@' + channel.username : 'ID: ' + channel.id}</p>
                    `;
                    sidebar.appendChild(item);
                });

                if (channels.length === 0) {
                    sidebar.innerHTML = '<div class="empty-state"><p>No channels found</p></div>';
                }
            } catch (error) {
                console.error('Error loading channels:', error);
                document.getElementById('sidebar').innerHTML = 
                    `<div class="error">Error loading channels: ${error.message}</div>`;
            }
        }

        // Render language options in sidebar for translator mode
        function renderLanguagesSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.innerHTML = '';

            languages.forEach(lang => {
                const item = document.createElement('div');
                item.className = 'channel-item' + (lang.id === selectedLanguage ? ' active' : '');
                item.onclick = () => {
                    selectedLanguage = lang.id;
                    renderLanguagesSidebar();
                };
                item.innerHTML = `
                    <h3>${lang.name}</h3>
                    <p>Source: ${lang.source.toUpperCase()} → Target: ${lang.target.toUpperCase()}</p>
                `;
                sidebar.appendChild(item);
            });

            if (languages.length === 0) {
                sidebar.innerHTML = '<div class="empty-state"><p>No languages configured</p></div>';
            }
        }

        // Select channel
        function selectChannel(channelId) {
            currentChannelId = channelId;
            
            // Update dropdown
            document.getElementById('channelSelect').value = channelId;
            
            // Update sidebar active state
            document.querySelectorAll('.channel-item').forEach(item => {
                item.classList.remove('active');
            });
            event?.target?.closest('.channel-item')?.classList.add('active');
            
            // Load messages
            loadMessages(channelId);
        }

        // Load messages
        async function loadMessages(channelId) {
            const messagesList = document.getElementById('messagesList');
            messagesList.innerHTML = '<div class="loading">Loading messages...</div>';

            try {
                const response = await fetch(
                    `${API_BASE_URL}/channels/${channelId}/messages?limit=50&translate=true`
                );
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch messages: ${response.statusText}`);
                }

                const messages = await response.json();
                
                if (messages.length === 0) {
                    messagesList.innerHTML = '<div class="empty-state"><h2>No messages found</h2><p>This channel has no messages yet</p></div>';
                    return;
                }

                messagesList.innerHTML = '';
                
                // Reverse messages to show newest at bottom
                messages.reverse().forEach(message => {
                    const bubble = document.createElement('div');
                    bubble.className = 'message-bubble received';
                    
                    const header = document.createElement('div');
                    header.className = 'message-header';
                    
                    const sender = document.createElement('span');
                    sender.className = 'message-sender';
                    sender.textContent = message.sender_username || `User ${message.sender_id || 'Unknown'}`;
                    
                    const time = document.createElement('span');
                    time.className = 'message-time';
                    time.textContent = formatDate(message.date);
                    
                    header.appendChild(sender);
                    header.appendChild(time);
                    
                    const text = document.createElement('div');
                    text.className = 'message-text';
                    text.textContent = message.text || '[Empty message]';
                    
                    bubble.appendChild(header);
                    bubble.appendChild(text);
                    
                    // Add reactions if available
                    if (message.reactions && message.reactions.length > 0) {
                        const reactionsContainer = document.createElement('div');
                        reactionsContainer.className = 'message-reactions';
                        
                        message.reactions.forEach(reaction => {
                            const reactionBtn = document.createElement('div');
                            reactionBtn.className = 'reaction-button';
                            reactionBtn.innerHTML = `
                                <span class="reaction-emoji">${reaction.emoji}</span>
                                <span class="reaction-count">${reaction.count}</span>
                            `;
                            reactionsContainer.appendChild(reactionBtn);
                        });
                        
                        bubble.appendChild(reactionsContainer);
                    }
                    
                    // Add stats if available
                    if (message.views !== null || message.forwards !== null) {
                        const stats = document.createElement('div');
                        stats.className = 'message-stats';
                        if (message.views !== null) {
                            stats.innerHTML += `👁️ ${message.views}`;
                        }
                        if (message.forwards !== null) {
                            stats.innerHTML += `📤 ${message.forwards}`;
                        }
                        bubble.appendChild(stats);
                    }
                    
                    messagesList.appendChild(bubble);
                });

                // Scroll to bottom
                messagesList.scrollTop = messagesList.scrollHeight;
            } catch (error) {
                console.error('Error loading messages:', error);
                messagesList.innerHTML = 
                    `<div class="error">Error loading messages: ${error.message}</div>`;
            }
        }

        // Refresh messages
        function refreshMessages() {
            if (currentChannelId) {
                loadMessages(currentChannelId);
            } else {
                loadChannels();
            }
        }

        // Toggle modes between viewer and translator
        function setMode(mode) {
            currentMode = mode;
            const channelSelect = document.getElementById('channelSelect');
            const refreshControls = document.querySelector('.refresh-controls');
            const messagesList = document.getElementById('messagesList');
            const translatorContainer = document.getElementById('translatorContainer');
            const viewerEmptyState = document.getElementById('viewerEmptyState');

            if (mode === 'viewer') {
                channelSelect.style.display = 'block';
                refreshControls.style.display = 'flex';
                messagesList.style.display = 'flex';
                translatorContainer.style.display = 'none';
                viewerEmptyState.style.display = 'block';
                startAutoRefresh();
                loadChannels();
            } else {
                // Translator mode
                stopAutoRefresh();
                channelSelect.style.display = 'none';
                refreshControls.style.display = 'none';
                messagesList.style.display = 'none';
                viewerEmptyState.style.display = 'none';
                translatorContainer.style.display = 'flex';
                renderLanguagesSidebar();
                const modeSelect = document.getElementById('translatorModeSelect');
                if (modeSelect) {
                    modeSelect.value = translatorMode;
                }
                handleTranslateInput();
            }
        }

        // Translate text using API
        async function translateText() {
            const input = document.getElementById('translateInput');
            const output = document.getElementById('translateOutput');
            const status = document.getElementById('translateStatus');
            const errorEl = document.getElementById('translateError');
            const btn = document.getElementById('translateBtn');
            const lang = languages.find(l => l.id === selectedLanguage) || languages[0];

            const text = input.value.trim();
            if (!text) {
                status.textContent = 'Enter text to translate.';
                return;
            }
            if (text.length > TRANSLATE_CHAR_LIMIT) {
                errorEl.textContent = `Too many characters. Limit is ${TRANSLATE_CHAR_LIMIT}.`;
                status.textContent = '';
                return;
            }

            status.textContent = 'Translating...';
            errorEl.textContent = '';
            output.value = '';

            try {
                const response = await fetch(`${API_BASE_URL}/translate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text,
                        source_lang: lang.source,
                        target_lang: lang.target,
                        mode: translatorMode
                    })
                });

                if (!response.ok) {
                    throw new Error(`Failed: ${response.statusText}`);
                }

                const data = await response.json();
                output.value = data.translated_text || '';
                status.textContent = `Translated ${lang.source.toUpperCase()} → ${lang.target.toUpperCase()}`;
            } catch (error) {
                console.error('Translation error:', error);
                status.textContent = `Error: ${error.message}`;
            }
        }

        function handleTranslateInput() {
            const input = document.getElementById('translateInput');
            const charCount = document.getElementById('translateCharCount');
            const errorEl = document.getElementById('translateError');
            const btn = document.getElementById('translateBtn');
            const len = input.value.length;

            charCount.textContent = `${len} / ${TRANSLATE_CHAR_LIMIT}`;

            if (len > TRANSLATE_CHAR_LIMIT) {
                errorEl.textContent = `Too many characters. Limit is ${TRANSLATE_CHAR_LIMIT}.`;
                btn.disabled = true;
                btn.style.opacity = 0.7;
            } else {
                errorEl.textContent = '';
                btn.disabled = false;
                btn.style.opacity = 1;
            }
        }

        // Toggle auto-refresh
        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const btn = document.getElementById('autoRefreshBtn');
            
            if (autoRefreshEnabled) {
                startAutoRefresh();
                btn.textContent = '⏸️ Stop Auto-Refresh';
                btn.classList.remove('stop');
            } else {
                stopAutoRefresh();
                btn.textContent = '▶️ Start Auto-Refresh';
                btn.classList.add('stop');
            }
        }

        // Start auto-refresh
        function startAutoRefresh() {
            stopAutoRefresh(); // Clear any existing interval
            
            const intervalInput = document.getElementById('refreshInterval');
            const intervalSeconds = parseInt(intervalInput.value) || 30;
            const intervalMs = intervalSeconds * 1000;
            
            autoRefreshInterval = setInterval(() => {
                if (currentChannelId && autoRefreshEnabled) {
                    loadMessages(currentChannelId);
                }
            }, intervalMs);
        }

        // Stop auto-refresh
        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
            }
        }

        // Update refresh interval when input changes
        function updateRefreshInterval() {
            if (autoRefreshEnabled) {
                startAutoRefresh();
            }
        }

        // Channel select change handler
        document.getElementById('channelSelect').addEventListener('change', (e) => {
            if (e.target.value) {
                selectChannel(parseInt(e.target.value));
            }
        });

        // Mode select handler
        document.getElementById('modeSelect').addEventListener('change', (e) => {
            const mode = e.target.value === 'translator' ? 'translator' : 'viewer';
            setMode(mode);
        });

        // Translator mode selector
        document.getElementById('translatorModeSelect').addEventListener('change', (e) => {
            translatorMode = e.target.value === 'offline' ? 'offline' : 'online';
            handleTranslateInput();
        });

        // Refresh interval input change handler
        document.getElementById('refreshInterval').addEventListener('change', updateRefreshInterval);
        document.getElementById('refreshInterval').addEventListener('input', updateRefreshInterval);

        // Initialize on load
        window.addEventListener('load', () => {
            setMode('viewer');
            // Start auto-refresh with default interval in viewer mode
            startAutoRefresh();
            handleTranslateInput();
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def frontend():
    """Serve the Telegram-like frontend"""
    return HTML_TEMPLATE

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Telegram Channel Frontend on http://localhost:8001")
    print("📡 Make sure the API is running on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8001)

