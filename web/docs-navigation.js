/**
 * Documentation Navigation
 * Handles smooth scrolling and active section highlighting
 */

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.docs-nav a');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);

            if (target) {
                // Smooth scroll to target
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update active state
                navLinks.forEach(a => a.classList.remove('active'));
                link.classList.add('active');

                // Update URL without page reload
                history.pushState(null, '', `#${targetId}`);
            }
        });
    });

    // Active section highlighting on scroll
    const sections = document.querySelectorAll('.docs-content section, .endpoint-card');

    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                if (id) {
                    // Update active nav link
                    navLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href === `#${id}`) {
                            navLinks.forEach(a => a.classList.remove('active'));
                            link.classList.add('active');
                        }
                    });
                }
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        if (section.id) {
            observer.observe(section);
        }
    });

    // Handle initial hash in URL
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        const target = document.getElementById(targetId);

        if (target) {
            setTimeout(() => {
                target.scrollIntoView({ behavior: 'smooth' });

                navLinks.forEach(link => {
                    if (link.getAttribute('href') === `#${targetId}`) {
                        link.classList.add('active');
                    }
                });
            }, 100);
        }
    }
});

// Example command handler
function useExample(command) {
    localStorage.setItem('nca_example_command', command);

    // Show feedback
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary-color);
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = '✓ Befehl übernommen! Weiterleitung...';
    document.body.appendChild(notification);

    // Redirect to main page
    setTimeout(() => {
        window.location.href = '/';
    }, 800);
}

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
