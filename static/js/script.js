// Dark mode functionality
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Check for saved theme preference or default to system preference
    const currentTheme = localStorage.getItem('theme') || 
                        (prefersDarkScheme.matches ? 'dark' : 'light');
    
    // Apply the theme
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Toggle theme function
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }
    
    // Event listeners - only add if element exists
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleTheme);
    }
    
    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
        }
    });
});

// Enhanced smooth scrolling functionality
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const navbarHeight = 100; // Height of fixed navbar
                let targetPosition = targetElement.offsetTop - navbarHeight;
                
                // Special handling for top of page
                if (targetId === '#top') {
                    targetPosition = 0;
                }
                
                // Faster smooth scroll
                smoothScrollTo(targetPosition, 400);
            }
        });
    });
    
    // Simplified and faster smooth scroll function
    function smoothScrollTo(targetPosition, duration) {
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        const startTime = performance.now();
        
        function animation(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Simple ease-out function for faster, more natural movement
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentPosition = startPosition + (distance * easeOut);
            
            window.scrollTo(0, currentPosition);
            
            if (progress < 1) {
                requestAnimationFrame(animation);
            }
        }
        
        requestAnimationFrame(animation);
    }
    
    // Simplified scroll animations for sections
    const sections = document.querySelectorAll('section');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Add fade-in class to sections and observe them
    sections.forEach(section => {
        section.classList.add('fade-in');
        sectionObserver.observe(section);
    });
    
    // Active navigation highlighting
    const navLinks = document.querySelectorAll('.nav-links a');
    const sectionsWithIds = document.querySelectorAll('section[id]');
    
    function updateActiveNavLink() {
        const scrollPosition = window.scrollY + 150; // Offset for navbar
        
        sectionsWithIds.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    // Throttled scroll event for better performance
    let ticking = false;
    function updateOnScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateActiveNavLink();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', updateOnScroll);
    
    // Initial call to set active nav link
    updateActiveNavLink();
});

// Existing mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    
    // Only add event listeners if elements exist
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        
        // Close menu when clicking on a link
        const navLinksItems = navLinks.querySelectorAll('a');
        navLinksItems.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navLinks.contains(event.target)) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }
});

// Newsletter functionality
document.addEventListener('DOMContentLoaded', function() {
    // Newsletter form submission
    const newsletterForm = document.getElementById('newsletter-form');
    const popupNewsletterForm = document.getElementById('popup-newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSubmit);
    }
    
    if (popupNewsletterForm) {
        popupNewsletterForm.addEventListener('submit', handleNewsletterSubmit);
    }
    
    // Exit intent popup
    setupExitIntentPopup();
});

async function handleNewsletterSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const isPopup = form.id === 'popup-newsletter-form';
    
    const email = formData.get('email');
    const gdprConsent = formData.get('gdpr_consent') === 'on';
    
    const messageElement = isPopup ? 
        document.getElementById('popup-message') : 
        document.getElementById('newsletter-message');
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.textContent = 'Subscribing...';
    submitButton.disabled = true;
    
    try {
        const response = await fetch('/api/newsletter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                gdpr_consent: gdprConsent
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage(messageElement, result.message, 'success');
            form.reset();
            
            // If popup, close it after success
            if (isPopup) {
                setTimeout(() => {
                    closeExitIntentPopup();
                }, 2000);
            }
            
            // Track subscription event (for analytics)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'newsletter_signup', {
                    'event_category': 'engagement',
                    'event_label': isPopup ? 'exit_intent' : 'newsletter_section'
                });
            }
        } else {
            showMessage(messageElement, result.message, 'error');
        }
    } catch (error) {
        showMessage(messageElement, 'An error occurred. Please try again.', 'error');
    } finally {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `form-message ${type}`;
    element.style.display = 'block';
    
    // Hide message after 5 seconds
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

function setupExitIntentPopup() {
    const popup = document.getElementById('exit-intent-popup');
    const closeButton = document.getElementById('popup-close');
    let popupShown = false;
    let mouseLeftWindow = false;
    
    // Check if user has already subscribed or dismissed popup
    if (localStorage.getItem('newsletter_popup_dismissed') || 
        localStorage.getItem('newsletter_subscribed')) {
        return;
    }
    
    // Show popup when mouse leaves window (exit intent)
    document.addEventListener('mouseleave', function(e) {
        if (e.clientY <= 0 && !popupShown && !mouseLeftWindow) {
            showExitIntentPopup();
            mouseLeftWindow = true;
        }
    });
    
    // Alternative trigger: after 30 seconds if user is still on page
    setTimeout(() => {
        if (!popupShown && isUserEngaged()) {
            showExitIntentPopup();
        }
    }, 30000);
    
    // Close popup handlers
    if (closeButton) {
        closeButton.addEventListener('click', closeExitIntentPopup);
    }
    
    // Close on overlay click
    if (popup) {
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                closeExitIntentPopup();
            }
        });
    }
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && popupShown) {
            closeExitIntentPopup();
        }
    });
}

function showExitIntentPopup() {
    const popup = document.getElementById('exit-intent-popup');
    if (popup && !localStorage.getItem('newsletter_popup_dismissed')) {
        popup.style.display = 'flex';
        popupShown = true;
        document.body.style.overflow = 'hidden';
    }
}

function closeExitIntentPopup() {
    const popup = document.getElementById('exit-intent-popup');
    if (popup) {
        popup.style.display = 'none';
        popupShown = false;
        document.body.style.overflow = '';
        localStorage.setItem('newsletter_popup_dismissed', 'true');
    }
}

function isUserEngaged() {
    // Check if user has scrolled or spent time on page
    const scrolled = window.pageYOffset > 100;
    const timeSpent = Date.now() - performance.timing.navigationStart > 15000;
    return scrolled || timeSpent;
}

// Track successful newsletter subscription
function trackNewsletterSignup(source) {
    localStorage.setItem('newsletter_subscribed', 'true');
    
    // Google Analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'newsletter_signup', {
            'event_category': 'conversion',
            'event_label': source
        });
    }
}
