// Fonctionnalités avancées pour le portfolio

class PortfolioEnhancer {
    constructor() {
        this.init();
    }

    init() {
        this.setupParticles();
        this.setupScrollAnimations();
        this.setupTypingEffect();
        this.setupSkillsAnimation();
        this.setupImageLazyLoading();
        this.setupSearchFunctionality();
        this.setupThemeTransitions();
        this.setupContactFormEnhancements();
        this.setupPerformanceMonitoring();
    }

    // Système de particules pour le hero
    setupParticles() {
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;

        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles';
        heroSection.appendChild(particlesContainer);

        for (let i = 0; i < 50; i++) {
            this.createParticle(particlesContainer);
        }

        // Créer de nouvelles particules périodiquement
        setInterval(() => {
            if (particlesContainer.children.length < 50) {
                this.createParticle(particlesContainer);
            }
        }, 200);
    }

    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
        container.appendChild(particle);

        // Supprimer la particule après l'animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 6000);
    }

    // Animations au scroll
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    
                    // Ajouter des classes d'animation basées sur la position
                    if (element.classList.contains('animate-on-scroll')) {
                        const animationType = element.dataset.animation || 'fade-in-scale';
                        element.classList.add(`animate-${animationType}`);
                    }

                    // Animation spéciale pour les cartes
                    if (element.classList.contains('card')) {
                        element.classList.add('animate-fade-in-scale');
                    }

                    // Animation pour les éléments de timeline
                    if (element.classList.contains('timeline-item')) {
                        element.classList.add('animate-slide-in-left');
                    }
                }
            });
        }, observerOptions);

        // Observer tous les éléments animables
        document.querySelectorAll('.card, .timeline-item, .animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    // Effet de frappe pour le titre
    setupTypingEffect() {
        const titleElement = document.querySelector('.hero-section h1');
        if (!titleElement) return;

        const originalText = titleElement.textContent;
        titleElement.textContent = '';
        titleElement.classList.add('typewriter');

        let i = 0;
        const typeInterval = setInterval(() => {
            titleElement.textContent += originalText.charAt(i);
            i++;
            if (i >= originalText.length) {
                clearInterval(typeInterval);
                setTimeout(() => {
                    titleElement.classList.remove('typewriter');
                }, 1000);
            }
        }, 100);
    }

    // Animation des barres de compétences
    setupSkillsAnimation() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.style.width;
                    
                    progressBar.style.width = '0%';
                    progressBar.parentElement.classList.add('progress-animated');
                    
                    setTimeout(() => {
                        progressBar.style.width = targetWidth;
                    }, 200);
                }
            });
        });

        progressBars.forEach(bar => progressObserver.observe(bar));
    }

    // Chargement paresseux des images
    setupImageLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Créer un placeholder de chargement
                    const placeholder = document.createElement('div');
                    placeholder.className = 'image-placeholder';
                    placeholder.innerHTML = '<div class="loading-spinner"></div>';
                    img.parentNode.insertBefore(placeholder, img);
                    
                    img.onload = () => {
                        img.classList.add('loaded');
                        placeholder.remove();
                    };
                    
                    img.src = img.dataset.src;
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Fonctionnalité de recherche
    setupSearchFunctionality() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        // Raccourci clavier Ctrl+K pour la recherche
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    performSearch(query) {
        const searchableItems = document.querySelectorAll('.searchable-item');
        const noResults = document.getElementById('noResults');
        let hasResults = false;

        searchableItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            if (matches || query === '') {
                item.style.display = 'block';
                item.classList.add('search-highlight');
                hasResults = true;
            } else {
                item.style.display = 'none';
                item.classList.remove('search-highlight');
            }
        });

        if (noResults) {
            noResults.style.display = hasResults || query === '' ? 'none' : 'block';
        }
    }

    // Transitions de thème améliorées
    setupThemeTransitions() {
        const themeToggle = document.getElementById('darkModeToggle');
        if (!themeToggle) return;

        themeToggle.addEventListener('click', () => {
            document.body.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }

    // Améliorations du formulaire de contact
    setupContactFormEnhancements() {
        const contactForm = document.getElementById('contactForm');
        if (!contactForm) return;

        // Validation en temps réel
        const inputs = contactForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });

        // Sauvegarde automatique
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                localStorage.setItem(`form_${input.name}`, input.value);
            });
        });

        // Restaurer les données sauvegardées
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`form_${input.name}`);
            if (savedValue) {
                input.value = savedValue;
            }
        });

        // Nettoyer après envoi réussi
        contactForm.addEventListener('submit', () => {
            inputs.forEach(input => {
                localStorage.removeItem(`form_${input.name}`);
            });
        });
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Validation requise
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Ce champ est requis';
        }

        // Validation email
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Adresse email invalide';
            }
        }

        // Validation longueur minimale
        if (field.dataset.minLength && value.length < parseInt(field.dataset.minLength)) {
            isValid = false;
            errorMessage = `Minimum ${field.dataset.minLength} caractères requis`;
        }

        this.updateFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    updateFieldValidation(field, isValid, errorMessage) {
        field.classList.remove('is-valid', 'is-invalid');
        
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            
            let errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentNode.appendChild(errorDiv);
            }
            errorDiv.textContent = errorMessage;
        }
    }

    // Monitoring des performances
    setupPerformanceMonitoring() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                    
                    console.log(`Page load time: ${loadTime}ms`);
                    
                    if (loadTime > 3000) {
                        console.warn('Page load time is slow. Consider optimizing.');
                    }
                }, 0);
            });
        }
    }

    // Méthodes utilitaires
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type} show`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialiser les améliorations
document.addEventListener('DOMContentLoaded', () => {
    new PortfolioEnhancer();
});

// Fonctions globales pour la compatibilité
window.showNotification = (message, type, duration) => {
    if (window.portfolioEnhancer) {
        window.portfolioEnhancer.showNotification(message, type, duration);
    }
};