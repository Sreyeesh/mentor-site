document.addEventListener('DOMContentLoaded', function() {

    const initScrollReveal = () => {
        const revealElements = Array.from(document.querySelectorAll('[data-reveal]'));
        if (!revealElements.length) {
            return;
        }

        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduceMotion || !('IntersectionObserver' in window)) {
            revealElements.forEach((element) => element.classList.add('is-visible'));
            return;
        }

        revealElements.forEach((element) => {
            const delay = element.dataset.revealDelay;
            if (delay) {
                element.style.setProperty('--reveal-delay', `${delay}ms`);
            }
        });

        const observer = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    entry.target.classList.add('is-visible');
                    obs.unobserve(entry.target);
                });
            },
            {
                threshold: 0.18,
                rootMargin: '0px 0px -8% 0px'
            }
        );

        revealElements.forEach((element) => observer.observe(element));
    };
    
    // ===== DARK MODE TOGGLE =====
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    
    if (darkModeToggle) {
        // Set initial theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);

        const emitThemeChange = (theme) => {
            document.dispatchEvent(new CustomEvent('themechange', { detail: theme }));
        };

        emitThemeChange(savedTheme);

        // Add click event
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';


            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            emitThemeChange(newTheme);

            // Force repaint
            document.body.offsetHeight;
        });

    } else {
        console.error('❌ Dark mode toggle not found!');
    }
    
    // ===== MOBILE MENU =====
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    
    
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function(e) {
            e.preventDefault();
            
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
            
        });
        
        // Close menu when clicking links
        const menuLinks = navLinks.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
        
    } else {
        console.error('❌ Hamburger or nav links not found!');
    }
    
    // ===== SMOOTH SCROLLING =====
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const navbarHeight = 100;
                let targetPosition = targetElement.offsetTop - navbarHeight;
                
                if (targetId === '#top') {
                    targetPosition = 0;
                }
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    initScrollReveal();

    // ===== CONTACT FORM HANDLER =====
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        const submitButton = contactForm.querySelector('.submit-button');
        const successMessage = document.getElementById('contact-success');
        const errorMessage = document.getElementById('contact-error');
        const defaultButtonText = submitButton ? submitButton.textContent : '';

        contactForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (successMessage) successMessage.hidden = true;
            if (errorMessage) errorMessage.hidden = true;

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Sending...';
            }

            try {
                const response = await fetch(contactForm.action, {
                    method: 'POST',
                    body: new FormData(contactForm),
                    headers: { 'Accept': 'application/json' }
                });

                if (response.ok) {
                    contactForm.reset();
                    if (successMessage) successMessage.hidden = false;
                } else {
                    throw new Error(`Form submission failed with status ${response.status}`);
                }
            } catch (error) {
                console.error('❌ Contact form submission error:', error);
                if (errorMessage) errorMessage.hidden = false;
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = defaultButtonText;
                }
            }
        });
    }

    // ===== CALENDLY BADGE & TRIGGERS =====
    const calendlyLink = document.body && document.body.dataset
        ? document.body.dataset.calendlyLink
        : null;
    const contactLinkHref = document.body && document.body.dataset
        ? document.body.dataset.contactLink
        : null;
    if (calendlyLink) {
        const ensureCalendlyScript = () => new Promise((resolve, reject) => {
            const existingScript = document.querySelector('script[data-calendly-widget]');
            if (existingScript) {
                if (window.Calendly) {
                    resolve();
                    return;
                }
                existingScript.addEventListener('load', resolve, { once: true });
                existingScript.addEventListener('error', reject, { once: true });
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://assets.calendly.com/assets/external/widget.js';
            script.async = true;
            script.dataset.calendlyWidget = 'true';
            script.addEventListener('load', resolve, { once: true });
            script.addEventListener('error', reject, { once: true });
            document.head.appendChild(script);
        });

        const markContactLinks = () => {
            if (!contactLinkHref) {
                return;
            }
            const contactAnchors = document.querySelectorAll(`a[href="${contactLinkHref}"]`);
            contactAnchors.forEach(anchor => {
                anchor.classList.add('js-calendly-trigger');
                if (!anchor.dataset.calendlyUrl) {
                    anchor.dataset.calendlyUrl = calendlyLink;
                }
            });
        };

        const attachCalendlyTriggers = () => {
            const triggers = document.querySelectorAll('.js-calendly-trigger');
            triggers.forEach(trigger => {
                if (trigger.dataset.calendlyBound === 'true') {
                    return;
                }

                trigger.addEventListener('click', (event) => {
                    const targetUrl = trigger.dataset.calendlyUrl || calendlyLink;
                    const canOpenPopup = window.Calendly && typeof window.Calendly.initPopupWidget === 'function';

                    if (canOpenPopup) {
                        event.preventDefault();
                        window.Calendly.initPopupWidget({ url: targetUrl });
                    } else if (trigger.tagName === 'A') {
                        trigger.setAttribute('target', '_blank');
                        trigger.href = targetUrl;
                    } else {
                        window.open(targetUrl, '_blank');
                    }
                });

                trigger.dataset.calendlyBound = 'true';
            });
        };

        markContactLinks();
        attachCalendlyTriggers();
        ensureCalendlyScript()
            .then(() => {
                attachCalendlyTriggers();
            })
            .catch((error) => {
                console.error('❌ Calendly widget failed to load', error);
            });
    }

});
