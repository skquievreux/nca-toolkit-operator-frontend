/**
 * One-Click Workflows
 * Enables instant execution of suggested actions without typing
 *
 * @version 1.0.0
 * @author NCA Toolkit Team
 */

class OneClickWorkflows {
    constructor(smartDetector) {
        this.detector = smartDetector;
        this.currentAnalysis = null;
        this.panelVisible = false;
        console.log('⚡ OneClickWorkflows initialized');
    }

    /**
     * Handle file drop/select and show suggestions
     * @param {File[]} files - Array of File objects
     */
    async handleFileDrop(files) {
        if (!files || files.length === 0) {
            this.hideSuggestionsPanel();
            return;
        }

        // Show loading state
        this.showLoadingState(files.length);

        try {
            // Analyze files
            const startTime = Date.now();
            this.currentAnalysis = await this.detector.analyzeFiles(files);
            const duration = Date.now() - startTime;

            console.log(`⚡ Analysis completed in ${duration}ms`);

            // Render suggestions panel
            this.renderSuggestions(this.currentAnalysis);

        } catch (error) {
            console.error('❌ Error analyzing files:', error);
            this.showError('Fehler bei der Dateianalyse: ' + error.message);
        }
    }

    /**
     * Show loading state
     * @param {number} fileCount - Number of files being analyzed
     */
    showLoadingState(fileCount) {
        const panel = document.getElementById('suggestionsPanel');
        if (!panel) {
            console.warn('Suggestions panel not found in DOM');
            return;
        }

        panel.innerHTML = `
            <div class="suggestions-loading">
                <div class="loading-spinner"></div>
                <span>Analysiere ${fileCount} Datei${fileCount > 1 ? 'en' : ''}...</span>
            </div>
        `;
        panel.style.display = 'block';
        this.panelVisible = true;
    }

    /**
     * Render suggestions panel
     * @param {Object} analysis - Analysis result
     */
    renderSuggestions(analysis) {
        const panel = document.getElementById('suggestionsPanel');
        if (!panel) {
            console.warn('Suggestions panel not found in DOM');
            return;
        }

        // File summary
        const fileSummaryHtml = this.renderFileSummary(analysis.files);

        // Warnings
        const warningsHtml = analysis.warnings.length > 0
            ? this.renderWarnings(analysis.warnings)
            : '';

        // Primary suggestion (highest priority)
        const primaryHtml = analysis.suggestions.length > 0
            ? this.renderPrimarySuggestion(analysis.suggestions[0])
            : this.renderNoSuggestions();

        // Secondary suggestions (next 3-5)
        const secondaryHtml = analysis.suggestions.length > 1
            ? this.renderSecondarySuggestions(analysis.suggestions.slice(1, 5))
            : '';

        panel.innerHTML = `
            ${fileSummaryHtml}
            ${warningsHtml}
            ${primaryHtml}
            ${secondaryHtml}
        `;

        panel.style.display = 'block';
        this.panelVisible = true;
    }

    /**
     * Render file summary header
     * @param {Object[]} files - Analyzed files
     * @returns {string} HTML
     */
    renderFileSummary(files) {
        const items = files.map(f => {
            const icon = this.getFileIcon(f.category);
            const sizeMB = (f.size / 1024 / 1024).toFixed(1);
            const meta = f.metadata
                ? `${f.metadata.resolution || ''} ${this.formatDuration(f.metadata.duration)}`
                : '';

            return `
                <div class="file-summary-item">
                    <span class="file-icon">${icon}</span>
                    <span class="file-name">${this.escapeHtml(f.name)}</span>
                    <span class="file-meta">${meta ? `(${meta}, ${sizeMB}MB)` : `(${sizeMB}MB)`}</span>
                </div>
            `;
        }).join('');

        return `
            <div class="suggestions-header">
                <div class="suggestions-title">
                    <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <span>${files.length} Datei${files.length > 1 ? 'en' : ''} hochgeladen</span>
                </div>
                <button class="btn-icon btn-clear-files" onclick="window.oneClickWorkflows.clearAllFiles()" title="Alle entfernen">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="file-summary-list">
                ${items}
            </div>
        `;
    }

    /**
     * Render warnings section
     * @param {Object[]} warnings - Warnings array
     * @returns {string} HTML
     */
    renderWarnings(warnings) {
        const items = warnings.map(w => {
            const severityClass = w.severity === 'error' ? 'error' : 'warning';
            const icon = w.severity === 'error' ? '❌' : '⚠️';

            return `
                <div class="warning-item ${severityClass}">
                    <span class="warning-icon">${icon}</span>
                    <div class="warning-content">
                        <div class="warning-message">${this.escapeHtml(w.message)}</div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="suggestions-warnings">
                ${items}
            </div>
        `;
    }

    /**
     * Render primary suggestion
     * @param {Object} suggestion - Suggestion object
     * @returns {string} HTML
     */
    renderPrimarySuggestion(suggestion) {
        const confidenceBadge = this.getConfidenceBadge(suggestion.confidence);
        const compatibleBadge = suggestion.compatible === false
            ? '<span class="badge badge-warning">⚠️ Inkompatibel</span>'
            : '';

        return `
            <div class="primary-suggestion">
                <div class="suggestion-header">
                    <span class="suggestion-icon">🎯</span>
                    <h3>Empfohlene Aktion</h3>
                </div>
                <div class="suggestion-card primary" data-suggestion-id="0">
                    <div class="suggestion-card-header">
                        <div class="suggestion-icon-large">${suggestion.icon}</div>
                        <div class="suggestion-card-info">
                            <div class="suggestion-title">${this.escapeHtml(suggestion.title)}</div>
                            <div class="suggestion-meta">
                                ${confidenceBadge}
                                ${compatibleBadge}
                            </div>
                        </div>
                    </div>
                    <div class="suggestion-description">${this.escapeHtml(suggestion.description)}</div>
                    ${suggestion.reason ? `<div class="suggestion-reason">ℹ️ ${this.escapeHtml(suggestion.reason)}</div>` : ''}
                    ${suggestion.warning ? `<div class="suggestion-warning">${this.escapeHtml(suggestion.warning)}</div>` : ''}
                    <div class="suggestion-actions">
                        <button class="btn-execute" onclick="window.oneClickWorkflows.executeOneClick(0)">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <polygon points="5 3 19 12 5 21 5 3"></polygon>
                            </svg>
                            <span>Jetzt ausführen</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render secondary suggestions
     * @param {Object[]} suggestions - Suggestions array
     * @returns {string} HTML
     */
    renderSecondarySuggestions(suggestions) {
        const items = suggestions.map((s, idx) => {
            return `
                <div class="suggestion-item" onclick="window.oneClickWorkflows.executeOneClick(${idx + 1})">
                    <span class="suggestion-item-icon">${s.icon}</span>
                    <div class="suggestion-item-content">
                        <div class="suggestion-item-title">${this.escapeHtml(s.title)}</div>
                        <div class="suggestion-item-desc">${this.escapeHtml(s.description)}</div>
                    </div>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </div>
            `;
        }).join('');

        return `
            <div class="secondary-suggestions">
                <h4>Weitere Aktionen:</h4>
                <div class="suggestion-list">
                    ${items}
                </div>
            </div>
        `;
    }

    /**
     * Render no suggestions message
     * @returns {string} HTML
     */
    renderNoSuggestions() {
        return `
            <div class="no-suggestions">
                <div class="no-suggestions-icon">💡</div>
                <h3>Keine automatischen Vorschläge</h3>
                <p>Beschreiben Sie im Chat, was Sie mit den Dateien tun möchten.</p>
            </div>
        `;
    }

    /**
     * Execute one-click action
     * @param {number} suggestionIndex - Index of suggestion in array
     */
    async executeOneClick(suggestionIndex) {
        if (!this.currentAnalysis || !this.currentAnalysis.suggestions[suggestionIndex]) {
            console.error('❌ Invalid suggestion index:', suggestionIndex);
            return;
        }

        const suggestion = this.currentAnalysis.suggestions[suggestionIndex];

        console.log(`⚡ Executing one-click: ${suggestion.title}`);
        addLogMessage(`⚡ One-Click: ${suggestion.title}`, 'info');

        // Hide suggestions panel
        this.hideSuggestionsPanel();

        // Build message for display
        const message = `${suggestion.icon} ${suggestion.title}`;

        // Add user message
        addMessage('user', message);

        // Show processing message
        const processingMsg = addMessage('assistant', '🤖 Verarbeite Anfrage...');
        const progressDiv = createProgressBar();
        processingMsg.querySelector('.message-content').appendChild(progressDiv);

        try {
            // Get the files for this suggestion
            const files = suggestion.files.map(f => f.file);

            // Call backend
            const result = await processRequest(message, files);

            // Remove processing message
            if (processingMsg.parentNode) {
                elements.messages.removeChild(processingMsg);
            }

            // Show result
            if (result.success) {
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
            addLogMessage(`❌ One-Click failed: ${error.message}`, 'error');
        }
    }

    /**
     * Clear all files
     */
    clearAllFiles() {
        state.attachedFiles = [];
        renderFileAttachments();
        this.hideSuggestionsPanel();
        addLogMessage('🗑️ Alle Dateien entfernt', 'info');
    }

    /**
     * Hide suggestions panel
     */
    hideSuggestionsPanel() {
        const panel = document.getElementById('suggestionsPanel');
        if (panel) {
            panel.style.display = 'none';
            this.panelVisible = false;
        }
        this.currentAnalysis = null;
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        const panel = document.getElementById('suggestionsPanel');
        if (!panel) return;

        panel.innerHTML = `
            <div class="suggestions-error">
                <div class="error-icon">❌</div>
                <div class="error-message">${this.escapeHtml(message)}</div>
            </div>
        `;
        panel.style.display = 'block';
        this.panelVisible = true;
    }

    /**
     * Get file icon based on category
     * @param {string} category - File category
     * @returns {string} Emoji icon
     */
    getFileIcon(category) {
        const icons = {
            'video': '🎥',
            'audio': '🎵',
            'image': '🖼️',
            'subtitle': '📝',
            'other': '📄'
        };
        return icons[category] || '📄';
    }

    /**
     * Get confidence badge HTML
     * @param {number} confidence - Confidence score (0-1)
     * @returns {string} HTML
     */
    getConfidenceBadge(confidence) {
        const percent = Math.round(confidence * 100);
        let className = 'high';

        if (confidence < 0.7) className = 'low';
        else if (confidence < 0.85) className = 'medium';

        return `<span class="confidence-badge ${className}">
            Confidence: ${percent}%
        </span>`;
    }

    /**
     * Format duration in seconds to MM:SS
     * @param {number} seconds - Duration
     * @returns {string} Formatted duration
     */
    formatDuration(seconds) {
        if (!seconds || isNaN(seconds)) return '';

        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} str - String to escape
     * @returns {string} Escaped string
     */
    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

// Make globally available
if (typeof window !== 'undefined') {
    window.OneClickWorkflows = OneClickWorkflows;
    console.log('✅ OneClickWorkflows class loaded');
}
