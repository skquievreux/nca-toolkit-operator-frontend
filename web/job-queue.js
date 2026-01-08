// Job Queue Management
// NOTE: state.jobQueue is already defined in app.js
// We just add functions to manage it here

console.log('🔧 job-queue.js loading...');

// Job Queue Functions
function initJobQueue() {
    const toggleBtn = document.getElementById('toggleQueueBtn');
    const panel = document.getElementById('jobQueuePanel');

    // Toggle queue panel
    toggleBtn?.addEventListener('click', () => {
        state.jobQueue.collapsed = !state.jobQueue.collapsed;
        panel?.classList.toggle('collapsed', state.jobQueue.collapsed);

        // Save preference
        localStorage.setItem('jobQueueCollapsed', state.jobQueue.collapsed);
    });

    // Restore collapsed state from localStorage
    const savedCollapsed = localStorage.getItem('jobQueueCollapsed') === 'true';
    if (savedCollapsed) {
        state.jobQueue.collapsed = true;
        panel?.classList.add('collapsed');
    }

    // Start periodic refresh of all active jobs
    setInterval(() => refreshAllJobs(), 2000);

    console.log('✅ Job Queue initialized');
}

function addJobToQueue(jobId, jobData) {
    // Add to local state
    state.jobQueue.jobs[jobId] = {
        ...(jobData || {}),
        id: jobId,
        status: jobData?.status || 'pending',
        created_at: jobData?.created_at || Date.now() / 1000
    };

    // Start polling this job
    startJobPolling(jobId);

    // Update UI
    renderJobQueue();

    console.log(`📋 Job added to queue: ${jobId}`);
}

function startJobPolling(jobId) {
    // Don't poll if already polling
    if (state.jobQueue.polling[jobId]) return;

    // Poll immediately, then every 2 seconds
    pollJobStatus(jobId);

    state.jobQueue.polling[jobId] = setInterval(() => {
        pollJobStatus(jobId);
    }, 2000);
}

function stopJobPolling(jobId) {
    if (state.jobQueue.polling[jobId]) {
        clearInterval(state.jobQueue.polling[jobId]);
        delete state.jobQueue.polling[jobId];
    }
}

async function pollJobStatus(jobId) {
    try {
        const response = await fetch(`${state.backendUrl}/api/jobs/${jobId}`);
        if (!response.ok) {
            // Job not found or error - stop polling
            if (response.status === 404) {
                stopJobPolling(jobId);
                delete state.jobQueue.jobs[jobId];
                renderJobQueue();
            }
            return;
        }

        const job = await response.json();

        // Update local state
        state.jobQueue.jobs[jobId] = job;

        // Stop polling if job complete or failed
        if (job.status === 'completed' || job.status === 'failed') {
            stopJobPolling(jobId);

            // Auto-remove completed jobs after 5 minutes
            setTimeout(() => {
                delete state.jobQueue.jobs[jobId];
                renderJobQueue();
            }, 5 * 60 * 1000);
        }

        // Update UI for this specific job
        updateJobCard(jobId, job);

    } catch (error) {
        console.error(`Error polling job ${jobId}:`, error);
    }
}

async function refreshAllJobs() {
    // Get list of active jobs from backend
    try {
        const response = await fetch(`${state.backendUrl}/api/jobs`);
        if (response.ok) {
            const data = await response.json();
            const jobs = data.jobs || [];

            console.log(`📋 Loaded ${jobs.length} jobs from backend`);

            // CRITICAL FIX: Show ALL jobs but only poll ACTIVE ones
            // This prevents ERR_INSUFFICIENT_RESOURCES from polling 100+ completed jobs
            jobs.forEach(job => {
                // Add job to local state for display
                state.jobQueue.jobs[job.id] = job;

                // Only start polling for ACTIVE jobs (not completed/failed)
                if (job.status === 'processing' || job.status === 'pending') {
                    if (!state.jobQueue.polling[job.id]) {
                        startJobPolling(job.id);
                    }
                } else {
                    // Stop polling for completed/failed jobs (if it was running)
                    stopJobPolling(job.id);
                }
            });

            console.log(`📋 Total jobs in state: ${Object.keys(state.jobQueue.jobs).length}`);

            // Update UI to show all jobs
            renderJobQueue();
        } else {
            console.error(`❌ API returned ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error("❌ Error running refreshAllJobs:", error);
    }
}

function renderJobQueue() {
    const jobList = document.getElementById('jobList');
    const badge = document.getElementById('jobCountBadge');

    if (!jobList) return;

    // Get jobs sorted by creation time (newest first)
    const jobs = Object.values(state.jobQueue.jobs).sort((a, b) =>
        (b.created_at || 0) - (a.created_at || 0)
    );

    // Update badge count
    const activeCount = jobs.filter(j => j.status === 'processing' || j.status === 'pending').length;
    if (badge) {
        badge.textContent = activeCount;
        badge.style.display = activeCount > 0 ? 'inline-flex' : 'none';
    }

    // Render jobs
    if (jobs.length === 0) {
        jobList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                <p>Keine aktiven Jobs</p>
                <p style="font-size: 0.85rem; margin-top: 0.5rem;">
                    Jobs erscheinen hier, wenn Sie eine Aufgabe starten
                </p>
            </div>
        `;
        return;
    }

    jobList.innerHTML = jobs.map(job => createJobCardHTML(job)).join('');

    // Attach event listeners
    jobs.forEach(job => {
        const viewBtn = document.getElementById(`view-job-${job.id}`);
        const cancelBtn = document.getElementById(`cancel-job-${job.id}`);

        viewBtn?.addEventListener('click', () => viewJobResult(job.id));
        cancelBtn?.addEventListener('click', () => cancelJob(job.id));
    });
}

function createJobCardHTML(job) {
    const status = job.status || 'pending';
    const progress = job.progress || 0;
    const title = job.title || job.request_summary || 'Processing...';
    const message = job.message || '';

    // Format timestamp
    const timeAgo = job.created_at ? formatTimeAgo(job.created_at) : 'Just now';

    // Status badge text
    const statusText = {
        'pending': 'Wartend',
        'processing': 'Läuft',
        'completed': 'Fertig',
        'failed': 'Fehler'
    }[status] || status;

    return `
        <div class="job-card status-${status}" data-job-id="${job.id}">
            <div class="job-card-header">
                <div class="job-title">${escapeHtml(title)}</div>
                <span class="job-status-badge ${status}">${statusText}</span>
            </div>
            
            ${job.request_summary ? `
                <div class="job-details">${escapeHtml(job.request_summary)}</div>
            ` : ''}
            
            ${status === 'processing' || status === 'pending' ? `
                <div class="job-progress">
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${progress}%"></div>
                    </div>
                    <div class="progress-text">
                        ${status === 'processing' ? '<span class="job-spinner"></span>' : ''}
                        ${progress}% - ${escapeHtml(message)}
                    </div>
                </div>
            ` : ''}
            
            <div class="job-actions">
                ${status === 'completed' ? `
                    <button class="job-action-btn primary" id="view-job-${job.id}">
                        Ergebnis anzeigen
                    </button>
                ` : ''}
                ${status === 'processing' || status === 'pending' ? `
                    <button class="job-action-btn" id="cancel-job-${job.id}">
                        Abbrechen
                    </button>
                ` : ''}
                ${status === 'failed' ? `
                    <button class="job-action-btn" id="view-job-${job.id}">
                        Fehler anzeigen
                    </button>
                ` : ''}
            </div>
            
            <div class="job-timestamp">${timeAgo}</div>
        </div>
    `;
}

function updateJobCard(jobId, job) {
    const card = document.querySelector(`.job-card[data-job-id="${jobId}"]`);
    if (!card) {
        // Job card doesn't exist yet, re-render full list
        renderJobQueue();
        return;
    }

    // Update status class
    card.className = `job-card status-${job.status}`;

    // Update status badge
    const badge = card.querySelector('.job-status-badge');
    if (badge) {
        const statusText = {
            'pending': 'Wartend',
            'processing': 'Läuft',
            'completed': 'Fertig',
            'failed': 'Fehler'
        }[job.status] || job.status;

        badge.className = `job-status-badge ${job.status}`;
        badge.textContent = statusText;
    }

    // Update progress bar
    const progressBar = card.querySelector('.progress-bar');
    const progressText = card.querySelector('.progress-text');

    if (progressBar) {
        progressBar.style.width = `${job.progress || 0}%`;
    }

    if (progressText) {
        const spinner = job.status === 'processing' ? '<span class="job-spinner"></span>' : '';
        progressText.innerHTML = `${spinner}${job.progress || 0}% - ${escapeHtml(job.message || '')}`;
    }

    // Update badge count
    const activeCount = Object.values(state.jobQueue.jobs).filter(
        j => j.status === 'processing' || j.status === 'pending'
    ).length;

    const countBadge = document.getElementById('jobCountBadge');
    if (countBadge) {
        countBadge.textContent = activeCount;
        countBadge.style.display = activeCount > 0 ? 'inline-flex' : 'none';
    }
}

function viewJobResult(jobId) {
    const job = state.jobQueue.jobs[jobId];
    if (!job) return;

    console.log('📊 Job result:', job);

    // If job has result OR explicit URLs, display it in chat
    // Merge job URLs into result for display
    let displayResult = job.result || {};

    // Sometimes URLs are at top level or specific fields
    if (job.url) displayResult.url = job.url;
    if (job.image_url) displayResult.image_url = job.image_url;
    if (job.video_url) displayResult.video_url = job.video_url;
    if (job.audio_url) displayResult.audio_url = job.audio_url;
    if (job.output_url) displayResult.output_url = job.output_url;

    if (Object.keys(displayResult).length > 0) {
        // Create a formatted result object that addMessage can handle
        const formattedData = {
            intent: {
                endpoint: job.endpoint || 'Job Result',
                confidence: 1.0,
                reasoning: job.title || 'Job completed'
            },
            result: displayResult
        };

        addMessage('assistant', `✅ ${job.title || 'Job Result'}`, formattedData);

        // Scroll to bottom
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    } else if (job.status === 'failed') {
        addMessage('assistant', `❌ Job Failed: ${job.statusMessage || 'Unknown error'}`);
    } else {
        addMessage('assistant', `⏳ Job is still ${job.status}...`);
    }
}

function cancelJob(jobId) {
    // For now, just remove from local state
    // TODO: Add backend endpoint to actually cancel job
    stopJobPolling(jobId);
    delete state.jobQueue.jobs[jobId];
    renderJobQueue();

    console.log(`🛑 Job cancelled: ${jobId}`);
}

function formatTimeAgo(timestamp) {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);

    if (seconds < 60) return 'Gerade eben';
    if (seconds < 3600) return `vor ${Math.floor(seconds / 60)} Min`;
    if (seconds < 86400) return `vor ${Math.floor(seconds / 3600)} Std`;
    return `vor ${Math.floor(seconds / 86400)} Tagen`;
}

// Helper function for HTML escaping
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-initialize when loaded (since app.js is already loaded)
console.log('🚀 initializing Job Queue...');
initJobQueue();
