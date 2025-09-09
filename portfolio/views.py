from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from .models import (
    Profile, Education, Experience, Skill, 
    Certification, Project, Contact, SiteSettings,
    BlogPost, Testimonial, Service, Achievement, Newsletter, VisitorStats
)
from .forms import ContactForm
import json
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator

class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['profile'] = None
            context['site_settings'] = None
        return context

    def dispatch(self, request, *args, **kwargs):
        # Enregistrer les statistiques de visite
        if hasattr(request, 'META'):
            VisitorStats.objects.create(
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                page_visited=request.path,
                referrer=request.META.get('HTTP_REFERER', ''),
                session_id=request.session.session_key or ''
            )
        return super().dispatch(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class HomeView(BaseView):
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['featured_projects'] = Project.objects.filter(is_featured=True)[:3]
            context['featured_skills'] = Skill.objects.filter(is_featured=True)
            context['recent_experiences'] = Experience.objects.all()[:3]
            context['testimonials'] = Testimonial.objects.filter(is_featured=True)[:3]
            context['services'] = Service.objects.filter(is_active=True)[:4]
            context['recent_blog_posts'] = BlogPost.objects.filter(is_published=True)[:3]
            context['achievements'] = Achievement.objects.all()[:3]
        except:
            # Si les tables n'existent pas encore, retourne des listes vides
            context['featured_projects'] = []
            context['featured_skills'] = []
            context['recent_experiences'] = []
            context['testimonials'] = []
            context['services'] = []
            context['recent_blog_posts'] = []
            context['achievements'] = []
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
        return context

class CertificationView(BaseView):
    template_name = 'portfolio/certifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certifications'] = Certification.objects.all()
        return context

# CORRECTION : Héritage simple pour ProjectListView
class ProjectListView(ListView):
    model = Project
    template_name = 'portfolio/projects.html'
    context_object_name = 'projects'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Project.objects.all()
        
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
                Q(technologies__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajout des données de base manuellement
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['search_query'] = self.request.GET.get('search', '')
            context['current_status'] = self.request.GET.get('status', '')
            context['show_featured'] = self.request.GET.get('featured', '')
        except:
            context['profile'] = None
            context['site_settings'] = None
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajout des données de base manuellement
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['profile'] = None
            context['site_settings'] = None
        return context

class ContactView(FormView):
    template_name = 'portfolio/contact.html'
    form_class = ContactForm
    success_url = '/contact/success/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajout des données de base manuellement
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['profile'] = None
            context['site_settings'] = None
        return context
    
    def form_valid(self, form):
        # Sauvegarder le message
        contact = form.save()
        
        # Envoyer l'email
        try:
            send_mail(
                subject=f"Nouveau message de {contact.name}: {contact.subject}",
                message=f"De: {contact.name} ({contact.email})\n\nMessage:\n{contact.message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(self.request, _("Erreur lors de l'envoi de l'email."))
        
        messages.success(self.request, _("Votre message a été envoyé avec succès!"))
        return super().form_valid(form)

class ContactSuccessView(TemplateView):
    template_name = 'portfolio/contact_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajout des données de base manuellement
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['profile'] = None
            context['site_settings'] = None
        return context

@method_decorator(csrf_exempt, name='dispatch')
class ContactAPIView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            contact = Contact.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                subject=data.get('subject'),
                message=data.get('message')
            )
            
            # Envoyer l'email
            try:
                send_mail(
                    subject=f"Nouveau message de {contact.name}: {contact.subject}",
                    message=f"De: {contact.name} ({contact.email})\n\nMessage:\n{contact.message}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except:
                pass
            
            return JsonResponse({'success': True, 'message': 'Message envoyé avec succès!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

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
                Q(tags__icontains=search)
            )
        
        # Filtrage par tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
            context['featured_posts'] = BlogPost.objects.filter(is_featured=True, is_published=True)[:3]
            # Extraire tous les tags
            all_posts = BlogPost.objects.filter(is_published=True)
            tags = []
            for post in all_posts:
                if post.tags:
                    tags.extend([tag.strip() for tag in post.tags.split(',')])
            context['popular_tags'] = list(set(tags))[:10]
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['featured_posts'] = []
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
            context['related_posts'] = BlogPost.objects.filter(
                is_published=True
            ).exclude(id=self.object.id)[:3]
        except:
            context['profile'] = None
            context['site_settings'] = None
            context['related_posts'] = []
        return context

class ServicesView(BaseView):
    template_name = 'portfolio/services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        return context

class TestimonialsView(BaseView):
    template_name = 'portfolio/testimonials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.all()
        return context

class AchievementsView(BaseView):
    template_name = 'portfolio/achievements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['achievements'] = Achievement.objects.all()
        return context

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
                return JsonResponse({'success': False, 'message': 'Email déjà inscrit'})
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