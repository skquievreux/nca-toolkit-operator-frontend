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

    // Start periodic refresh of active jobs only
    setInterval(() => refreshActiveJobs(), 2000);
    // Refresh all jobs once on init
    refreshAllJobs();

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

    // Auto-expand queue if collapsed
    if (state.jobQueue.collapsed) {
        state.jobQueue.collapsed = false;
        const panel = document.getElementById('jobQueuePanel');
        panel?.classList.remove('collapsed');
        localStorage.setItem('jobQueueCollapsed', 'false');
    }

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
        }

        // Update UI for this specific job
        updateJobCard(jobId, job);

    } catch (error) {
        console.error(`Error polling job ${jobId}:`, error);
    }
}

async function refreshActiveJobs() {
    // Get list of ACTIVE jobs only
    try {
        const response = await fetch(`${state.backendUrl}/api/jobs?status=pending,processing`);
        if (response.ok) {
            const data = await response.json();
            const jobs = data.jobs || [];

            // Update local state for these jobs
            jobs.forEach(job => {
                state.jobQueue.jobs[job.id] = job;

                // Ensure polling is active
                if (!state.jobQueue.polling[job.id]) {
                    startJobPolling(job.id);
                }
            });

            // Check for jobs that are no longer in the active list but we think are active
            // This handles cases where a job completed between polls
            Object.values(state.jobQueue.jobs).forEach(job => {
                if ((job.status === 'pending' || job.status === 'processing') &&
                    !jobs.find(j => j.id === job.id)) {
                    // Job is no longer in active list, likely completed/failed
                    // Poll it one last time to update status
                    pollJobStatus(job.id);
                }
            });

            renderJobQueue();
        }
    } catch (error) {
        console.error("❌ Error running refreshActiveJobs:", error);
    }
}

async function refreshAllJobs() {
    // Initial load of all jobs (including history)
    try {
        const response = await fetch(`${state.backendUrl}/api/jobs`);
        if (response.ok) {
            const data = await response.json();
            const jobs = data.jobs || [];

            jobs.forEach(job => {
                state.jobQueue.jobs[job.id] = job;
            });

            renderJobQueue();
        }
    } catch (error) {
        console.error("❌ Error running refreshAllJobs:", error);
    }
}

function renderJobQueue() {
    const jobList = document.getElementById('jobList');
    const badge = document.getElementById('jobCountBadge');

    // Create or get header controls container
    let headerControls = document.getElementById('jobQueueHeaderControls');
    if (!headerControls) {
        const header = document.querySelector('.job-queue-header');
        if (header) {
            headerControls = document.createElement('div');
            headerControls.id = 'jobQueueHeaderControls';
            headerControls.className = 'job-queue-controls';

            // Add bulk delete buttons
            headerControls.innerHTML = `
                <button id="deleteCompletedBtn" class="icon-btn small" title="Alle fertigen löschen">✅🗑️</button>
                <button id="deleteFailedBtn" class="icon-btn small" title="Alle fehlerhaften löschen">❌🗑️</button>
            `;
            // Insert BEFORE the toggle button so only toggle button is at the far right
            const toggleBtn = header.querySelector('#toggleQueueBtn');
            if (toggleBtn) {
                header.insertBefore(headerControls, toggleBtn);
            } else {
                header.appendChild(headerControls);
            }

            // Attach listeners
            document.getElementById('deleteCompletedBtn')?.addEventListener('click', () => deleteJobsBulk('completed'));
            document.getElementById('deleteFailedBtn')?.addEventListener('click', () => deleteJobsBulk('failed'));
        }
    }

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
                <p>Keine Jobs</p>
            </div>
        `;
        return;
    }

    jobList.innerHTML = jobs.map(job => createJobCardHTML(job)).join('');

    // Attach event listeners
    jobs.forEach(job => {
        const viewBtn = document.getElementById(`view-job-${job.id}`);
        // Cancel button for active jobs
        const cancelBtn = document.getElementById(`cancel-job-${job.id}`);
        // Delete button for completed/failed jobs
        const deleteBtn = document.getElementById(`delete-job-${job.id}`);

        viewBtn?.addEventListener('click', () => viewJobResult(job.id));
        cancelBtn?.addEventListener('click', () => cancelJob(job.id));
        deleteBtn?.addEventListener('click', () => deleteJob(job.id));
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
                    <button class="job-action-btn" id="delete-job-${job.id}" title="Löschen">
                        🗑️
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
                    <button class="job-action-btn" id="delete-job-${job.id}" title="Löschen">
                        🗑️
                    </button>
                ` : ''}
            </div>
            
            <div class="job-timestamp">${timeAgo}</div>
        </div>
    `;
}

function updateJobCard(jobId, job) {
    // Re-render full list if status changed to enable different buttons
    // Or simpler: just replace outer HTML of the specific card
    const oldCard = document.querySelector(`.job-card[data-job-id="${jobId}"]`);
    if (oldCard) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = createJobCardHTML(job);
        const newCard = tempDiv.firstElementChild;
        oldCard.replaceWith(newCard);

        // Re-attach listeners for this card
        const viewBtn = document.getElementById(`view-job-${job.id}`);
        const cancelBtn = document.getElementById(`cancel-job-${job.id}`);
        const deleteBtn = document.getElementById(`delete-job-${job.id}`);

        viewBtn?.addEventListener('click', () => viewJobResult(job.id));
        cancelBtn?.addEventListener('click', () => cancelJob(job.id));
        deleteBtn?.addEventListener('click', () => deleteJob(job.id));
    } else {
        renderJobQueue();
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

async function cancelJob(jobId) {
    // Treat cancel as delete for now, or just stop polling
    stopJobPolling(jobId);
    // Optionally call backend delete
    await deleteJob(jobId);
}

async function deleteJob(jobId) {
    if (!confirm('Job wirklich löschen?')) return;

    try {
        const response = await fetch(`${state.backendUrl}/api/jobs/${jobId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            stopJobPolling(jobId);
            delete state.jobQueue.jobs[jobId];
            renderJobQueue();
            console.log(`🗑️ Job deleted: ${jobId}`);
        } else {
            console.error('Failed to delete job');
        }
    } catch (e) {
        console.error('Error deleting job:', e);
    }
}

function formatTimeAgo(timestamp) {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);

    if (seconds < 60) return 'Gerade eben';
    if (seconds < 3600) return `vor ${Math.floor(seconds / 60)} Min`;
    if (seconds < 86400) return `vor ${Math.floor(seconds / 3600)} Std`;
    return `vor ${Math.floor(seconds / 86400)} Tagen`;
}

async function deleteJobsBulk(status) {
    const confirmMsg = status === 'completed'
        ? 'Alle fertigen Jobs löschen?'
        : 'Alle fehlerhaften Jobs löschen?';

    if (!confirm(confirmMsg)) return;

    try {
        const response = await fetch(`${state.backendUrl}/api/jobs?status=${status}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const data = await response.json();
            console.log(`🗑️ Deleted ${data.count} ${status} jobs`);

            // Clear from local state
            Object.keys(state.jobQueue.jobs).forEach(jobId => {
                if (state.jobQueue.jobs[jobId].status === status) {
                    stopJobPolling(jobId);
                    delete state.jobQueue.jobs[jobId];
                }
            });

            renderJobQueue();
        } else {
            console.error('Failed to delete jobs');
        }
    } catch (e) {
        console.error('Error deleting jobs:', e);
    }
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
