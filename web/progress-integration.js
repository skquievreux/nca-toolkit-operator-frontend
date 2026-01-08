/**
 * Enhanced Progress Integration with Job Polling
 * Integrates progress tracking into the main flow
 */

let currentProgressTracker = null;
let currentProgressContainer = null;

// Poll job status until complete
async function pollJobStatus(jobId, initialData) {
    const maxAttempts = 120; // 10 minutes max (120 * 5 seconds)
    let attempts = 0;

    addLogMessage(`🔄 Polling Job Status: ${jobId}`, 'info');

    while (attempts < maxAttempts) {
        try {
            const response = await fetch(`${CONFIG.apiUrl}/api/jobs/${jobId}`);
            const data = await response.json();

            // Critical Fix: Merge initial intent validation into polling data
            // The polling result often lacks the 'intent' field which createDataCard needs
            if (initialData && initialData.intent && !data.intent) {
                data.intent = initialData.intent;
            }

            if (currentProgressTracker) {
                // Update progress based on job status
                if (data.progress) {
                    const progressPercent = data.progress;
                    if (progressPercent >= 75) {
                        currentProgressTracker.nextStep(data.message || 'Fast fertig...');
                    } else if (progressPercent >= 50) {
                        currentProgressTracker.updateStep(data.message || 'Verarbeitung läuft...');
                    }
                }

                if (data.message) {
                    currentProgressTracker.updateStep(data.message);
                }
            }

            if (data.status === 'completed') {
                addLogMessage(`✅ Job abgeschlossen!`, 'success');

                if (currentProgressTracker) {
                    currentProgressTracker.complete();
                    // Remove tracker after delay, but UI update is immediate
                    setTimeout(() => {
                        if (currentProgressContainer && currentProgressContainer.parentNode) {
                            currentProgressContainer.remove();
                        }
                        currentProgressTracker = null;
                    }, 1000);
                }

                return data;
            }

            if (data.status === 'failed') {
                addLogMessage(`❌ Job fehlgeschlagen: ${data.error}`, 'error');

                if (currentProgressTracker) {
                    currentProgressTracker.error(data.error || 'Job fehlgeschlagen');
                }

                throw new Error(data.error || 'Job failed');
            }

            // Wait 5 seconds before next poll
            await new Sleep(5000);
            attempts++;

        } catch (error) {
            addLogMessage(`⚠️ Polling error: ${error.message}`, 'error');

            if (attempts >= 3) {
                throw error;
            }

            await new Sleep(5000);
            attempts++;
        }
    }

    throw new Error('Job timeout - max polling attempts reached');
}

function Sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Override handleSendMessage to add progress tracking
if (typeof window.originalHandleSendMessage === 'undefined') {
    window.originalHandleSendMessage = handleSendMessage;

    window.handleSendMessage = async function () {
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

        // Create progress tracker
        currentProgressContainer = document.createElement('div');
        currentProgressContainer.id = 'current-progress';
        elements.messages.appendChild(currentProgressContainer);

        currentProgressTracker = new ProgressTracker('current-progress');
        currentProgressTracker.start([
            { title: '📝 Anfrage vorbereiten', message: 'Dateien werden hochgeladen...' },
            { title: '🤖 Intent erkennen', message: 'Analysiere Ihre Anfrage...' },
            { title: '🔄 Verarbeitung', message: 'Führe Aktion aus...' },
            { title: '✅ Fertig', message: 'Ergebnis wird angezeigt...' }
        ]);

        currentProgressTracker.nextStep('Bereite Anfrage vor...');

        try {
            const result = await processRequest(message, state.attachedFiles);

            if (result.success) {
                currentProgressTracker.nextStep('Intent erkannt');

                // Poll for job status ONLY if job_id is returned AND no result yet
                if (result.job_id && !result.result) {
                    currentProgressTracker.nextStep('Verarbeite...');
                    const finalResult = await pollJobStatus(result.job_id, result);

                    // Display result in chat
                    if (finalResult && finalResult.result) {
                        addMessage('assistant', '✅ Anfrage erfolgreich verarbeitet!', finalResult);
                    } else if (finalResult) {
                        addMessage('assistant', '✅ Job abgeschlossen!', finalResult);
                    } else {
                        addMessage('assistant', '✅ Verarbeitung abgeschlossen!', result);
                    }
                } else {
                    currentProgressTracker.complete();
                    addMessage('assistant', '✅ Anfrage erfolgreich verarbeitet!', result);

                    setTimeout(() => {
                        if (currentProgressContainer && currentProgressContainer.parentNode) {
                            currentProgressContainer.remove();
                        }
                        currentProgressTracker = null;
                    }, 2000);
                }
            } else {
                if (currentProgressTracker) {
                    currentProgressTracker.error(result.error || 'Fehler');
                }
                addMessage('assistant', `❌ Fehler: ${result.error}`, result);
            }

        } catch (error) {
            if (currentProgressTracker) {
                currentProgressTracker.error(error.message);
            }
            addMessage('assistant', `❌ Fehler bei der Verarbeitung: ${error.message}`, { error: error.message });
        }

        // Clear attached files
        state.attachedFiles = [];
        renderFileAttachments();
    };
}

// Make pollJobStatus globally available
window.pollJobStatus = pollJobStatus;
