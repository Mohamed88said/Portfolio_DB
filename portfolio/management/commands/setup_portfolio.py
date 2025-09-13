from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import *
from datetime import date

class Command(BaseCommand):
    help = 'Setup portfolio with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up portfolio...')
        
        # Create or update profile
        profile, created = Profile.objects.get_or_create(
            defaults={
                'name': 'Mohamed Saïd Diallo',
                'title': 'Développeur Full Stack & Data Scientist',
                'bio': '''Passionné par le développement web et l'intelligence artificielle, 
                je crée des solutions innovantes qui allient performance technique et expérience utilisateur exceptionnelle. 
                Avec une expertise en Python, Django, React et Machine Learning, je transforme les idées en applications robustes et scalables.''',
                'email': 'mohamedsaiddiallo88@gmail.com',
                'phone': '+33 6 12 34 56 78',
                'location': 'Paris, France',
                'linkedin': 'https://linkedin.com/in/mohamed-said-diallo',
                'github': 'https://github.com/msdiallo',
                'website': 'https://msdiallo.dev',
            }
        )
        
        # Create sample CV
        cv, created = CVDocument.objects.get_or_create(
            title="CV Principal - Mohamed Saïd Diallo",
            defaults={
                'description': 'CV complet avec toutes mes expériences et compétences',
                'cv_type': 'main',
                'language': 'fr',
                'is_primary': True,
                'is_public': True,
            }
        )
        
        # Create sample skills
        skills_data = [
            {'name': 'Python', 'category': 'technical', 'proficiency': 'expert', 'years_of_experience': 5, 'is_featured': True},
            {'name': 'Django', 'category': 'technical', 'proficiency': 'expert', 'years_of_experience': 4, 'is_featured': True},
            {'name': 'React.js', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 3, 'is_featured': True},
            {'name': 'JavaScript', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 4, 'is_featured': True},
            {'name': 'Machine Learning', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 2, 'is_featured': True},
            {'name': 'PostgreSQL', 'category': 'technical', 'proficiency': 'advanced', 'years_of_experience': 3, 'is_featured': True},
        ]
        
        for skill_data in skills_data:
            Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults=skill_data
            )
        
        # Create sample project
        project, created = Project.objects.get_or_create(
            title="Portfolio Django",
            defaults={
                'description': 'Portfolio professionnel développé avec Django et Bootstrap',
                'technologies': 'Django, Python, Bootstrap, JavaScript, PostgreSQL',
                'status': 'completed',
                'start_date': date.today(),
                'is_featured': True,
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Portfolio setup completed!'))