/**
 * Progress Tracker
 * Visualizes processing steps in real-time
 */

class ProgressTracker {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.steps = [];
        this.currentStepIndex = -1;
        this.startTime = null;
    }

    start(steps) {
        this.steps = steps.map((step, index) => ({
            id: index,
            title: step.title,
            message: step.message || '',
            status: 'pending', // pending, active, completed, error
            startTime: null,
            endTime: null
        }));
        this.currentStepIndex = -1;
        this.startTime = Date.now();
        this.render();
    }

    nextStep(message = '') {
        // Complete current step
        if (this.currentStepIndex >= 0) {
            this.steps[this.currentStepIndex].status = 'completed';
            this.steps[this.currentStepIndex].endTime = Date.now();
        }

        // Start next step
        this.currentStepIndex++;
        if (this.currentStepIndex < this.steps.length) {
            this.steps[this.currentStepIndex].status = 'active';
            this.steps[this.currentStepIndex].startTime = Date.now();
            if (message) {
                this.steps[this.currentStepIndex].message = message;
            }
        }

        this.render();
    }

    updateStep(message) {
        if (this.currentStepIndex >= 0 && this.currentStepIndex < this.steps.length) {
            this.steps[this.currentStepIndex].message = message;
            this.render();
        }
    }

    error(message) {
        if (this.currentStepIndex >= 0 && this.currentStepIndex < this.steps.length) {
            this.steps[this.currentStepIndex].status = 'error';
            this.steps[this.currentStepIndex].message = message;
            this.steps[this.currentStepIndex].endTime = Date.now();
        }
        this.render();
    }

    complete() {
        // Complete all remaining steps
        for (let i = this.currentStepIndex; i < this.steps.length; i++) {
            if (this.steps[i].status !== 'completed') {
                this.steps[i].status = 'completed';
                this.steps[i].endTime = Date.now();
            }
        }
        this.render();
    }

    getProgress() {
        const completedSteps = this.steps.filter(s => s.status === 'completed').length;
        return Math.round((completedSteps / this.steps.length) * 100);
    }

    getElapsedTime(step) {
        if (!step.startTime) return '';
        const end = step.endTime || Date.now();
        const elapsed = (end - step.startTime) / 1000;
        return `${elapsed.toFixed(1)}s`;
    }

    render() {
        if (!this.container) return;

        const progress = this.getProgress();

        this.container.innerHTML = `
            <div class="progress-tracker">
                <div class="progress-tracker-header">
                    <div class="progress-tracker-title">⚙️ Verarbeitungsschritte</div>
                    <div class="progress-tracker-percentage">${progress}%</div>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>
                <div class="progress-steps">
                    ${this.steps.map(step => this.renderStep(step)).join('')}
                </div>
            </div>
        `;
    }

    renderStep(step) {
        const icon = this.getStepIcon(step.status);
        const timeStr = this.getElapsedTime(step);

        return `
            <div class="progress-step ${step.status}">
                <div class="progress-step-icon">${icon}</div>
                <div class="progress-step-content">
                    <div class="progress-step-title">${step.title}</div>
                    ${step.message ? `<div class="progress-step-message">${step.message}</div>` : ''}
                </div>
                ${timeStr ? `<div class="progress-step-time">${timeStr}</div>` : ''}
            </div>
        `;
    }

    getStepIcon(status) {
        switch (status) {
            case 'pending': return '○';
            case 'active': return '⟳';
            case 'completed': return '✓';
            case 'error': return '✗';
            default: return '○';
        }
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Make it globally available
window.ProgressTracker = ProgressTracker;
