// ===== Configuration =====
const CONFIG = {
    apiUrl: localStorage.getItem('nca_api_url') || 'http://localhost:8080',
    apiKey: localStorage.getItem('nca_api_key') || 'change_me_to_secure_key_123',
    autoExecute: localStorage.getItem('nca_auto_execute') === 'true'
};

// ===== API Endpoint Definitions =====
const API_ENDPOINTS = {
    audio: {
        concatenate: {
            endpoint: '/v1/audio/concatenate',
            description: 'Kombiniert mehrere Audiodateien',
            keywords: ['audio', 'zusammenfügen', 'kombinieren', 'merge', 'concat'],
            params: ['audio_urls']
        }
    },
    code: {
        executePython: {
            endpoint: '/v1/code/execute/python',
            description: 'Führt Python-Code aus',
            keywords: ['python', 'code', 'ausführen', 'execute', 'script'],
            params: ['code']
        }
    },
    image: {
        convertToVideo: {
            endpoint: '/v1/image/convert/video',
            description: 'Konvertiert Bild zu Video',
            keywords: ['bild', 'video', 'konvertieren', 'image', 'convert'],
            params: ['image_url', 'duration', 'zoom']
        },
        screenshotWebpage: {
            endpoint: '/v1/image/screenshot/webpage',
            description: 'Erstellt Screenshot einer Webseite',
            keywords: ['screenshot', 'webseite', 'webpage', 'capture', 'bild'],
            params: ['url', 'viewport_width', 'viewport_height']
        }
    },
    media: {
        convert: {
            endpoint: '/v1/media/convert',
            description: 'Konvertiert Medienformate',
            keywords: ['konvertieren', 'convert', 'format', 'media'],
            params: ['media_url', 'output_format']
        },
        convertToMp3: {
            endpoint: '/v1/media/convert/mp3',
            description: 'Konvertiert zu MP3',
            keywords: ['mp3', 'audio', 'konvertieren', 'convert'],
            params: ['media_url']
        },
        transcribe: {
            endpoint: '/v1/media/transcribe',
            description: 'Transkribiert Audio/Video',
            keywords: ['transkript', 'transcribe', 'untertitel', 'text', 'speech'],
            params: ['media_url', 'language']
        },
        metadata: {
            endpoint: '/v1/media/metadata',
            description: 'Extrahiert Metadaten',
            keywords: ['metadaten', 'metadata', 'info', 'information'],
            params: ['media_url']
        }
    },
    video: {
        addAudio: {
            endpoint: '/v1/video/add/audio',
            description: 'Fügt Audio zu Video hinzu',
            keywords: ['video', 'audio', 'hinzufügen', 'add', 'zusammenfügen', 'merge'],
            params: ['video_url', 'audio_url']
        },
        addCaptions: {
            endpoint: '/v1/video/add/captions',
            description: 'Fügt Untertitel hinzu',
            keywords: ['untertitel', 'captions', 'subtitles', 'hinzufügen'],
            params: ['video_url', 'captions']
        },
        concatenate: {
            endpoint: '/v1/video/concatenate',
            description: 'Fügt Videos zusammen',
            keywords: ['video', 'zusammenfügen', 'concatenate', 'merge', 'combine'],
            params: ['video_urls']
        },
        resize: {
            endpoint: '/v1/video/resize',
            description: 'Ändert Video-Größe',
            keywords: ['größe', 'resize', 'scale', 'dimension'],
            params: ['video_url', 'width', 'height']
        }
    }
};

// ===== State Management =====
const state = {
    messages: [],
    attachedFiles: [],
    history: JSON.parse(localStorage.getItem('nca_history') || '[]')
};

// ===== DOM Elements =====
const elements = {
    chatContainer: document.getElementById('chatContainer'),
    messages: document.getElementById('messages'),
    userInput: document.getElementById('userInput'),
    sendBtn: document.getElementById('sendBtn'),
    attachBtn: document.getElementById('attachBtn'),
    fileInput: document.getElementById('fileInput'),
    fileAttachments: document.getElementById('fileAttachments'),
    settingsBtn: document.getElementById('settingsBtn'),
    settingsModal: document.getElementById('settingsModal'),
    historyBtn: document.getElementById('historyBtn'),
    historyModal: document.getElementById('historyModal'),
    historyList: document.getElementById('historyList')
};

// ===== AI Intent Recognition =====
function analyzeIntent(userMessage) {
    const message = userMessage.toLowerCase();
    const detectedActions = [];

    // Durchsuche alle Endpunkte
    for (const [category, endpoints] of Object.entries(API_ENDPOINTS)) {
        for (const [name, config] of Object.entries(endpoints)) {
            const score = config.keywords.reduce((acc, keyword) => {
                return acc + (message.includes(keyword.toLowerCase()) ? 1 : 0);
            }, 0);

            if (score > 0) {
                detectedActions.push({
                    category,
                    name,
                    config,
                    score,
                    confidence: Math.min(score / config.keywords.length, 1)
                });
            }
        }
    }

    // Sortiere nach Score
    detectedActions.sort((a, b) => b.score - a.score);

    return detectedActions.length > 0 ? detectedActions[0] : null;
}

// ===== Extract Parameters from Message =====
function extractParameters(message, action) {
    const params = {};
    
    // URL-Extraktion
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = message.match(urlRegex) || [];
    
    if (action.config.params.includes('video_url') && urls.length > 0) {
        params.video_url = urls[0];
    }
    if (action.config.params.includes('audio_url') && urls.length > 1) {
        params.audio_url = urls[1];
    }
    if (action.config.params.includes('media_url') && urls.length > 0) {
        params.media_url = urls[0];
    }
    if (action.config.params.includes('image_url') && urls.length > 0) {
        params.image_url = urls[0];
    }
    if (action.config.params.includes('url') && urls.length > 0) {
        params.url = urls[0];
    }
    
    // Sprache erkennen
    if (action.config.params.includes('language')) {
        if (message.includes('deutsch') || message.includes('german')) {
            params.language = 'de';
        } else if (message.includes('englisch') || message.includes('english')) {
            params.language = 'en';
        } else {
            params.language = 'de'; // Default
        }
    }
    
    // Viewport-Größe für Screenshots
    if (action.config.params.includes('viewport_width')) {
        params.viewport_width = 1920;
        params.viewport_height = 1080;
    }
    
    // Attached Files
    if (state.attachedFiles.length > 0) {
        const fileUrls = state.attachedFiles.map(f => f.url || f.name);
        if (action.config.params.includes('video_urls')) {
            params.video_urls = fileUrls;
        } else if (action.config.params.includes('audio_urls')) {
            params.audio_urls = fileUrls;
        }
    }
    
    return params;
}

// ===== API Call =====
async function callAPI(endpoint, params) {
    const response = await fetch(`${CONFIG.apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': CONFIG.apiKey
        },
        body: JSON.stringify(params)
    });
    
    if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
}

// ===== UI Functions =====
function addMessage(role, content, apiAction = null) {
    const message = {
        role,
        content,
        apiAction,
        timestamp: new Date().toISOString()
    };
    
    state.messages.push(message);
    renderMessage(message);
    scrollToBottom();
}

function renderMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = message.role === 'user' 
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = message.content;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date(message.timestamp).toLocaleTimeString('de-DE', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    contentDiv.appendChild(bubble);
    
    if (message.apiAction) {
        const actionCard = createAPIActionCard(message.apiAction);
        contentDiv.appendChild(actionCard);
    }
    
    contentDiv.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    elements.messages.appendChild(messageDiv);
}

function createAPIActionCard(action) {
    const card = document.createElement('div');
    card.className = 'api-action';
    card.id = `action-${Date.now()}`;
    
    card.innerHTML = `
        <div class="api-action-header">
            <div class="api-action-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            </div>
            <div>
                <div class="api-action-title">${action.config.description}</div>
                <div class="api-action-endpoint">${action.config.endpoint}</div>
            </div>
        </div>
        <div class="api-action-params">
            <pre>${JSON.stringify(action.params, null, 2)}</pre>
        </div>
        <div class="api-action-buttons">
            <button class="btn-primary" onclick="executeAction('${card.id}', ${JSON.stringify(action).replace(/"/g, '&quot;')})">
                Ausführen
            </button>
            <button class="btn-secondary" onclick="cancelAction('${card.id}')">
                Abbrechen
            </button>
        </div>
    `;
    
    if (CONFIG.autoExecute) {
        setTimeout(() => executeAction(card.id, action), 500);
    }
    
    return card;
}

async function executeAction(cardId, action) {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    // Update UI
    const buttonsDiv = card.querySelector('.api-action-buttons');
    buttonsDiv.innerHTML = `
        <div class="api-action-status pending">
            <div class="spinner"></div>
            <span>Wird ausgeführt...</span>
        </div>
    `;
    
    try {
        const result = await callAPI(action.config.endpoint, action.params);
        
        buttonsDiv.innerHTML = `
            <div class="api-action-status success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Erfolgreich!</span>
            </div>
        `;
        
        // Add result message
        addMessage('assistant', formatResult(result));
        
        // Save to history
        saveToHistory(action, result);
        
    } catch (error) {
        buttonsDiv.innerHTML = `
            <div class="api-action-status error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>Fehler: ${error.message}</span>
            </div>
        `;
    }
}

function cancelAction(cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    const buttonsDiv = card.querySelector('.api-action-buttons');
    buttonsDiv.innerHTML = `
        <div class="api-action-status" style="background: rgba(148, 163, 184, 0.1); color: var(--text-muted);">
            <span>Abgebrochen</span>
        </div>
    `;
}

function formatResult(result) {
    if (result.output_url) {
        return `✅ Fertig! Ergebnis: ${result.output_url}`;
    }
    if (result.job_id) {
        return `✅ Job gestartet! Job-ID: ${result.job_id}`;
    }
    if (result.text) {
        return `✅ Transkript:\n\n${result.text}`;
    }
    return `✅ Erfolgreich abgeschlossen!\n\n${JSON.stringify(result, null, 2)}`;
}

function saveToHistory(action, result) {
    state.history.unshift({
        action,
        result,
        timestamp: new Date().toISOString()
    });
    
    // Limit to 50 entries
    if (state.history.length > 50) {
        state.history = state.history.slice(0, 50);
    }
    
    localStorage.setItem('nca_history', JSON.stringify(state.history));
}

function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

// ===== Event Handlers =====
async function handleSendMessage() {
    const message = elements.userInput.value.trim();
    if (!message) return;
    
    // Hide welcome message
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.style.display = 'none';
    
    // Add user message
    addMessage('user', message);
    
    // Clear input
    elements.userInput.value = '';
    elements.sendBtn.disabled = true;
    
    // Analyze intent
    const action = analyzeIntent(message);
    
    if (action) {
        const params = extractParameters(message, action);
        
        addMessage('assistant', `Ich habe verstanden! Ich werde "${action.config.description}" ausführen.`, {
            ...action,
            params
        });
    } else {
        addMessage('assistant', 'Entschuldigung, ich konnte keine passende Aktion für Ihre Anfrage finden. Bitte versuchen Sie es mit einer anderen Formulierung oder prüfen Sie die Beispiele.');
    }
    
    // Clear attached files
    state.attachedFiles = [];
    renderFileAttachments();
}

function handleFileAttach() {
    elements.fileInput.click();
}

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    state.attachedFiles.push(...files);
    renderFileAttachments();
}

function removeFile(index) {
    state.attachedFiles.splice(index, 1);
    renderFileAttachments();
}

function renderFileAttachments() {
    elements.fileAttachments.innerHTML = '';
    
    state.attachedFiles.forEach((file, index) => {
        const attachment = document.createElement('div');
        attachment.className = 'file-attachment';
        attachment.innerHTML = `
            <span>📎 ${file.name}</span>
            <button class="file-attachment-remove" onclick="removeFile(${index})">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        `;
        elements.fileAttachments.appendChild(attachment);
    });
}

// ===== Settings =====
function openSettings() {
    elements.settingsModal.classList.add('active');
    document.getElementById('apiUrl').value = CONFIG.apiUrl;
    document.getElementById('apiKey').value = CONFIG.apiKey;
    document.getElementById('autoExecute').checked = CONFIG.autoExecute;
}

function closeSettings() {
    elements.settingsModal.classList.remove('active');
}

function saveSettings() {
    CONFIG.apiUrl = document.getElementById('apiUrl').value;
    CONFIG.apiKey = document.getElementById('apiKey').value;
    CONFIG.autoExecute = document.getElementById('autoExecute').checked;
    
    localStorage.setItem('nca_api_url', CONFIG.apiUrl);
    localStorage.setItem('nca_api_key', CONFIG.apiKey);
    localStorage.setItem('nca_auto_execute', CONFIG.autoExecute);
    
    closeSettings();
}

// ===== History =====
function openHistory() {
    elements.historyModal.classList.add('active');
    renderHistory();
}

function closeHistory() {
    elements.historyModal.classList.remove('active');
}

function renderHistory() {
    elements.historyList.innerHTML = '';
    
    if (state.history.length === 0) {
        elements.historyList.innerHTML = '<p style="text-align: center; color: var(--text-muted);">Noch keine Einträge im Verlauf</p>';
        return;
    }
    
    state.history.forEach((entry, index) => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="history-item-time">${new Date(entry.timestamp).toLocaleString('de-DE')}</div>
            <div class="history-item-text">${entry.action.config.description}</div>
        `;
        elements.historyList.appendChild(item);
    });
}

function clearHistory() {
    if (confirm('Möchten Sie den gesamten Verlauf löschen?')) {
        state.history = [];
        localStorage.removeItem('nca_history');
        renderHistory();
    }
}

// ===== Event Listeners =====
elements.sendBtn.addEventListener('click', handleSendMessage);
elements.userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});
elements.userInput.addEventListener('input', () => {
    elements.sendBtn.disabled = !elements.userInput.value.trim();
    
    // Auto-resize textarea
    elements.userInput.style.height = 'auto';
    elements.userInput.style.height = elements.userInput.scrollHeight + 'px';
});

elements.attachBtn.addEventListener('click', handleFileAttach);
elements.fileInput.addEventListener('change', handleFileSelect);

elements.settingsBtn.addEventListener('click', openSettings);
document.getElementById('closeSettings').addEventListener('click', closeSettings);
document.getElementById('cancelSettings').addEventListener('click', closeSettings);
document.getElementById('saveSettings').addEventListener('click', saveSettings);

elements.historyBtn.addEventListener('click', openHistory);
document.getElementById('closeHistory').addEventListener('click', closeHistory);
document.getElementById('closeHistoryBtn').addEventListener('click', closeHistory);
document.getElementById('clearHistory').addEventListener('click', clearHistory);

// Example prompts
document.querySelectorAll('.example-prompt').forEach(btn => {
    btn.addEventListener('click', () => {
        elements.userInput.value = btn.dataset.prompt;
        elements.sendBtn.disabled = false;
        elements.userInput.focus();
    });
});

// Close modals on outside click
elements.settingsModal.addEventListener('click', (e) => {
    if (e.target === elements.settingsModal) closeSettings();
});
elements.historyModal.addEventListener('click', (e) => {
    if (e.target === elements.historyModal) closeHistory();
});

// Make functions global for onclick handlers
window.executeAction = executeAction;
window.cancelAction = cancelAction;
window.removeFile = removeFile;

console.log('🚀 NCA Toolkit AI Assistant geladen!');
console.log('API URL:', CONFIG.apiUrl);
console.log('Verfügbare Endpunkte:', Object.keys(API_ENDPOINTS).length);
