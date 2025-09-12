from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
import json
from datetime import datetime, timedelta
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.serializers import serialize

from .models import (
    Profile, Education, Experience, Skill, Certification, Project, 
    Contact, SiteSettings, BlogPost, BlogCategory, Testimonial, 
    Service, Achievement, Newsletter, VisitorStats, SiteCustomization
)
from .models import Tag, FAQ, Timeline, Collaboration, Resource, Analytics, SearchQuery as SearchQueryModel
from .forms import ContactForm, TestimonialForm, SiteCustomizationForm, NewsletterForm

class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['popular_tags'] = Tag.objects.filter(is_featured=True)[:10]
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
        return context

    def dispatch(self, request, *args, **kwargs):
        # Enregistrer les statistiques de visite
        if hasattr(request, 'META'):
            try:
                VisitorStats.objects.create(
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    page_visited=request.path,
                    referrer=request.META.get('HTTP_REFERER', ''),
                    session_id=request.session.session_key or ''
                )
            except:
                pass  # Ignore errors in stats collection
        return super().dispatch(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_search_query(self, request, query, results_count):
        """Enregistrer les requêtes de recherche pour analytics"""
        try:
            SearchQueryModel.objects.create(
                query=query,
                results_count=results_count,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except:
            pass



class HomeView(BaseView):
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['featured_projects'] = Project.objects.filter(is_featured=True)[:3]
            # Utilisation de only() pour spécifier les champs nécessaires uniquement
            context['featured_skills'] = Skill.objects.filter(is_featured=True).only('name', 'category', 'proficiency')[:6]
            context['recent_experiences'] = Experience.objects.all()[:3]
            context['testimonials'] = Testimonial.objects.filter(is_featured=True, is_approved=True)[:3]
            context['services'] = Service.objects.filter(is_active=True)[:4]
            context['recent_blog_posts'] = BlogPost.objects.filter(is_published=True)[:3]
            context['achievements'] = Achievement.objects.all()[:3]
            context['timeline_events'] = Timeline.objects.filter(is_milestone=True)[:5]
            context['collaborations'] = Collaboration.objects.filter(is_ongoing=True)[:6]
            context['faq_items'] = FAQ.objects.filter(is_active=True, category='general')[:3]
            context['popular_resources'] = Resource.objects.filter(is_public=True).order_by('-download_count')[:3]
        except Exception as e:
            # Ajout d'un message d'erreur pour le débogage
            print(f"Erreur lors du chargement des données: {e}")
            # Si les tables n'existent pas encore, retourne des listes vides
            context['featured_projects'] = []
            context['featured_skills'] = []
            context['recent_experiences'] = []
            context['testimonials'] = []
            context['services'] = []
            context['recent_blog_posts'] = []
            context['achievements'] = []
            context['timeline_events'] = []
            context['collaborations'] = []
            context['faq_items'] = []
            context['popular_resources'] = []
        return context



class AcademicView(BaseView):
    template_name = 'portfolio/academic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['educations'] = Education.objects.all()
        context['skills'] = Skill.objects.all()
        return context

class ExperienceView(BaseView):
    template_name = 'portfolio/experience.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experiences'] = Experience.objects.all()
        # Grouper par catégorie
        context['professional_experiences'] = Experience.objects.filter(category='professional')
        context['academic_experiences'] = Experience.objects.filter(category='academic')
        context['volunteer_experiences'] = Experience.objects.filter(category='volunteer')
        context['personal_experiences'] = Experience.objects.filter(category='personal')
        context['creative_experiences'] = Experience.objects.filter(category='creative')
        context['sports_experiences'] = Experience.objects.filter(category='sports')
        context['other_experiences'] = Experience.objects.filter(category='other')
        return context

class CertificationView(BaseView):
    template_name = 'portfolio/certifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certifications'] = Certification.objects.all()
        return context

class ProjectListView(ListView):
    model = Project
    template_name = 'portfolio/projects.html'
    context_object_name = 'projects'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Project.objects.all()
        
        # Filtrage par type
        project_type = self.request.GET.get('type')
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Filtrage par statut
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtrage par projets vedettes
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(technologies__icontains=search) |
                Q(client__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
            context['search_query'] = self.request.GET.get('search', '')
            context['current_type'] = self.request.GET.get('type', '')
            context['current_status'] = self.request.GET.get('status', '')
            context['show_featured'] = self.request.GET.get('featured', '')
            context['project_types'] = Project.PROJECT_TYPES
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
            # Projets similaires
            context['related_projects'] = Project.objects.filter(
                project_type=self.object.project_type
            ).exclude(id=self.object.id)[:3]
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
            context['related_projects'] = []
        return context

class ContactView(FormView):
    template_name = 'portfolio/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('portfolio:contact_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
        return context
    
    def form_valid(self, form):
        # Sauvegarder le message
        contact = form.save(commit=False)
        contact.ip_address = self.get_client_ip()
        contact.save()
        
        # Envoyer l'email
        try:
            subject = f"Nouveau message de {contact.name}: {contact.subject}"
            message = f"""
Nouveau message reçu via le formulaire de contact:

Nom: {contact.name}
Email: {contact.email}
Téléphone: {contact.phone or 'Non renseigné'}
Entreprise: {contact.company or 'Non renseignée'}
Budget: {contact.budget or 'Non renseigné'}
Délai: {contact.timeline or 'Non renseigné'}

Sujet: {contact.subject}

Message:
{contact.message}

---
Envoyé le {contact.created_at.strftime('%d/%m/%Y à %H:%M')}
IP: {contact.ip_address}
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(self.request, _("Erreur lors de l'envoi de l'email."))
        
        messages.success(self.request, _("Votre message a été envoyé avec succès! Je vous répondrai dans les plus brefs délais."))
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class ContactSuccessView(BaseView):
    template_name = 'portfolio/contact_success.html'

class TestimonialCreateView(CreateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'portfolio/testimonial_form.html'
    success_url = reverse_lazy('portfolio:testimonial_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
        return context
    
    def form_valid(self, form):
        # Vérifier si les témoignages sont autorisés
        site_settings = SiteSettings.objects.first()
        if site_settings and not site_settings.allow_testimonials:
            messages.error(self.request, _("Les témoignages ne sont pas autorisés actuellement."))
            return redirect('portfolio:home')
        
        testimonial = form.save(commit=False)
        testimonial.ip_address = self.get_client_ip()
        testimonial.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # Si la modération est activée, ne pas approuver automatiquement
        if site_settings and site_settings.moderate_testimonials:
            testimonial.is_approved = False
        else:
            testimonial.is_approved = True
            testimonial.approved_at = timezone.now()
        
        # Gérer l'anonymat
        if testimonial.is_anonymous:
            testimonial.name = ""
            testimonial.email = ""
            testimonial.company = ""
            testimonial.position = ""
            testimonial.location = ""
            testimonial.website = ""
            testimonial.phone = ""
        
        testimonial.save()
        
        if site_settings and site_settings.moderate_testimonials:
            messages.success(self.request, _("Merci pour votre témoignage! Il sera publié après modération."))
        else:
            messages.success(self.request, _("Merci pour votre témoignage! Il a été publié avec succès."))
        
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class TestimonialSuccessView(BaseView):
    template_name = 'portfolio/testimonial_success.html'

class BlogListView(ListView):
    model = BlogPost
    template_name = 'portfolio/blog.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        
        # Recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        # Filtrage par catégorie
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filtrage par tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        return queryset.order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
            context['featured_posts'] = BlogPost.objects.filter(is_featured=True, is_published=True)[:3]
            context['categories'] = BlogCategory.objects.filter(is_active=True)
            
            # Extraire tous les tags
            all_posts = BlogPost.objects.filter(is_published=True)
            tags = []
            for post in all_posts:
                if post.tags:
                    tags.extend([tag.strip() for tag in post.tags.split(',')])
            context['popular_tags'] = list(set(tags))[:10]
            
            context['search_query'] = self.request.GET.get('search', '')
            context['current_category'] = self.request.GET.get('category', '')
            context['current_tag'] = self.request.GET.get('tag', '')
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
            context['featured_posts'] = []
            context['categories'] = []
            context['popular_tags'] = []
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'portfolio/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Incrémenter le compteur de vues
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['site_customization'] = SiteCustomization.objects.filter(is_active=True).first()
            
            # Articles similaires (même catégorie)
            related_posts = BlogPost.objects.filter(
                is_published=True,
                category=self.object.category
            ).exclude(id=self.object.id)[:3]
            
            if len(related_posts) < 3:
                # Compléter avec d'autres articles récents
                additional_posts = BlogPost.objects.filter(
                    is_published=True
                ).exclude(id=self.object.id).exclude(
                    id__in=[p.id for p in related_posts]
                )[:3-len(related_posts)]
                related_posts = list(related_posts) + list(additional_posts)
            
            context['related_posts'] = related_posts
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['site_customization'] = None
            context['related_posts'] = []
        return context

class ServicesView(BaseView):
    template_name = 'portfolio/services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True).order_by('order')
        return context

class TestimonialsView(BaseView):
    template_name = 'portfolio/testimonials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.filter(is_approved=True)
        context['featured_testimonials'] = Testimonial.objects.filter(is_featured=True, is_approved=True)
        return context

class AchievementsView(BaseView):
    template_name = 'portfolio/achievements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['achievements'] = Achievement.objects.all()
        return context

# Admin Views (Protected)
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

# Nouvelles vues avancées

class UniversalSearchView(BaseView):
    """Recherche universelle dans tout le contenu"""
    template_name = 'portfolio/search_results.html'
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', 'all')
        
        if not query:
            return render(request, self.template_name, {
                'query': query,
                'results': [],
                'total_results': 0,
                'suggestions': self.get_search_suggestions(),
                'popular_searches': self.get_popular_searches(),
            })
        
        results = self.perform_universal_search(query, category)
        total_results = sum(len(category_results) for category_results in results.values())
        
        # Enregistrer la recherche
        self.log_search_query(request, query, total_results)
        
        context = {
            'query': query,
            'category': category,
            'results': results,
            'total_results': total_results,
            'suggestions': self.get_search_suggestions(query),
            'popular_searches': self.get_popular_searches(),
        }
        
        return render(request, self.template_name, context)
    
    def perform_universal_search(self, query, category='all'):
        """Effectuer une recherche dans tous les contenus"""
        results = {}
        
        # Recherche dans les projets
        if category in ['all', 'projects']:
            projects = Project.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(detailed_description__icontains=query) |
                Q(technologies__icontains=query) |
                Q(client__icontains=query) |
                Q(challenges_faced__icontains=query)
            )
            results['projects'] = [{
                'title': p.title,
                'description': p.description,
                'url': p.get_absolute_url(),
                'type': 'Projet',
                'date': p.start_date,
                'tags': p.technologies.split(',') if p.technologies else [],
                'image': p.image.url if p.image else None,
            } for p in projects]
        
        # Recherche dans les expériences
        if category in ['all', 'experiences']:
            experiences = Experience.objects.filter(
                Q(title__icontains=query) |
                Q(company__icontains=query) |
                Q(description__icontains=query) |
                Q(achievements__icontains=query) |
                Q(technologies__icontains=query)
            )
            results['experiences'] = [{
                'title': f"{e.title} - {e.company}",
                'description': e.description,
                'url': '/experience/',
                'type': 'Expérience',
                'date': e.start_date,
                'tags': e.technologies.split(',') if e.technologies else [],
            } for e in experiences]
        
        # Recherche dans les compétences
        if category in ['all', 'skills']:
            skills = Skill.objects.filter(
                Q(name__icontains=query) |
                Q(certification_level__icontains=query)
            )
            results['skills'] = [{
                'title': s.name,
                'description': f"{s.get_category_display()} - {s.get_proficiency_display()}",
                'url': '/academic/',
                'type': 'Compétence',
                'tags': [s.get_category_display(), s.get_proficiency_display()],
            } for s in skills]
        
        # Recherche dans le blog
        if category in ['all', 'blog']:
            blog_posts = BlogPost.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__icontains=query)
            )
            results['blog'] = [{
                'title': b.title,
                'description': b.excerpt or b.content[:200],
                'url': b.get_absolute_url(),
                'type': 'Article',
                'date': b.published_at,
                'tags': b.tags.split(',') if b.tags else [],
                'image': b.featured_image.url if b.featured_image else None,
            } for b in blog_posts]
        
        # Recherche dans les certifications
        if category in ['all', 'certifications']:
            certifications = Certification.objects.filter(
                Q(name__icontains=query) |
                Q(issuing_organization__icontains=query) |
                Q(credential_id__icontains=query)
            )
            results['certifications'] = [{
                'title': c.name,
                'description': f"Délivré par {c.issuing_organization}",
                'url': '/certifications/',
                'type': 'Certification',
                'date': c.issue_date,
                'tags': [c.issuing_organization],
            } for c in certifications]
        
        # Recherche dans les témoignages
        if category in ['all', 'testimonials']:
            testimonials = Testimonial.objects.filter(
                is_approved=True
            ).filter(
                Q(content__icontains=query) |
                Q(name__icontains=query) |
                Q(company__icontains=query) |
                Q(position__icontains=query)
            )
            results['testimonials'] = [{
                'title': f"Témoignage de {t.name if not t.is_anonymous else 'Anonyme'}",
                'description': t.content[:200],
                'url': '/testimonials/',
                'type': 'Témoignage',
                'date': t.created_at,
                'tags': [t.company] if t.company else [],
            } for t in testimonials]
        
        # Recherche dans les FAQ
        if category in ['all', 'faq']:
            faqs = FAQ.objects.filter(
                is_active=True
            ).filter(
                Q(question__icontains=query) |
                Q(answer__icontains=query)
            )
            results['faq'] = [{
                'title': f.question,
                'description': f.answer[:200],
                'url': '/faq/',
                'type': 'FAQ',
                'tags': [f.get_category_display()],
            } for f in faqs]
        
        # Recherche dans les ressources
        if category in ['all', 'resources']:
            resources = Resource.objects.filter(
                is_public=True
            ).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            results['resources'] = [{
                'title': r.title,
                'description': r.description,
                'url': f'/resources/{r.id}/',
                'type': 'Ressource',
                'date': r.created_at,
                'tags': [r.get_category_display(), r.get_file_type_display()],
            } for r in resources]
        
        return results
    
    def get_search_suggestions(self, query=None):
        """Obtenir des suggestions de recherche"""
        if query:
            # Suggestions basées sur la requête actuelle
            tags = Tag.objects.filter(name__icontains=query)[:5]
            return [tag.name for tag in tags]
        else:
            # Suggestions populaires
            return Tag.objects.filter(is_featured=True).values_list('name', flat=True)[:10]
    
    def get_popular_searches(self):
        """Obtenir les recherches populaires"""
        return SearchQueryModel.objects.values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:10]

class AdminDashboardView(SuperuserRequiredMixin, TemplateView):
    template_name = 'portfolio/admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques générales
        context['total_projects'] = Project.objects.count()
        context['total_experiences'] = Experience.objects.count()
        context['total_skills'] = Skill.objects.count()
        context['total_blog_posts'] = BlogPost.objects.count()
        context['published_posts'] = BlogPost.objects.filter(is_published=True).count()
        context['total_testimonials'] = Testimonial.objects.count()
        context['pending_testimonials'] = Testimonial.objects.filter(is_approved=False).count()
        context['total_contacts'] = Contact.objects.count()
        context['unread_contacts'] = Contact.objects.filter(is_read=False).count()
        
        # Statistiques de visite (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['recent_visits'] = VisitorStats.objects.filter(visit_date__gte=thirty_days_ago).count()
        context['unique_visitors'] = VisitorStats.objects.filter(
            visit_date__gte=thirty_days_ago
        ).values('ip_address').distinct().count()
        
        # Nouvelles statistiques avancées
        context['total_tags'] = Tag.objects.count()
        context['total_searches'] = SearchQueryModel.objects.count()
        context['total_faq'] = FAQ.objects.filter(is_active=True).count()
        context['total_resources'] = Resource.objects.filter(is_public=True).count()
        context['total_collaborations'] = Collaboration.objects.count()
        context['recent_searches'] = SearchQueryModel.objects.order_by('-search_date')[:10]
        context['popular_tags'] = Tag.objects.order_by('-usage_count')[:10]
        
        # Pages les plus visitées
        context['popular_pages'] = VisitorStats.objects.filter(
            visit_date__gte=thirty_days_ago
        ).values('page_visited').annotate(
            count=Count('page_visited')
        ).order_by('-count')[:5]
        
        # Contacts récents
        context['recent_contacts'] = Contact.objects.order_by('-created_at')[:5]
        
        # Témoignages récents
        context['recent_testimonials'] = Testimonial.objects.order_by('-created_at')[:5]
        
        return context

class FAQView(BaseView):
    template_name = 'portfolio/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faq_categories'] = FAQ.objects.filter(is_active=True).values('category').annotate(
            count=Count('category')
        ).order_by('category')
        context['faqs'] = FAQ.objects.filter(is_active=True).order_by('category', 'order')
        return context

class TimelineView(BaseView):
    template_name = 'portfolio/timeline.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timeline_events'] = Timeline.objects.all().order_by('-date')
        context['categories'] = Timeline.objects.values('category').annotate(
            count=Count('category')
        ).order_by('category')
        return context

# views.py
from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Count
from .models import Collaboration

class CollaborationsView(ListView):
    model = Collaboration
    template_name = 'portfolio/collaborations.html'
    context_object_name = 'collaborations'
    
    def get_queryset(self):
        return Collaboration.objects.filter(is_active=True).order_by('order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les catégories pour les filtres si nécessaire
        context['categories'] = Collaboration.objects.values('category').annotate(
            count=Count('category')
        ).order_by('category')
        return context

# views.py - Modifiez la classe ResourcesView
class ResourcesView(BaseView):
    template_name = 'portfolio/resources.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resources = Resource.objects.filter(is_public=True).order_by('-created_at')
        
        # Calculer les statistiques
        total_downloads = sum(resource.download_count for resource in resources)
        total_size = sum(resource.file_size or 0 for resource in resources)
        
        context['resources'] = resources
        context['resource_categories'] = Resource.objects.filter(is_public=True).values('category').annotate(
            count=Count('category')
        ).order_by('category')
        context['total_downloads'] = total_downloads
        context['total_size'] = total_size
        
        return context

class ResourceDownloadView(BaseView):
    def get(self, request, resource_id):
        resource = get_object_or_404(Resource, id=resource_id, is_public=True)
        resource.download_count += 1
        resource.save()
        
        response = HttpResponse(resource.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{resource.file.name}"'
        return response

class AdvancedAnalyticsView(SuperuserRequiredMixin, TemplateView):
    template_name = 'portfolio/admin/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Analytics des 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Statistiques de recherche
        search_stats = SearchQueryModel.objects.filter(
            search_date__gte=thirty_days_ago
        ).values('query').annotate(
            count=Count('query'),
            avg_results=Avg('results_count')
        ).order_by('-count')[:20]
        
        context['search_stats'] = search_stats
        
        # Statistiques des tags
        tag_stats = Tag.objects.annotate(
            projects_count=Count('project'),
            blog_posts_count=Count('blogpost_set'),
            total_usage=Count('project') + Count('blogpost_set')
        ).order_by('-total_usage')[:15]
        
        context['tag_stats'] = tag_stats
        
        # Statistiques des téléchargements
        download_stats = Resource.objects.filter(
            is_public=True
        ).order_by('-download_count')[:10]
        
        context['download_stats'] = download_stats
        
        # FAQ les plus consultées
        faq_stats = FAQ.objects.filter(
            is_active=True
        ).order_by('-views_count')[:10]
        
        context['faq_stats'] = faq_stats
        
        return context

# API Views pour AJAX
class SearchSuggestionsAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # Suggestions de tags
        tag_suggestions = Tag.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        
        # Suggestions de projets
        project_suggestions = Project.objects.filter(
            title__icontains=query
        ).values_list('title', flat=True)[:3]
        
        # Suggestions de compétences
        skill_suggestions = Skill.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        # Suggestions de recherches populaires
        popular_suggestions = SearchQueryModel.objects.filter(
            query__icontains=query
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count').values_list('query', flat=True)[:3]
        
        all_suggestions = list(tag_suggestions) + list(project_suggestions) + \
                         list(skill_suggestions) + list(popular_suggestions)
        
        # Supprimer les doublons et limiter
        unique_suggestions = list(dict.fromkeys(all_suggestions))[:10]
        
        return JsonResponse({'suggestions': unique_suggestions})

class TagCloudAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        tags = Tag.objects.annotate(
            total_usage=Count('project') + Count('blogpost_set')
        ).filter(total_usage__gt=0).order_by('-total_usage')[:50]
        
        tag_data = [{
            'name': tag.name,
            'count': tag.total_usage,
            'color': tag.color,
            'url': f'/search/?q={tag.name}'
        } for tag in tags]
        
        return JsonResponse({'tags': tag_data})

class AdminCustomizationView(SuperuserRequiredMixin, FormView):
    template_name = 'portfolio/admin/customization.html'
    form_class = SiteCustomizationForm
    success_url = reverse_lazy('portfolio:admin_customization')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Charger la personnalisation active ou créer une nouvelle
        customization = SiteCustomization.objects.filter(is_active=True).first()
        if customization:
            kwargs['instance'] = customization
        return kwargs
    
    def form_valid(self, form):
        customization = form.save(commit=False)
        customization.is_active = True
        
        # Désactiver les autres personnalisations
        SiteCustomization.objects.exclude(pk=customization.pk).update(is_active=False)
        customization.save()
        
        messages.success(self.request, _("Personnalisation sauvegardée avec succès!"))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_customization'] = SiteCustomization.objects.filter(is_active=True).first()
        context['all_customizations'] = SiteCustomization.objects.all()[:10]
        return context

# API Views
@method_decorator(csrf_exempt, name='dispatch')
class ContactAPIView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            contact = Contact.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                company=data.get('company', ''),
                subject=data.get('subject'),
                message=data.get('message'),
                budget=data.get('budget', ''),
                timeline=data.get('timeline', ''),
                ip_address=self.get_client_ip(request)
            )
            
            # Envoyer l'email
            try:
                send_mail(
                    subject=f"Nouveau message de {contact.name}: {contact.subject}",
                    message=f"De: {contact.name} ({contact.email})\nEntreprise: {contact.company}\nTéléphone: {contact.phone}\n\nMessage:\n{contact.message}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except:
                pass
            
            return JsonResponse({'success': True, 'message': 'Message envoyé avec succès!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

@method_decorator(csrf_exempt, name='dispatch')
class NewsletterAPIView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name', '')
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Email requis'})
            
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            
            if created:
                return JsonResponse({'success': True, 'message': 'Inscription réussie!'})
            else:
                if newsletter.is_active:
                    return JsonResponse({'success': False, 'message': 'Email déjà inscrit'})
                else:
                    newsletter.is_active = True
                    newsletter.save()
                    return JsonResponse({'success': True, 'message': 'Réinscription réussie!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

class StatsAPIView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            from django.db.models import Count
            from datetime import datetime, timedelta
            
            # Statistiques générales
            total_projects = Project.objects.count()
            total_skills = Skill.objects.count()
            total_experience_years = Profile.objects.first().years_of_experience if Profile.objects.exists() else 0
            
            # Statistiques de visite (30 derniers jours)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_visits = VisitorStats.objects.filter(visit_date__gte=thirty_days_ago).count()
            
            # Pages les plus visitées
            popular_pages = VisitorStats.objects.filter(
                visit_date__gte=thirty_days_ago
            ).values('page_visited').annotate(
                count=Count('page_visited')
            ).order_by('-count')[:5]
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_projects': total_projects,
                    'total_skills': total_skills,
                    'experience_years': total_experience_years,
                    'recent_visits': recent_visits,
                    'popular_pages': list(popular_pages)
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

class DownloadCVView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.first()
            if profile and profile.cv_file:
                response = HttpResponse(profile.cv_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="CV_{profile.name.replace(" ", "_")}.pdf"'
                return response
            else:
                raise Http404("CV non disponible")
        except Exception:
            raise Http404("CV non disponible")

class FAQHelpfulAPIView(TemplateView):
    def post(self, request, faq_id):
        try:
            faq = get_object_or_404(FAQ, id=faq_id)
            faq.helpful_votes += 1
            faq.save()
            return JsonResponse({'success': True, 'votes': faq.helpful_votes})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

class NewsletterSubscribeView(TemplateView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name', '')
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Email requis'})
            
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            
            if created:
                return JsonResponse({'success': True, 'message': 'Inscription réussie à la newsletter!'})
            else:
                if newsletter.is_active:
                    return JsonResponse({'success': False, 'message': 'Email déjà inscrit'})
                else:
                    newsletter.is_active = True
                    newsletter.save()
                    return JsonResponse({'success': True, 'message': 'Réinscription réussie!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

# Customization API
@method_decorator(csrf_exempt, name='dispatch')
class CustomizationPreviewAPIView(SuperuserRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            
            # Créer une personnalisation temporaire pour la prévisualisation
            preview_data = {
                'primary_color': data.get('primary_color', '#007bff'),
                'secondary_color': data.get('secondary_color', '#6c757d'),
                'accent_color': data.get('accent_color', '#28a745'),
                'background_color': data.get('background_color', '#ffffff'),
                'text_color': data.get('text_color', '#333333'),
                'font_family': data.get('font_family', 'inter'),
                'heading_font_size': data.get('heading_font_size', 32),
                'body_font_size': data.get('body_font_size', 16),
                'border_radius': data.get('border_radius', 8),
                'spacing_unit': data.get('spacing_unit', 16),
            }
            
            # Générer le CSS pour la prévisualisation
            css = self.generate_preview_css(preview_data)
            
            return JsonResponse({
                'success': True,
                'css': css,
                'message': 'Prévisualisation générée'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    def generate_preview_css(self, data):
        css = f"""
        :root {{
            --primary-color: {data['primary_color']};
            --secondary-color: {data['secondary_color']};
            --accent-color: {data['accent_color']};
            --background-color: {data['background_color']};
            --text-color: {data['text_color']};
            --border-radius: {data['border_radius']}px;
            --spacing-unit: {data['spacing_unit']}px;
        }}
        
        body {{
            font-family: {data['font_family']}, sans-serif;
            font-size: {data['body_font_size']}px;
            color: var(--text-color);
            background-color: var(--background-color);
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-size: {data['heading_font_size']}px;
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }}
        
        .btn-secondary {{
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }}
        
        .text-primary {{
            color: var(--primary-color) !important;
        }}
        
        .bg-primary {{
            background-color: var(--primary-color) !important;
        }}
        
        .card {{
            border-radius: var(--border-radius);
        }}
        
        .btn {{
            border-radius: var(--border-radius);
        }}
        """
        return css