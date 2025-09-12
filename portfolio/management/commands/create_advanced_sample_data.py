from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import *
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Create advanced sample data for the portfolio'

    def handle(self, *args, **options):
        self.stdout.write('Creating advanced sample data...')
        
        # Créer des tags
        tags_data = [
            {'name': 'Python', 'color': '#3776ab', 'is_featured': True},
            {'name': 'Django', 'color': '#092e20', 'is_featured': True},
            {'name': 'React', 'color': '#61dafb', 'is_featured': True},
            {'name': 'JavaScript', 'color': '#f7df1e', 'is_featured': True},
            {'name': 'Machine Learning', 'color': '#ff6b6b', 'is_featured': True},
            {'name': 'Data Science', 'color': '#4ecdc4', 'is_featured': True},
            {'name': 'API REST', 'color': '#45b7d1'},
            {'name': 'PostgreSQL', 'color': '#336791'},
            {'name': 'Docker', 'color': '#2496ed'},
            {'name': 'AWS', 'color': '#ff9900'},
            {'name': 'Vue.js', 'color': '#4fc08d'},
            {'name': 'Node.js', 'color': '#339933'},
            {'name': 'MongoDB', 'color': '#47a248'},
            {'name': 'Redis', 'color': '#dc382d'},
            {'name': 'Kubernetes', 'color': '#326ce5'},
            {'name': 'TensorFlow', 'color': '#ff6f00'},
            {'name': 'Blockchain', 'color': '#f7931a'},
            {'name': 'IoT', 'color': '#00d4aa'},
            {'name': 'DevOps', 'color': '#326ce5'},
            {'name': 'Microservices', 'color': '#ff6b35'},
        ]
        
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults=tag_data
            )
            if created:
                self.stdout.write(f'Created tag: {tag.name}')

        # Créer des FAQ
        faqs_data = [
            {
                'question': 'Quels sont vos tarifs pour un projet web ?',
                'answer': '''Mes tarifs varient selon la complexité du projet :

**Sites vitrine** : 1 500€ - 3 000€
- Design responsive
- CMS intégré
- Optimisation SEO de base

**Applications web** : 5 000€ - 15 000€
- Fonctionnalités sur mesure
- Base de données
- Panel d'administration

**Applications complexes** : 15 000€+
- Architecture microservices
- Intégrations multiples
- Haute performance

Je propose toujours un devis gratuit après analyse de vos besoins.''',
                'category': 'pricing',
                'order': 1
            },
            {
                'question': 'Combien de temps prend le développement d\'un projet ?',
                'answer': '''La durée dépend de la complexité :

**Site vitrine** : 2-4 semaines
**Application web simple** : 1-3 mois
**Application complexe** : 3-6 mois
**Projet d\'entreprise** : 6+ mois

Je fournis toujours un planning détaillé avec des jalons clairs.''',
                'category': 'process',
                'order': 2
            },
            {
                'question': 'Proposez-vous de la maintenance après livraison ?',
                'answer': '''Oui, je propose plusieurs formules de maintenance :

**Maintenance corrective** : Correction des bugs
**Maintenance évolutive** : Nouvelles fonctionnalités
**Maintenance préventive** : Mises à jour sécurité

Tous mes projets incluent 3 mois de maintenance gratuite.''',
                'category': 'services',
                'order': 3
            },
            {
                'question': 'Travaillez-vous avec des équipes existantes ?',
                'answer': '''Absolument ! J\'ai l\'habitude de travailler :

- En équipe avec d\'autres développeurs
- Avec des designers et UX/UI
- En méthode Agile/Scrum
- En remote ou sur site

Je m\'adapte à vos processus existants.''',
                'category': 'process',
                'order': 4
            },
            {
                'question': 'Quelles technologies utilisez-vous ?',
                'answer': '''Mon stack principal :

**Backend** : Python/Django, Node.js, PostgreSQL
**Frontend** : React, Vue.js, JavaScript moderne
**DevOps** : Docker, AWS, CI/CD
**Mobile** : React Native, Flutter
**IA/ML** : TensorFlow, Scikit-learn, OpenAI

Je choisis toujours la technologie la plus adaptée au projet.''',
                'category': 'technical',
                'order': 5
            }
        ]
        
        for faq_data in faqs_data:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                self.stdout.write(f'Created FAQ: {faq.question[:50]}...')

        # Créer des événements timeline
        timeline_events = [
            {
                'title': 'Début des études en informatique',
                'description': 'Entrée à l\'université pour étudier l\'informatique et les mathématiques appliquées.',
                'date': date(2017, 9, 1),
                'category': 'education',
                'icon': 'fas fa-graduation-cap',
                'color': '#3498db'
            },
            {
                'title': 'Premier stage en développement',
                'description': 'Stage de 3 mois dans une startup tech, découverte du développement web avec Django.',
                'date': date(2019, 6, 1),
                'category': 'career',
                'icon': 'fas fa-briefcase',
                'color': '#2ecc71',
                'is_milestone': True
            },
            {
                'title': 'Obtention du Bachelor',
                'description': 'Diplôme en informatique et mathématiques appliquées avec mention Bien.',
                'date': date(2020, 6, 30),
                'category': 'education',
                'icon': 'fas fa-medal',
                'color': '#f39c12',
                'is_milestone': True
            },
            {
                'title': 'Premier emploi Full Stack',
                'description': 'Embauche comme développeur Full Stack junior dans une scale-up parisienne.',
                'date': date(2020, 9, 1),
                'category': 'career',
                'icon': 'fas fa-rocket',
                'color': '#e74c3c',
                'is_milestone': True
            },
            {
                'title': 'Certification AWS',
                'description': 'Obtention de la certification AWS Solutions Architect Associate.',
                'date': date(2021, 3, 15),
                'category': 'achievement',
                'icon': 'fas fa-cloud',
                'color': '#ff9500'
            },
            {
                'title': 'Lancement du premier projet personnel',
                'description': 'Création et lancement d\'EcoTrack, application de suivi environnemental.',
                'date': date(2021, 8, 1),
                'category': 'project',
                'icon': 'fas fa-leaf',
                'color': '#27ae60',
                'is_milestone': True
            },
            {
                'title': 'Promotion Lead Developer',
                'description': 'Promotion au poste de Lead Developer avec management d\'équipe.',
                'date': date(2022, 1, 1),
                'category': 'career',
                'icon': 'fas fa-users',
                'color': '#8e44ad',
                'is_milestone': True
            },
            {
                'title': 'Conférence TechTalk',
                'description': 'Présentation sur l\'IA et le développement durable à la conférence TechTalk Paris.',
                'date': date(2022, 10, 15),
                'category': 'achievement',
                'icon': 'fas fa-microphone',
                'color': '#e67e22'
            },
            {
                'title': 'Début du freelancing',
                'description': 'Transition vers le freelancing pour plus de flexibilité et de projets variés.',
                'date': date(2023, 1, 1),
                'category': 'career',
                'icon': 'fas fa-handshake',
                'color': '#34495e',
                'is_milestone': True
            }
        ]
        
        for event_data in timeline_events:
            event, created = Timeline.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data
            )
            if created:
                self.stdout.write(f'Created timeline event: {event.title}')

        # Créer des collaborations
        collaborations_data = [
            {
                'partner_name': 'TechCorp Solutions',
                'collaboration_type': 'employer',
                'description': 'Développement d\'applications web innovantes pour des clients grands comptes.',
                'start_date': date(2022, 7, 1),
                'is_ongoing': True,
                'website': 'https://techcorp-solutions.com'
            },
            {
                'partner_name': 'StartupInnovante',
                'collaboration_type': 'client',
                'description': 'Création d\'une plateforme SaaS de gestion de projets.',
                'start_date': date(2021, 1, 15),
                'end_date': date(2022, 6, 30),
                'website': 'https://startupinnovante.fr'
            },
            {
                'partner_name': 'OpenSource Community',
                'collaboration_type': 'contributor',
                'description': 'Contributions régulières à des projets open source Django et React.',
                'start_date': date(2020, 1, 1),
                'is_ongoing': True,
                'website': 'https://github.com'
            },
            {
                'partner_name': 'École 42',
                'collaboration_type': 'mentor',
                'description': 'Mentorat d\'étudiants en développement web et mobile.',
                'start_date': date(2022, 9, 1),
                'is_ongoing': True,
                'website': 'https://42.fr'
            }
        ]
        
        for collab_data in collaborations_data:
            collab, created = Collaboration.objects.get_or_create(
                partner_name=collab_data['partner_name'],
                defaults=collab_data
            )
            if created:
                self.stdout.write(f'Created collaboration: {collab.partner_name}')

        # Créer des ressources
        resources_data = [
            {
                'title': 'CV - Mohamed Saïd Diallo',
                'description': 'Mon CV complet au format PDF avec toutes mes expériences et compétences.',
                'file_type': 'pdf',
                'category': 'cv',
                'is_public': True
            },
            {
                'title': 'Template Django Starter',
                'description': 'Template de démarrage pour projets Django avec authentification et admin.',
                'file_type': 'code',
                'category': 'template',
                'is_public': True
            },
            {
                'title': 'Guide API REST avec Django',
                'description': 'Guide complet pour créer des APIs REST performantes avec Django REST Framework.',
                'file_type': 'pdf',
                'category': 'guide',
                'is_public': True
            },
            {
                'title': 'Présentation Machine Learning',
                'description': 'Slides de ma présentation sur l\'intégration du ML dans les applications web.',
                'file_type': 'pdf',
                'category': 'presentation',
                'is_public': True
            }
        ]
        
        for resource_data in resources_data:
            resource, created = Resource.objects.get_or_create(
                title=resource_data['title'],
                defaults=resource_data
            )
            if created:
                # Simuler des téléchargements
                resource.download_count = random.randint(10, 500)
                resource.save()
                self.stdout.write(f'Created resource: {resource.title}')

        # Créer des requêtes de recherche simulées
        search_queries = [
            'Python Django', 'React JavaScript', 'Machine Learning', 'API REST',
            'PostgreSQL', 'Docker', 'AWS', 'Vue.js', 'Node.js', 'MongoDB',
            'développement web', 'application mobile', 'intelligence artificielle',
            'data science', 'blockchain', 'microservices', 'devops'
        ]
        
        for query in search_queries:
            for _ in range(random.randint(1, 20)):
                SearchQueryModel.objects.create(
                    query=query,
                    results_count=random.randint(1, 50),
                    search_date=timezone.now() - timedelta(days=random.randint(1, 30))
                )
        
        self.stdout.write(f'Created {len(search_queries)} search query types')

        # Associer des tags aux projets existants
        projects = Project.objects.all()
        tags = Tag.objects.all()
        
        for project in projects:
            # Associer 3-5 tags aléatoires à chaque projet
            project_tags = random.sample(list(tags), random.randint(3, 5))
            project.tags.set(project_tags)
            
            # Mettre à jour le compteur d'usage des tags
            for tag in project_tags:
                tag.usage_count += 1
                tag.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully created all advanced sample data!')
        )