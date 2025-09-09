// Dashboard et statistiques avancées

class PortfolioDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.loadStats();
        this.setupRealTimeUpdates();
        this.initializeCharts();
        this.setupMetricsAnimation();
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats/');
            const data = await response.json();
            
            if (data.success) {
                this.updateDashboardMetrics(data.stats);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des statistiques:', error);
        }
    }

    updateDashboardMetrics(stats) {
        // Mettre à jour les métriques principales
        this.animateCounter('totalProjects', stats.total_projects);
        this.animateCounter('totalSkills', stats.total_skills);
        this.animateCounter('experienceYears', stats.experience_years);
        this.animateCounter('recentVisits', stats.recent_visits);

        // Mettre à jour les pages populaires
        this.updatePopularPages(stats.popular_pages);
    }

    animateCounter(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const duration = 2000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * this.easeOutQuart(progress));
            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    updatePopularPages(pages) {
        const container = document.getElementById('popularPages');
        if (!container || !pages) return;

        container.innerHTML = pages.map(page => `
            <div class="popular-page-item d-flex justify-content-between align-items-center mb-2">
                <span class="page-name">${page.page_visited}</span>
                <span class="badge bg-primary">${page.count}</span>
            </div>
        `).join('');
    }

    setupRealTimeUpdates() {
        // Mettre à jour les statistiques toutes les 30 secondes
        setInterval(() => {
            this.loadStats();
        }, 30000);
    }

    initializeCharts() {
        this.createVisitsChart();
        this.createSkillsChart();
        this.createProjectsChart();
    }

    createVisitsChart() {
        const canvas = document.getElementById('visitsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Données simulées pour la démonstration
        const data = {
            labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
            datasets: [{
                label: 'Visites',
                data: [12, 19, 3, 5, 2, 3, 9],
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    createSkillsChart() {
        const canvas = document.getElementById('skillsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        const data = {
            labels: ['Technique', 'Soft Skills', 'Langues', 'Outils'],
            datasets: [{
                data: [45, 25, 15, 15],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(52, 152, 219, 0.8)',
                    'rgba(231, 76, 60, 0.8)'
                ],
                borderWidth: 0
            }]
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createProjectsChart() {
        const canvas = document.getElementById('projectsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        const data = {
            labels: ['Terminés', 'En cours', 'Planifiés'],
            datasets: [{
                label: 'Projets',
                data: [8, 3, 2],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(108, 117, 125, 0.8)'
                ],
                borderWidth: 0
            }]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    setupMetricsAnimation() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    element.classList.add('metric-animated');
                    
                    // Animer les compteurs
                    const counter = element.querySelector('.metric-value');
                    if (counter) {
                        const targetValue = parseInt(counter.textContent);
                        this.animateCounter(counter.id || 'temp', targetValue);
                    }
                }
            });
        });

        document.querySelectorAll('.realtime-metric, .dashboard-stat').forEach(el => {
            observer.observe(el);
        });
    }

    // Méthodes utilitaires pour les métriques
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    calculatePercentageChange(current, previous) {
        if (previous === 0) return 0;
        return ((current - previous) / previous * 100).toFixed(1);
    }

    updateMetricWithChange(elementId, currentValue, previousValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const valueElement = element.querySelector('.metric-value');
        const changeElement = element.querySelector('.metric-change');

        if (valueElement) {
            valueElement.textContent = this.formatNumber(currentValue);
        }

        if (changeElement && previousValue !== undefined) {
            const change = this.calculatePercentageChange(currentValue, previousValue);
            const isPositive = change >= 0;
            
            changeElement.textContent = `${isPositive ? '+' : ''}${change}%`;
            changeElement.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
        }
    }

    // Exportation des données
    exportStats() {
        this.loadStats().then(() => {
            const data = {
                timestamp: new Date().toISOString(),
                stats: this.currentStats
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {
                type: 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `portfolio-stats-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
}

// Initialiser le dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.dashboard-stat, .realtime-metric')) {
        window.portfolioDashboard = new PortfolioDashboard();
    }
});

// Fonctions globales pour l'exportation
window.exportStats = () => {
    if (window.portfolioDashboard) {
        window.portfolioDashboard.exportStats();
    }
};