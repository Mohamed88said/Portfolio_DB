// Traductions communes à toutes les pages
const translations = {
    'fr': {
        'nav_home': 'Accueil',
        'nav_academic': 'Parcours Académique',
        'nav_experience': 'Expériences',
        'nav_certifications': 'Certifications',
        'nav_contact': 'Contact',
        'rights': 'Tous droits réservés'
    },
    'en': {
        'nav_home': 'Home',
        'nav_academic': 'Academic Path',
        'nav_experience': 'Experiences',
        'nav_certifications': 'Certifications',
        'nav_contact': 'Contact',
        'rights': 'All rights reserved'
    },
    'ar': {
        'nav_home': 'الرئيسية',
        'nav_academic': 'المسار الأكاديمي',
        'nav_experience': 'الخبرات',
        'nav_certifications': 'الشهادات',
        'nav_contact': 'اتصل',
        'rights': 'جميع الحقوق محفوظة'
    }
};

// Fonction pour changer de langue
function changeLanguage(lang) {
    // Sauvegarder la langue
    localStorage.setItem('preferredLanguage', lang);
    
    // Mettre à jour le sélecteur
    const select = document.querySelector('.language-select');
    if (select) select.value = lang;
    
    // Appliquer les traductions
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    // Mettre à jour l'attribut lang
    document.documentElement.lang = lang;
}

// Fonction pour basculer le mode sombre
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const icon = document.querySelector('.dark-mode-toggle i');
    
    if (document.body.classList.contains('dark-mode')) {
        icon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('darkMode', 'enabled');
    } else {
        icon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Appliquer les préférences au chargement
function applyPreferences() {
    // Mode sombre
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        const icon = document.querySelector('.dark-mode-toggle i');
        if (icon) icon.classList.replace('fa-moon', 'fa-sun');
    }
    
    // Langue
    const lang = localStorage.getItem('preferredLanguage') || 'fr';
    changeLanguage(lang);
    
    // Année du footer
    document.getElementById('currentYear').textContent = new Date().getFullYear();
}

// Initialisation
document.addEventListener('DOMContentLoaded', applyPreferences);

// Exposer les fonctions globales
window.toggleDarkMode = toggleDarkMode;
window.changeLanguage = changeLanguage;
