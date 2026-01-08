// Wait for DOM and app.js to be ready
window.addEventListener('DOMContentLoaded', () => {
    // Wait a bit more for app.js to initialize elements
    setTimeout(() => {
        // Check for example command from docs page
        const exampleCommand = localStorage.getItem('nca_example_command');
        if (exampleCommand && typeof elements !== 'undefined') {
            localStorage.removeItem('nca_example_command');
            elements.userInput.value = exampleCommand;
            elements.sendBtn.disabled = false;
            addLogMessage(`📋 Beispiel-Befehl übernommen: "${exampleCommand}"`, 'success');

            // Auto-resize textarea
            elements.userInput.style.height = 'auto';
            elements.userInput.style.height = elements.userInput.scrollHeight + 'px';
        }
    }, 100);
});
