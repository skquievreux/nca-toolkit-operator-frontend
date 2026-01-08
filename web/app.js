// ===== Configuration =====
const CONFIG = {
    apiUrl: localStorage.getItem('nca_api_url') || 'http://localhost:5000',  // Flask Backend Server!
    autoExecute: localStorage.getItem('nca_auto_execute') === 'true'
};

// ===== State Management =====
const state = {
    messages: [],
    attachedFiles: [],
    history: [], // Will be loaded from server
    allScenarios: {},
    currentScenarioId: null,
    currentConversationId: localStorage.getItem('last_conversation_id') || null,
    logs: [],
    backendUrl: CONFIG.apiUrl,
    jobQueue: {
        jobs: {},
        polling: {},
        collapsed: localStorage.getItem('jobQueueCollapsed') === 'true'
    }
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
    historyList: document.getElementById('historyList'),
    scenariosBtn: document.getElementById('scenariosBtn'),
    scenariosModal: document.getElementById('scenariosModal'),
    scenariosList: document.getElementById('scenariosList'),
    editorContent: document.getElementById('editorContent'),
    editorEmptyState: document.getElementById('editorEmptyState')
};

// ===== Drag & Drop Setup =====
function setupDragAndDrop() {
    const dropZone = elements.chatContainer;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = Array.from(dt.files);

    state.attachedFiles.push(...files);
    renderFileAttachments();

    addLogMessage(`📁 ${files.length} Datei(en) hinzugefügt`);

    // 🆕 Trigger smart detection
    if (window.oneClickWorkflows) {
        window.oneClickWorkflows.handleFileDrop(files);
    }
}

// ===== Logging System =====
function addLogMessage(message, type = 'info') {
    const log = {
        message,
        type,
        timestamp: new Date().toISOString()
    };

    state.logs.push(log);
    console.log(`[${type.toUpperCase()}]`, message);

    // Keep only last 100 logs
    if (state.logs.length > 100) {
        state.logs = state.logs.slice(-100);
    }
}

function showLogs() {
    const logsHtml = state.logs.map(log => {
        const time = new Date(log.timestamp).toLocaleTimeString('de-DE');
        const icon = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️'
        }[log.type] || 'ℹ️';

        return `<div class="log-entry log-${log.type}">
            <span class="log-time">${time}</span>
            <span class="log-icon">${icon}</span>
            <span class="log-message">${log.message}</span>
        </div>`;
    }).reverse().join('');

    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h2>📊 Live-Logs</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body" style="max-height: 500px; overflow-y: auto; font-family: monospace; font-size: 12px;">
                ${logsHtml || '<p style="text-align: center; color: var(--text-muted);">Keine Logs verfügbar</p>'}
            </div>
            <div class="modal-footer" style="display: flex; gap: 12px; justify-content: flex-end;">
                <button class="btn-primary" onclick="copyLogsToClipboard()">📋 Alle kopieren</button>
                <button class="btn-secondary" onclick="this.closest('.modal').remove()">Schließen</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

function copyLogsToClipboard() {
    const logsText = state.logs.map(log => {
        const time = new Date(log.timestamp).toLocaleTimeString('de-DE');
        const icon = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️'
        }[log.type] || 'ℹ️';
        return `${time} ${icon} ${log.message}`;
    }).reverse().join('\n');

    navigator.clipboard.writeText(logsText).then(() => {
        // Show success notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10001;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = '✓ Logs in Zwischenablage kopiert!';
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy logs:', err);
        alert('Fehler beim Kopieren der Logs');
    });
}


// ===== API Call with new /api/process endpoint =====
async function processRequest(message, files) {
    addLogMessage(`📨 Sende Request: "${message.substring(0, 50)}..."`);

    const formData = new FormData();
    formData.append('message', message);
    if (state.currentConversationId) {
        formData.append('conversation_id', state.currentConversationId);
    }

    files.forEach((file, index) => {
        formData.append('files', file);
        addLogMessage(`📎 Datei ${index + 1}: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB, ${file.type})`, 'info');
    });

    try {
        const startTime = Date.now();
        addLogMessage(`🚀 Rufe Backend auf: ${CONFIG.apiUrl}/api/process`, 'info');

        const response = await fetch(`${CONFIG.apiUrl}/api/process`, {
            method: 'POST',
            body: formData
        });

        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        addLogMessage(`📡 Response Status: ${response.status} (${duration}s)`, response.ok ? 'success' : 'error');

        const data = await response.json();

        if (!response.ok) {
            addLogMessage(`❌ Fehler: ${data.error}`, 'error');
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        // Log detailed response
        addLogMessage(`✅ Request erfolgreich! (${duration}s)`, 'success');

        if (data.conversation_id) {
            state.currentConversationId = data.conversation_id;
            localStorage.setItem('last_conversation_id', data.conversation_id);
        }

        if (data.job_id) {
            addLogMessage(`🆔 Job-ID: ${data.job_id}`, 'info');
        }

        if (data.intent) {
            addLogMessage(`🎯 Intent: ${data.intent.endpoint} (Confidence: ${(data.intent.confidence * 100).toFixed(0)}%)`, 'info');
            addLogMessage(`💭 Reasoning: ${data.intent.reasoning}`, 'info');
        }

        if (data.params) {
            addLogMessage(`📋 Parameter: ${JSON.stringify(data.params, null, 2)}`, 'info');
        }

        if (data.uploaded_files && data.uploaded_files.length > 0) {
            addLogMessage(`📁 ${data.uploaded_files.length} Datei(en) hochgeladen:`, 'success');
            data.uploaded_files.forEach(f => {
                addLogMessage(`  • ${f.filename} (${f.size_mb}MB) → ${f.url}`, 'info');
            });
        }

        if (data.result) {
            addLogMessage(`📦 Ergebnis erhalten:`, 'success');
            addLogMessage(`${JSON.stringify(data.result, null, 2)}`, 'info');
        }

        return data;

    } catch (error) {
        addLogMessage(`❌ Fehler: ${error.message}`, 'error');
        throw error;
    }
}

// ===== UI Functions =====
function addMessage(role, content, data = null) {
    const message = {
        role,
        content,
        data,
        timestamp: new Date().toISOString()
    };

    state.messages.push(message);
    return renderMessage(message);
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

    // Add data card if present
    if (message.data) {
        const dataCard = createDataCard(message.data);
        contentDiv.appendChild(dataCard);
    }

    contentDiv.appendChild(time);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    elements.messages.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function createDataCard(data) {
    const card = document.createElement('div');
    card.className = 'api-action';

    if (data.intent || data.result) {
        card.innerHTML = `
            <div class="api-action-header">
                <div class="api-action-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <div>
                    <div class="api-action-title">🎯 Intent erkannt</div>
                    <div class="api-action-endpoint">${(data.intent && data.intent.endpoint) ? data.intent.endpoint : 'Ergebnis verfügbar'}</div>
                </div>
            </div>
            <div class="api-action-params">
                <div><strong>Confidence:</strong> ${(data.intent && data.intent.confidence) ? (data.intent.confidence * 100).toFixed(0) + '%' : 'N/A'}</div>
                <div><strong>Reasoning:</strong> ${(data.intent && data.intent.reasoning) ? data.intent.reasoning : 'Direkte Ausführung'}</div>
                ${data.params ? `
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color);">
                        <div><strong>🔧 API Aufruf:</strong></div>
                        <div style="font-family: monospace; font-size: 0.9em; margin-top: 4px;">
                            <span style="color: var(--primary-color); font-weight: 600;">POST</span> ${data.intent.endpoint}
                        </div>
                        <details style="margin-top: 8px;">
                            <summary style="cursor: pointer; color: var(--text-muted); font-size: 0.9em;">Parameter anzeigen</summary>
                            <pre style="margin-top: 8px; font-size: 0.85em;">${JSON.stringify(data.params, null, 2)}</pre>
                        </details>
                    </div>
                ` : ''}
            </div>
            ${data.result ? `
                <div class="api-action-params" style="background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e;">
                    <div><strong>✅ Ergebnis:</strong></div>
                    ${renderResultData(data.result)}
                </div>
            ` : ''}
            ${data.uploaded_files && data.uploaded_files.length > 0 ? `
                <div class="api-action-params">
                    <div><strong>📁 Hochgeladene Dateien:</strong></div>
                    ${data.uploaded_files.map(f => `
                        <div>• ${f.filename} (${f.size_mb}MB) - <a href="${f.url}" target="_blank">Öffnen</a></div>
                    `).join('')}
                </div>
            ` : ''}
        `;
    } else if (data.error) {
        card.innerHTML = `
            <div class="api-action-header" style="background: rgba(239, 68, 68, 0.1);">
                <div class="api-action-icon" style="color: #ef4444;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div>
                    <div class="api-action-title">❌ Fehler</div>
                    <div class="api-action-endpoint">${data.error}</div>
                </div>
            </div>
        `;
    }

    return card;
}

function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

// ===== Event Handlers =====
async function handleSendMessage() {
    const message = elements.userInput.value.trim();
    if (!message && state.attachedFiles.length === 0) return;

    // Hide welcome message
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.style.display = 'none';

    // Add user message
    addMessage('user', message || '📎 Dateien hochgeladen');

    // Clear input
    elements.userInput.value = '';
    elements.sendBtn.disabled = true;

    // Show processing with progress
    const processingMsg = addMessage('assistant', '🤖 Verarbeite Anfrage...');
    const progressDiv = createProgressBar();
    processingMsg.querySelector('.message-content').appendChild(progressDiv);

    try {
        const result = await processRequest(message, state.attachedFiles);

        // Remove processing message
        elements.messages.removeChild(processingMsg);

        if (result.success) {
            // Poll for job status if job_id is returned
            if (result.job_id) {
                await pollJobStatus(result.job_id, result);
            } else {
                addMessage('assistant', '✅ Anfrage erfolgreich verarbeitet!', result);
            }
        } else {
            addMessage('assistant', `❌ Fehler: ${result.error}`, result);
        }

    } catch (error) {
        // Remove processing message
        if (processingMsg.parentNode) {
            elements.messages.removeChild(processingMsg);
        }

        addMessage('assistant', `❌ Fehler bei der Verarbeitung: ${error.message}`, { error: error.message });
    }

    // Clear attached files
    state.attachedFiles = [];
    renderFileAttachments();
}

function createProgressBar() {
    const progressDiv = document.createElement('div');
    progressDiv.className = 'progress-container';
    progressDiv.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
        <div class="progress-text">Starte...</div>
    `;
    return progressDiv;
}

async function pollJobStatus(jobId, initialResult) {
    let lastProgress = 0;
    const maxAttempts = 120; // 2 Minuten max
    let attempts = 0;

    const progressMsg = addMessage('assistant', '⏳ Verarbeite...');
    const progressDiv = createProgressBar();
    progressMsg.querySelector('.message-content').appendChild(progressDiv);

    const interval = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${CONFIG.apiUrl}/api/jobs/${jobId}`);
            const data = await response.json();

            if (data.success && data.job) {
                const job = data.job;

                // Update progress bar
                const progressFill = progressDiv.querySelector('.progress-fill');
                const progressText = progressDiv.querySelector('.progress-text');

                if (progressFill && progressText) {
                    progressFill.style.width = `${job.progress}%`;
                    progressText.textContent = job.message || `${job.progress}%`;
                }

                lastProgress = job.progress;

                // Check if completed
                if (job.status === 'completed') {
                    clearInterval(interval);
                    elements.messages.removeChild(progressMsg);
                    addMessage('assistant', '✅ Anfrage erfolgreich verarbeitet!', {
                        ...initialResult,
                        result: job.result
                    });
                } else if (job.status === 'failed') {
                    clearInterval(interval);
                    elements.messages.removeChild(progressMsg);
                    addMessage('assistant', `❌ Fehler: ${job.message}`, {
                        error: job.message
                    });
                }
            }
        } catch (error) {
            console.error('Poll error:', error);
        }

        // Timeout
        if (attempts >= maxAttempts) {
            clearInterval(interval);
            elements.messages.removeChild(progressMsg);
            addMessage('assistant', '⏱️ Timeout: Request dauert zu lange. Prüfen Sie die Logs.');
        }
    }, 1000); // Poll every second
}

function handleFileAttach() {
    elements.fileInput.click();
}

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    state.attachedFiles.push(...files);
    renderFileAttachments();
    addLogMessage(`📁 ${files.length} Datei(en) ausgewählt`);

    // 🆕 Trigger smart detection
    if (window.oneClickWorkflows) {
        window.oneClickWorkflows.handleFileDrop(files);
    }
}

function removeFile(index) {
    const file = state.attachedFiles[index];
    state.attachedFiles.splice(index, 1);
    renderFileAttachments();
    addLogMessage(`🗑️ Datei entfernt: ${file.name}`);

    // 🆕 Update suggestions panel
    if (window.oneClickWorkflows) {
        if (state.attachedFiles.length > 0) {
            window.oneClickWorkflows.handleFileDrop(state.attachedFiles);
        } else {
            window.oneClickWorkflows.hideSuggestionsPanel();
        }
    }
}

function renderFileAttachments() {
    elements.fileAttachments.innerHTML = '';

    state.attachedFiles.forEach((file, index) => {
        const attachment = document.createElement('div');
        attachment.className = 'file-attachment';

        const icon = getFileIcon(file.type);
        const sizeMB = (file.size / 1024 / 1024).toFixed(2);

        attachment.innerHTML = `
            <span>${icon} ${file.name} (${sizeMB}MB)</span>
            <button class="file-attachment-remove" onclick="removeFile(${index})">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        `;
        elements.fileAttachments.appendChild(attachment);
    });
}

function getFileIcon(type) {
    if (type.startsWith('video/')) return '🎥';
    if (type.startsWith('audio/')) return '🎵';
    if (type.startsWith('image/')) return '🖼️';
    return '📄';
}

// ===== Settings =====
function openSettings() {
    elements.settingsModal.classList.add('active');
    document.getElementById('apiUrl').value = CONFIG.apiUrl;
    document.getElementById('autoExecute').checked = CONFIG.autoExecute;
}

function closeSettings() {
    elements.settingsModal.classList.remove('active');
}

function saveSettings() {
    CONFIG.apiUrl = document.getElementById('apiUrl').value;
    CONFIG.autoExecute = document.getElementById('autoExecute').checked;

    localStorage.setItem('nca_api_url', CONFIG.apiUrl);
    localStorage.setItem('nca_auto_execute', CONFIG.autoExecute);

    addLogMessage(`⚙️ Einstellungen gespeichert`, 'success');
    closeSettings();
}

// ===== History =====
async function openHistory() {
    elements.historyModal.classList.add('active');
    elements.historyList.innerHTML = '<div class="loading-spinner"></div> Lade Verlauf...';

    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/history`);
        const data = await response.json();
        if (data.success) {
            state.history = data.conversations;
            renderHistory();
        }
    } catch (error) {
        addLogMessage(`Fehler beim Laden des Verlaufs: ${error.message}`, 'error');
        elements.historyList.innerHTML = 'Fehler beim Laden.';
    }
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

    state.history.forEach((conv) => {
        const item = document.createElement('div');
        item.className = 'history-item';
        const date = new Date(conv.createdAt).toLocaleString('de-DE');
        item.innerHTML = `
            <div class="history-item-title">${conv.title || 'Ohne Titel'}</div>
            <div class="history-item-time">${date} • ${conv.messages.length} Nachrichten</div>
        `;
        item.onclick = () => loadConversation(conv.id);
        elements.historyList.appendChild(item);
    });
}

async function loadConversation(id) {
    const conv = state.history.find(c => c.id === id);
    if (!conv) return;

    state.currentConversationId = conv.id;
    state.messages = [];
    elements.messages.innerHTML = '';

    // Hide welcome
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.style.display = 'none';

    conv.messages.forEach(msg => {
        addMessage(msg.role, msg.text, msg.data);
    });

    closeHistory();
    addLogMessage(`Chat geladen: ${conv.title}`, 'success');
}

// ===== Scenarios =====
async function openScenarios() {
    elements.scenariosModal.classList.add('active');
    loadScenarios();
}

async function loadScenarios() {
    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/scenarios`);
        const data = await response.json();
        if (data.success) {
            state.allScenarios = data.scenarios;
            renderScenariosList();
            renderScenarioButtons(); // Add buttons to welcome screen
        }
    } catch (error) {
        addLogMessage(`Fehler beim Laden der Szenarien: ${error.message}`, 'error');
    }
}

function renderScenarioButtons() {
    const container = document.querySelector('.example-prompts');
    if (!container) return;

    // Check if we already added the scenarios section
    if (document.getElementById('dynamicScenarios')) return;

    const section = document.createElement('div');
    section.id = 'dynamicScenarios';
    section.innerHTML = '<h3 style="margin-top: 1.5rem; color: var(--secondary);">🚀 Verfügbare Szenarien:</h3>';

    const grid = document.createElement('div');
    grid.style.display = 'flex';
    grid.style.flexWrap = 'wrap';
    grid.style.gap = '10px';
    grid.style.marginTop = '10px';

    Object.keys(state.allScenarios).forEach(id => {
        const s = state.allScenarios[id];
        const btn = document.createElement('button');
        btn.className = 'example-prompt';
        btn.style.borderColor = 'var(--secondary)';
        btn.innerHTML = `✨ ${s.name}`;
        btn.onclick = () => {
            selectScenario(id);
            openScenarios();
        };
        grid.appendChild(btn);
    });

    section.appendChild(grid);
    container.appendChild(section);
}

function renderScenariosList() {
    elements.scenariosList.innerHTML = '';
    Object.keys(state.allScenarios).forEach(id => {
        const s = state.allScenarios[id];
        const item = document.createElement('div');
        item.className = `scenario-item ${state.currentScenarioId === id ? 'active' : ''}`;
        item.innerHTML = `
            <h4>${s.name}</h4>
            <p>${s.description}</p>
        `;
        item.onclick = () => selectScenario(id);
        elements.scenariosList.appendChild(item);
    });
}

function selectScenario(id) {
    state.currentScenarioId = id;
    renderScenariosList();

    const s = state.allScenarios[id];
    elements.editorEmptyState.style.display = 'none';
    elements.editorContent.style.display = 'block';

    document.getElementById('scenarioId').value = id;
    document.getElementById('scenarioName').value = s.name;
    document.getElementById('scenarioDesc').value = s.description;

    // Create copy for editor (removing meta fields if they exist)
    const config = { ...s };
    delete config.name;
    delete config.description;

    document.getElementById('scenarioJson').value = JSON.stringify(config, null, 2);
}

document.getElementById('addScenarioBtn').onclick = () => {
    const id = 'new_scenario_' + Math.floor(Math.random() * 1000);
    state.allScenarios[id] = {
        name: 'Neues Szenario',
        description: 'Beschreibung hier...',
        steps: []
    };
    selectScenario(id);
};

document.getElementById('saveScenarioBtn').onclick = async () => {
    const id = document.getElementById('scenarioId').value;
    const name = document.getElementById('scenarioName').value;
    const desc = document.getElementById('scenarioDesc').value;
    let config;

    try {
        config = JSON.parse(document.getElementById('scenarioJson').value);
    } catch (e) {
        alert('Invalid JSON!');
        return;
    }

    state.allScenarios[id] = {
        name: name,
        description: desc,
        ...config
    };

    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/scenarios/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenarios: state.allScenarios })
        });
        if (response.ok) {
            addLogMessage(`Szenario "${name}" gespeichert`, 'success');
            loadScenarios();
        }
    } catch (error) {
        addLogMessage(`Fehler beim Speichern: ${error.message}`, 'error');
    }
};

document.getElementById('deleteScenarioBtn').onclick = async () => {
    if (!confirm('Sicher?')) return;
    delete state.allScenarios[state.currentScenarioId];
    // Save state
    const response = await fetch(`${CONFIG.apiUrl}/api/scenarios/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenarios: state.allScenarios })
    });
    if (response.ok) {
        state.currentScenarioId = null;
        elements.editorContent.style.display = 'none';
        elements.editorEmptyState.style.display = 'flex';
        loadScenarios();
    }
}

document.getElementById('executeScenarioBtn').onclick = async () => {
    const id = state.currentScenarioId;
    const s = state.allScenarios[id];

    // Prompt for required parameters
    const inputs = {};
    if (s.parameters) {
        for (const p of s.parameters) {
            const val = prompt(`${p.description} (${p.name}):`, p.default || '');
            if (val === null && p.required) return;
            inputs[p.name] = val;
        }
    }

    elements.scenariosModal.classList.remove('active');

    // Start progress
    const processingMsg = addMessage('assistant', `🎬 Starte Szenario: ${s.name}...`);
    const progressDiv = createProgressBar();
    processingMsg.querySelector('.message-content').appendChild(progressDiv);

    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/scenarios/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scenario_id: id,
                inputs: inputs,
                conversation_id: state.currentConversationId
            })
        });
        const data = await response.json();

        elements.messages.removeChild(processingMsg);

        if (data.success) {
            if (data.job_id) {
                await pollJobStatus(data.job_id, data);
            } else {
                addMessage('assistant', `✅ Szenario abgeschlossen!`, { result: data.results });
            }
            if (data.conversation_id) state.currentConversationId = data.conversation_id;
        } else {
            addMessage('assistant', `❌ Fehler: ${data.error}`, { error: data.error });
        }
    } catch (error) {
        elements.messages.removeChild(processingMsg);
        addMessage('assistant', `❌ Fehler: ${error.message}`, { error: error.message });
    }
};

function closeScenarios() {
    elements.scenariosModal.classList.remove('active');
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
    elements.sendBtn.disabled = !elements.userInput.value.trim() && state.attachedFiles.length === 0;

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

elements.scenariosBtn.addEventListener('click', openScenarios);
document.getElementById('closeScenarios').addEventListener('click', closeScenarios);

// Example prompts
document.querySelectorAll('.example-prompt').forEach(btn => {
    btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt;
        if (!prompt) return;

        elements.userInput.value = prompt;
        elements.sendBtn.disabled = false;

        // Auto-send
        handleSendMessage();
    });
});

// Close modals on outside click
elements.settingsModal.addEventListener('click', (e) => {
    if (e.target === elements.settingsModal) closeSettings();
});
elements.historyModal.addEventListener('click', (e) => {
    if (e.target === elements.historyModal) closeHistory();
});
elements.scenariosModal.addEventListener('click', (e) => {
    if (e.target === elements.scenariosModal) closeScenarios();
});

// Docs Logic
const docsBtn = document.getElementById('docsBtn');
const docsModal = document.getElementById('docsModal');
const closeDocs = document.getElementById('closeDocs');
const closeDocsBtn = document.getElementById('closeDocsBtn');
const docsSidebar = document.getElementById('docsSidebar');
const docsContent = document.getElementById('docsContent');

if (docsBtn) {
    docsBtn.addEventListener('click', openDocs);
    closeDocs.addEventListener('click', () => docsModal.style.display = 'none');
    closeDocsBtn.addEventListener('click', () => docsModal.style.display = 'none');
    docsModal.addEventListener('click', (e) => {
        if (e.target === docsModal) docsModal.style.display = 'none';
    });
}

function openDocs() {
    docsModal.style.display = 'flex';
    loadDocsList();
}

async function loadDocsList() {
    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/docs/list`);
        const docs = await response.json();

        docsSidebar.innerHTML = '';
        let currentCategory = '';

        docs.forEach(doc => {
            if (doc.category !== currentCategory) {
                const catHeader = document.createElement('div');
                catHeader.className = 'doc-category';
                catHeader.textContent = doc.category;
                docsSidebar.appendChild(catHeader);
                currentCategory = doc.category;
            }

            const item = document.createElement('div');
            item.className = 'doc-item';
            item.textContent = doc.name;
            item.addEventListener('click', () => loadDocContent(doc.path, item));
            docsSidebar.appendChild(item);
        });
    } catch (error) {
        docsSidebar.innerHTML = `<div style="color:red">Fehler beim Laden: ${error.message}</div>`;
    }
}

async function loadDocContent(path, itemElement) {
    // Active state
    document.querySelectorAll('.doc-item').forEach(el => el.classList.remove('active'));
    if (itemElement) itemElement.classList.add('active');

    docsContent.innerHTML = '<div class="loading-spinner"></div>Lade Inhalt...';

    try {
        const response = await fetch(`${CONFIG.apiUrl}/api/docs/read?path=${encodeURIComponent(path)}`);
        const data = await response.json();

        if (data.content) {
            // Render Markdown
            docsContent.innerHTML = marked.parse(data.content);
        } else {
            docsContent.innerHTML = '<div style="color:red">Kein Inhalt gefunden.</div>';
        }
    } catch (error) {
        docsContent.innerHTML = `<div style="color:red">Fehler beim Laden: ${error.message}</div>`;
    }
}

// Initialize Logs Button
const logsBtn = document.getElementById('logsBtn');
if (logsBtn) {
    logsBtn.addEventListener('click', showLogs);
}

// Initialize Version
const versionInfo = document.getElementById('versionInfo');
if (versionInfo && typeof APP_VERSION !== 'undefined') {
    versionInfo.innerHTML = `v${APP_VERSION.version} <span style="opacity: 0.5">(${APP_VERSION.commit.substring(0, 7)})</span>`;
    versionInfo.title = `Build: ${APP_VERSION.buildTime}`;
}

// Reset to Landing Page
function resetToLandingPage() {
    state.currentConversationId = null;
    state.messages = [];
    state.attachedFiles = [];

    localStorage.removeItem('last_conversation_id');

    // Reset UI
    if (elements.messages) elements.messages.innerHTML = '';
    renderFileAttachments();

    // Show welcome message again if it was hidden
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.style.display = 'block';

    // Clear URL if needed (optional)
    // window.history.pushState({}, '', '/');

    addLogMessage('🏠 Zurück zur Startseite');
}

// Make functions global for onclick handlers
window.removeFile = removeFile;
window.showLogs = showLogs;
window.resetToLandingPage = resetToLandingPage;

// 🆕 Initialize Smart Detection
let smartDetector = null;
let oneClickWorkflows = null;

if (typeof SmartFileDetector !== 'undefined' && typeof OneClickWorkflows !== 'undefined') {
    smartDetector = new SmartFileDetector();
    oneClickWorkflows = new OneClickWorkflows(smartDetector);

    // Make globally available
    window.smartDetector = smartDetector;
    window.oneClickWorkflows = oneClickWorkflows;

    console.log('✅ Smart Detection enabled');
    addLogMessage(`✨ Smart Detection aktiviert!`, 'success');
} else {
    console.warn('⚠️ Smart Detection classes not loaded');
}

// Initialize
setupDragAndDrop();
loadScenarios(); // Auto-load scenarios on start
checkLastConversation(); // Auto-load last conv if exists

// Initialize Job Queue (CRITICAL for job visibility!)
// Job Queue is initialized in job-queue.js now


async function checkLastConversation() {
    if (state.currentConversationId) {
        try {
            const response = await fetch(`${CONFIG.apiUrl}/api/history`);
            const data = await response.json();
            if (data.success) {
                state.history = data.conversations;
                const last = data.conversations.find(c => c.id === state.currentConversationId);
                if (last) {
                    loadConversation(last.id);
                }
            }
        } catch (e) {
            console.error("Failed to load last conversation", e);
        }
    }
}

// Use dynamic version from version.js
if (typeof APP_VERSION !== 'undefined') {
    addLogMessage(`🏗️ Build: ${APP_VERSION.build}`, 'info');
    console.log(`🚀 NCA Toolkit AI Assistant v${APP_VERSION.version} geladen!`);
    console.log(`🏗️  Build: ${APP_VERSION.build} (${APP_VERSION.commit})`);
} else {
    console.warn("⚠️ version.js not loaded");
}

addLogMessage(`🚀 NCA Toolkit AI Assistant geladen!`, 'success');
addLogMessage(`📡 Backend URL: ${CONFIG.apiUrl}`, 'info');

console.log('Backend URL:', CONFIG.apiUrl);
console.log('Drag & Drop: Aktiviert');
console.log('Live-Logs: Aktiviert');


function renderResultData(result) {
    if (!result) return '';

    // Check if Normalizer is loaded
    if (typeof ResultNormalizer === 'undefined') {
        console.error("ResultNormalizer missing! Fallback to JSON stringify");
        return `<pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
    }

    const blocks = ResultNormalizer.normalize(result);
    // Use escapeHtml for raw data
    const rawData = escapeHtml(JSON.stringify(result, null, 2));

    let html = '<div class="result-container" style="display: flex; flex-direction: column; gap: 16px;">';

    if (blocks.length === 0) {
        html += '<div class="text-muted">Keine anzeigbaren Inhalte gefunden.</div>';
    } else {
        blocks.forEach((block, index) => {
            let contentHtml = '';
            const labelStyle = 'font-size: 0.85em; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;';
            const fullUrl = block.url; // URLs are already constructed by Normalizer

            switch (block.type) {
                case 'video':
                    contentHtml = `
                        <div class="media-block video" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                            <div style="${labelStyle}">🎥 ${block.label || 'Video'}</div>
                            <video controls style="width: 100%; max-height: 400px; border-radius: 4px; background: #000;">
                                <source src="${fullUrl}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                            <div style="font-size: 0.8em; margin-top: 8px;">
                                <a href="${fullUrl}" target="_blank" download style="color: var(--primary-color); text-decoration: none;">⬇️ Video herunterladen</a>
                            </div>
                        </div>`;
                    break;

                case 'audio':
                    contentHtml = `
                        <div class="media-block audio" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                            <div style="${labelStyle}">🔊 ${block.label || 'Audio'}</div>
                            <audio controls style="width: 100%; margin-top: 4px;">
                                <source src="${fullUrl}">
                                Your browser does not support the audio element.
                            </audio>
                            <div style="font-size: 0.8em; margin-top: 8px;">
                                <a href="${fullUrl}" target="_blank" download style="color: var(--primary-color); text-decoration: none;">⬇️ Audio herunterladen</a>
                            </div>
                        </div>`;
                    break;

                case 'image':
                    contentHtml = `
                        <div class="media-block image" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                             <div style="${labelStyle}">🖼️ ${block.label || 'Image'}</div>
                             <a href="${fullUrl}" target="_blank">
                                <img src="${fullUrl}" style="max-width: 100%; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);" loading="lazy" />
                             </a>
                             <div style="font-size: 0.8em; margin-top: 8px;">
                                <a href="${fullUrl}" target="_blank" download style="color: var(--primary-color); text-decoration: none;">⬇️ Bild speichern</a>
                            </div>
                        </div>`;
                    break;

                case 'text':
                    // Check if markdown
                    const text = block.content;
                    const isMarkdown = true; // Always assume markdown for now or check
                    const rendered = (typeof marked !== 'undefined') ? marked.parse(text) : escapeHtml(text).replace(/\n/g, '<br>');

                    contentHtml = `
                        <div class="text-block">
                            <div style="${labelStyle}">📝 ${block.label || 'Text Result'}</div>
                            <div class="markdown-body" style="padding: 12px; background: rgba(255, 255, 255, 0.03); border-left: 3px solid var(--primary-color); border-radius: 4px; overflow-x: auto; font-size: 0.95em;">
                                ${rendered}
                            </div>
                        </div>`;
                    break;
            }

            html += contentHtml;
        });
    }

    // Always show raw data collapsed
    html += `
        <details style="margin-top: 16px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px;">
            <summary style="cursor: pointer; color: var(--text-muted); font-size: 0.8em; user-select: none;">🔍 Rohe Daten anzeigen</summary>
            <pre style="font-size: 0.7em; margin-top: 10px; max-height: 200px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px;">${rawData}</pre>
        </details>
    `;

    html += '</div>';
    return html;
}

