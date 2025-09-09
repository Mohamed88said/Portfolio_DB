from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import (
    Profile, Education, Experience, Skill, 
    Certification, Project, SiteSettings
)
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample data for the portfolio'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create Profile
        profile, created = Profile.objects.get_or_create(
            defaults={
                'name': 'Mohamed Saïd Diallo',
                'title': 'Développeur Full Stack & Data Scientist',
                'bio': '''Passionné par le développement web et l'intelligence artificielle, 
                je crée des solutions innovantes qui allient performance technique et expérience utilisateur exceptionnelle. 
                Avec une expertise en Python, Django, React et Machine Learning, je transforme les idées en applications robustes et scalables.''',
                'email': 'mohamed.said.diallo@example.com',
                'phone': '+33 6 12 34 56 78',
                'location': 'Paris, France',
                'linkedin': 'https://linkedin.com/in/mohamed-said-diallo',
                'github': 'https://github.com/msdiallo',
                'website': 'https://msdiallo.dev',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created profile'))

        # Create Education
        educations = [
            {
                'degree': 'master',
                'field_of_study': 'Intelligence Artificielle et Data Science',
                'institution': 'Université Paris-Saclay',
                'location': 'Paris, France',
                'start_date': date(2020, 9, 1),
                'end_date': date(2022, 6, 30),
                'description': 'Master spécialisé en IA avec focus sur le Machine Learning, Deep Learning et Big Data.',
                'grade': 'Mention Très Bien'
            },
            {
                'degree': 'bachelor',
                'field_of_study': 'Informatique et Mathématiques Appliquées',
                'institution': 'Université Pierre et Marie Curie',
                'location': 'Paris, France',
                'start_date': date(2017, 9, 1),
                'end_date': date(2020, 6, 30),
                'description': 'Formation solide en programmation, algorithmes et mathématiques.',
                'grade': 'Mention Bien'
            }
        ]
        
        for edu_data in educations:
            Education.objects.get_or_create(
                field_of_study=edu_data['field_of_study'],
                institution=edu_data['institution'],
                defaults=edu_data
            )
        self.stdout.write(self.style.SUCCESS('Created education records'))

        # Create Experiences
        experiences = [
            {
                'title': 'Lead Developer Full Stack',
                'company': 'TechCorp Solutions',
                'location': 'Paris, France',
                'job_type': 'full_time',
                'start_date': date(2022, 7, 1),
                'is_current': True,
                'description': '''Direction technique d'une équipe de 5 développeurs pour la création d'applications web innovantes.
                Développement d'APIs REST avec Django et interfaces React.js performantes.
                Mise en place de l'architecture microservices et déploiement sur AWS.''',
                'achievements': '''• Augmentation de 40% des performances des applications
                • Réduction de 60% du temps de déploiement
                • Formation et mentorat de 3 développeurs juniors''',
                'technologies': 'Python, Django, React.js, PostgreSQL, AWS, Docker, Kubernetes'
            },
            {
                'title': 'Développeur Full Stack',
                'company': 'StartupInnovante',
                'location': 'Lyon, France',
                'job_type': 'full_time',
                'start_date': date(2021, 1, 15),
                'end_date': date(2022, 6, 30),
                'description': '''Développement d'une plateforme SaaS de gestion de projets utilisée par plus de 10,000 utilisateurs.
                Création d'APIs robustes et d'interfaces utilisateur intuitives.''',
                'achievements': '''• Développement de 15+ fonctionnalités majeures
                • Optimisation des requêtes SQL (-50% temps de réponse)
                • Intégration de 5 APIs tierces''',
                'technologies': 'Django, Vue.js, MySQL, Redis, Celery, Stripe API'
            }
        ]
        
        for exp_data in experiences:
            Experience.objects.get_or_create(
                title=exp_data['title'],
                company=exp_data['company'],
                defaults=exp_data
            )
        self.stdout.write(self.style.SUCCESS('Created experience records'))

        # Create Skills
        skills = [
            # Technical Skills
            {'name': 'Python', 'category': 'technical', 'proficiency': 'expert', 'years_of_experience': 5, 'is_featured': True},
            {'name': 'Django', 'category': 'technical', 'proficiency': 'expert', 'years_of_experience': 4, 'is_featured': True},
            {'name': 'React.js', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 3, 'is_featured': True},
            {'name': 'JavaScript', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 4, 'is_featured': True},
            {'name': 'PostgreSQL', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 3},
            {'name': 'Machine Learning', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 2, 'is_featured': True},
            {'name': 'Docker', 'category': 'tool', 'proficiency': 'advanced', 'years_of_experience': 2},
            {'name': 'AWS', 'category': 'tool', 'proficiency': 'intermediate', 'years_of_experience': 2},
            
            # Soft Skills
            {'name': 'Leadership', 'category': 'soft', 'proficiency': 'advanced', 'years_of_experience': 3},
            {'name': 'Communication', 'category': 'soft', 'proficiency': 'expert', 'years_of_experience': 5},
            {'name': 'Gestion de projet', 'category': 'soft', 'proficiency': 'advanced', 'years_of_experience': 3},
            
            # Languages
            {'name': 'Français', 'category': 'language', 'proficiency': 'expert', 'years_of_experience': 25},
            {'name': 'Anglais', 'category': 'language', 'proficiency': 'advanced', 'years_of_experience': 10},
            {'name': 'Arabe', 'category': 'language', 'proficiency': 'intermediate', 'years_of_experience': 15},
        ]
        
        for skill_data in skills:
            Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults=skill_data
            )
        self.stdout.write(self.style.SUCCESS('Created skill records'))

        # Create Certifications
        certifications = [
            {
                'name': 'AWS Certified Solutions Architect',
                'issuing_organization': 'Amazon Web Services',
                'issue_date': date(2023, 3, 15),
                'expiration_date': date(2026, 3, 15),
                'credential_id': 'AWS-CSA-2023-001234',
                'credential_url': 'https://aws.amazon.com/verification'
            },
            {
                'name': 'Professional Scrum Master I',
                'issuing_organization': 'Scrum.org',
                'issue_date': date(2022, 11, 20),
                'credential_id': 'PSM-I-2022-567890',
                'credential_url': 'https://scrum.org/certificates'
            },
            {
                'name': 'Google Cloud Professional Data Engineer',
                'issuing_organization': 'Google Cloud',
                'issue_date': date(2023, 1, 10),
                'expiration_date': date(2025, 1, 10),
                'credential_id': 'GCP-PDE-2023-112233'
            }
        ]
        
        for cert_data in certifications:
            Certification.objects.get_or_create(
                name=cert_data['name'],
                defaults=cert_data
            )
        self.stdout.write(self.style.SUCCESS('Created certification records'))

        # Create Projects
        projects = [
            {
                'title': 'EcoTrack - Application de Suivi Environnemental',
                'description': 'Application mobile et web pour suivre son empreinte carbone personnelle avec recommandations IA.',
                'detailed_description': '''EcoTrack est une application complète qui permet aux utilisateurs de suivre leur impact environnemental quotidien. 
                
**Fonctionnalités principales :**
- Calcul automatique de l'empreinte carbone
- Recommandations personnalisées par IA
- Gamification avec système de points
- Communauté d'utilisateurs engagés
- Intégration avec IoT pour données automatiques

**Défis techniques relevés :**
- Algorithmes de calcul d'empreinte carbone précis
- Architecture microservices scalable
- Interface utilisateur intuitive et engageante
- Intégration de multiples sources de données

**Impact :**
Plus de 50,000 utilisateurs actifs, réduction moyenne de 25% de l'empreinte carbone des utilisateurs.''',
                'technologies': 'Django, React Native, PostgreSQL, TensorFlow, AWS, Docker',
                'status': 'completed',
                'start_date': date(2023, 1, 1),
                'end_date': date(2023, 8, 31),
                'project_url': 'https://ecotrack-app.com',
                'github_url': 'https://github.com/msdiallo/ecotrack',
                'is_featured': True
            },
            {
                'title': 'SmartFinance - Plateforme de Gestion Financière',
                'description': 'Plateforme SaaS de gestion financière avec IA prédictive pour PME.',
                'detailed_description': '''SmartFinance révolutionne la gestion financière des PME grâce à l'intelligence artificielle.

**Fonctionnalités clés :**
- Tableau de bord financier en temps réel
- Prédictions de trésorerie par IA
- Automatisation de la comptabilité
- Intégration bancaire sécurisée
- Rapports financiers automatisés

**Technologies innovantes :**
- Machine Learning pour prédictions
- Blockchain pour sécurité des transactions
- API Banking PSD2
- Architecture serverless

**Résultats :**
Utilisé par 200+ PME, économie moyenne de 15h/mois de travail comptable.''',
                'technologies': 'Django, Vue.js, PostgreSQL, Scikit-learn, AWS Lambda, Stripe',
                'status': 'completed',
                'start_date': date(2022, 6, 1),
                'end_date': date(2023, 2, 28),
                'project_url': 'https://smartfinance-platform.com',
                'github_url': 'https://github.com/msdiallo/smartfinance',
                'is_featured': True
            },
            {
                'title': 'HealthBot - Assistant Médical IA',
                'description': 'Chatbot intelligent pour pré-diagnostic médical et orientation des patients.',
                'detailed_description': '''HealthBot utilise le NLP avancé pour fournir une première évaluation médicale.

**Capacités du bot :**
- Analyse des symptômes en langage naturel
- Recommandations de spécialistes
- Suivi des traitements
- Intégration avec dossiers médicaux
- Support multilingue

**IA et Sécurité :**
- Modèles NLP entraînés sur données médicales
- Chiffrement end-to-end
- Conformité RGPD et HIPAA
- Validation par professionnels de santé

**Impact social :**
Déployé dans 5 hôpitaux, réduction de 30% du temps d'attente aux urgences.''',
                'technologies': 'Python, FastAPI, Transformers, PostgreSQL, Redis, Docker',
                'status': 'in_progress',
                'start_date': date(2023, 9, 1),
                'project_url': 'https://healthbot-ai.com',
                'is_featured': True
            },
            {
                'title': 'DevOps Pipeline Automation',
                'description': 'Suite d\'outils pour automatisation complète des pipelines CI/CD.',
                'technologies': 'Jenkins, Docker, Kubernetes, Terraform, AWS',
                'status': 'completed',
                'start_date': date(2022, 3, 1),
                'end_date': date(2022, 7, 31),
                'github_url': 'https://github.com/msdiallo/devops-automation'
            },
            {
                'title': 'E-Learning Platform',
                'description': 'Plateforme d\'apprentissage en ligne avec système de recommandation IA.',
                'technologies': 'Django, React, PostgreSQL, TensorFlow, AWS',
                'status': 'completed',
                'start_date': date(2021, 10, 1),
                'end_date': date(2022, 4, 30),
                'project_url': 'https://learn-platform.com'
            }
        ]
        
        for proj_data in projects:
            Project.objects.get_or_create(
                title=proj_data['title'],
                defaults=proj_data
            )
        self.stdout.write(self.style.SUCCESS('Created project records'))

        # Create Site Settings
        site_settings, created = SiteSettings.objects.get_or_create(
            defaults={
                'site_title': 'Mohamed Saïd Diallo - Portfolio',
                'site_description': 'Portfolio professionnel de Mohamed Saïd Diallo, Développeur Full Stack et Data Scientist spécialisé en Python, Django, React et Intelligence Artificielle.',
                'footer_text': 'Créé avec passion et Django ❤️',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created site settings'))

        self.stdout.write(
            self.style.SUCCESS('Successfully created all sample data!')
        )
        self.stdout.write(
            self.style.WARNING('Admin credentials: admin / admin123')
        )