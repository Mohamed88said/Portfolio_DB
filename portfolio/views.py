from django.shortcuts import render, get_object_or_404, redirect
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

from .models import (
    Profile, Education, Experience, Skill, Certification, Project, 
    Contact, SiteSettings, BlogPost, BlogCategory, Testimonial, 
    Service, Achievement, Newsletter, VisitorStats, SiteCustomization
)
from .forms import ContactForm, TestimonialForm, SiteCustomizationForm, NewsletterForm

class BaseView(TemplateView):
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

class HomeView(BaseView):
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['featured_projects'] = Project.objects.filter(is_featured=True)[:3]
            context['featured_skills'] = Skill.objects.filter(is_featured=True)[:6]
            context['recent_experiences'] = Experience.objects.all()[:3]
            context['testimonials'] = Testimonial.objects.filter(is_featured=True, is_approved=True)[:3]
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