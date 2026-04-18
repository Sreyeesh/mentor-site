document.addEventListener('DOMContentLoaded', function () {
    const initScrollReveal = () => {
        const revealElements = Array.from(document.querySelectorAll('[data-reveal]'));
        if (!revealElements.length) return;

        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduceMotion || !('IntersectionObserver' in window)) {
            revealElements.forEach((el) => el.classList.add('is-visible'));
            return;
        }

        revealElements.forEach((el) => {
            const delay = el.dataset.revealDelay;
            if (delay) el.style.setProperty('--reveal-delay', `${delay}ms`);
        });

        const observer = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add('is-visible');
                    obs.unobserve(entry.target);
                });
            },
            { threshold: 0.18, rootMargin: '0px 0px -8% 0px' }
        );
        revealElements.forEach((el) => observer.observe(el));
    };

    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);

        const emitThemeChange = (theme) => {
            document.dispatchEvent(new CustomEvent('themechange', { detail: theme }));
        };
        emitThemeChange(savedTheme);

        darkModeToggle.addEventListener('click', function (e) {
            e.preventDefault();
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            emitThemeChange(newTheme);
            document.body.offsetHeight;
        });
    }

    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function (e) {
            e.preventDefault();
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        navLinks.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', function () {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: this.getAttribute('href') === '#top' ? 0 : target.offsetTop - 100,
                    behavior: 'smooth',
                });
            }
        });
    });

    initScrollReveal();
});
