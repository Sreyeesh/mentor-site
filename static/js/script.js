// Simple, working JavaScript for dark mode and mobile menu
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded!');
    
    // ===== DARK MODE TOGGLE =====
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    console.log('🌙 Dark mode toggle found:', darkModeToggle);
    
    if (darkModeToggle) {
        // Set initial theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        console.log('🎨 Initial theme set to:', savedTheme);
        
        // Add click event
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🌙 Dark mode toggle clicked!');
            
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            console.log('🔄 Switching from', currentTheme, 'to', newTheme);
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Force repaint
            document.body.offsetHeight;
        });
        
        console.log('✅ Dark mode toggle event listener added');
    } else {
        console.error('❌ Dark mode toggle not found!');
    }
    
    // ===== MOBILE MENU =====
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    
    console.log('🍔 Hamburger found:', hamburger);
    console.log('📱 Nav links found:', navLinks);
    
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🍔 Hamburger clicked!');
            
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
            
            console.log('🍔 Menu toggled. Active:', navLinks.classList.contains('active'));
        });
        
        // Close menu when clicking links
        const menuLinks = navLinks.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                console.log('🔗 Menu link clicked, closing menu');
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
        
        console.log('✅ Mobile menu event listeners added');
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
    
    console.log('🎉 All functionality initialized!');
});
