from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.db.models import Q, Count
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json
from datetime import datetime, timedelta
from .models import *
from .forms import ContactForm, TestimonialForm, SiteCustomizationForm
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

class BasePortfolioView(TemplateView):
    """Vue de base avec collecte de statistiques"""
    
    def dispatch(self, request, *args, **kwargs):
        # Collecter les statistiques de visite
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

class HomeView(BasePortfolioView):
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'profile': Profile.objects.first(),
            'featured_skills': Skill.objects.filter(is_featured=True)[:6],
            'recent_experiences': Experience.objects.all()[:3],
            'services': Service.objects.filter(is_active=True)[:4],
            'testimonials': Testimonial.objects.filter(is_approved=True, is_featured=True)[:3],
            'recent_blog_posts': BlogPost.objects.filter(is_published=True)[:3],
            'achievements': Achievement.objects.all()[:3],
            'featured_projects': Project.objects.filter(is_featured=True)[:3],
        })
        return context

class AcademicView(BasePortfolioView):
    template_name = 'portfolio/academic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'educations': Education.objects.all(),
            'skills': Skill.objects.all(),
        })
        return context

class ExperienceView(BasePortfolioView):
    template_name = 'portfolio/experience.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experiences'] = Experience.objects.all()
        return context

class CertificationView(BasePortfolioView):
    template_name = 'portfolio/certifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certifications'] = Certification.objects.all()
        return context

class ProjectListView(BasePortfolioView, ListView):
    model = Project
    template_name = 'portfolio/projects.html'
    context_object_name = 'projects'
    paginate_by = 9

class ProjectDetailView(BasePortfolioView, DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

class ContactView(BasePortfolioView):
    template_name = 'portfolio/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        context['profile'] = Profile.objects.first()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.ip_address = self.get_client_ip(request)
            contact.save()
            
            # Envoyer email de notification
            self.send_contact_email(contact)
            
            messages.success(request, _("Votre message a été envoyé avec succès !"))
            return redirect('portfolio:contact_success')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def send_contact_email(self, contact):
        try:
            subject = f"Nouveau message de {contact.name}: {contact.subject}"
            
            message = f"""
Nouveau message reçu via le formulaire de contact:

Informations du contact:
- Nom: {contact.name}
- Email: {contact.email}
- Téléphone: {contact.phone or "Non renseigné"}
- Entreprise: {contact.company or "Non renseignée"}
- Budget: {contact.budget or "Non renseigné"}
- Délai: {contact.timeline or "Non renseigné"}

Sujet: {contact.subject}

Message:
{contact.message}

---
Envoyé le {contact.created_at.strftime('%d/%m/%Y à %H:%M')}
IP: {contact.ip_address}
"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")

class ContactSuccessView(BasePortfolioView):
    template_name = 'portfolio/contact_success.html'

class TestimonialsView(BasePortfolioView):
    template_name = 'portfolio/testimonials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.filter(is_approved=True)
        return context

class TestimonialCreateView(BasePortfolioView):
    template_name = 'portfolio/testimonial_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TestimonialForm()
        context['recent_testimonials'] = Testimonial.objects.filter(is_approved=True)[:3]
        return context
    
    def post(self, request, *args, **kwargs):
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.ip_address = self.get_client_ip(request)
            testimonial.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Auto-approuver si les témoignages ne nécessitent pas de modération
            site_settings = SiteSettings.objects.first()
            if not site_settings or not site_settings.moderate_testimonials:
                testimonial.is_approved = True
                testimonial.approved_at = timezone.now()
            
            testimonial.save()
            
            # Envoyer email de notification
            self.send_testimonial_email(testimonial)
            
            messages.success(request, _("Merci pour votre témoignage !"))
            return redirect('portfolio:testimonial_success')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
    def send_testimonial_email(self, testimonial):
        try:
            subject = f"Nouveau témoignage de {testimonial.name if not testimonial.is_anonymous else 'Anonyme'}"
            
            stars = "⭐" * testimonial.rating
            
            message = f"""
Nouveau témoignage reçu:

Nom: {testimonial.name if not testimonial.is_anonymous else "Anonyme"}
Email: {testimonial.email}
Entreprise: {testimonial.company or "Non renseignée"}
Poste: {testimonial.position or "Non renseigné"}
Localisation: {testimonial.location or "Non renseignée"}
Note: {stars} ({testimonial.rating}/5 étoiles)

Témoignage:
{testimonial.content}

Projet associé: {testimonial.project_related.title if testimonial.project_related else "Aucun"}

---
Statut: {"Publié automatiquement" if testimonial.is_approved else "En attente de modération"}
Reçu le {testimonial.created_at.strftime('%d/%m/%Y à %H:%M')}
"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email témoignage: {e}")

class TestimonialSuccessView(BasePortfolioView):
    template_name = 'portfolio/testimonial_success.html'

class BlogListView(BasePortfolioView, ListView):
    model = BlogPost
    template_name = 'portfolio/blog.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        search = self.request.GET.get('search')
        tag = self.request.GET.get('tag')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
        
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_posts': BlogPost.objects.filter(is_published=True, is_featured=True)[:3],
            'popular_tags': self.get_popular_tags(),
        })
        return context
    
    def get_popular_tags(self):
        # Extraire les tags populaires des articles
        all_tags = []
        for post in BlogPost.objects.filter(is_published=True):
            if post.tags:
                all_tags.extend([tag.strip() for tag in post.tags.split(',')])
        
        # Compter les occurrences
        from collections import Counter
        tag_counts = Counter(all_tags)
        return [tag for tag, count in tag_counts.most_common(10)]

class BlogDetailView(BasePortfolioView, DetailView):
    model = BlogPost
    template_name = 'portfolio/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
    
    def get_object(self):
        obj = super().get_object()
        # Incrémenter le compteur de vues
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Articles similaires
        related_posts = BlogPost.objects.filter(
            is_published=True,
            category=post.category
        ).exclude(pk=post.pk)[:3]
        
        context.update({
            'related_posts': related_posts,
            'profile': Profile.objects.first(),
        })
        return context

class ServicesView(BasePortfolioView):
    template_name = 'portfolio/services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        return context

class FAQView(BasePortfolioView):
    template_name = 'portfolio/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'faqs': FAQ.objects.filter(is_active=True),
            'faq_categories': FAQ.objects.filter(is_active=True).values('category').annotate(count=Count('id')),
        })
        return context

class TimelineView(BasePortfolioView):
    template_name = 'portfolio/timeline.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'timeline_events': Timeline.objects.all(),
            'categories': Timeline.objects.values('category').annotate(count=Count('id')),
        })
        return context

class CollaborationsView(BasePortfolioView):
    template_name = 'portfolio/collaborations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collaborations'] = Collaboration.objects.filter(is_active=True)
        return context

class ResourcesView(BasePortfolioView):
    template_name = 'portfolio/resources.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'resources': Resource.objects.filter(is_public=True),
            'resource_categories': Resource.objects.filter(is_public=True).values('category').annotate(count=Count('id')),
        })
        return context

class AchievementsView(BasePortfolioView):
    template_name = 'portfolio/achievements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['achievements'] = Achievement.objects.all()
        return context

class UniversalSearchView(BasePortfolioView):
    template_name = 'portfolio/search_results.html'
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', 'all')
        
        if not query:
            return render(request, self.template_name, {
                'query': query,
                'results': {},
                'total_results': 0,
                'suggestions': self.get_search_suggestions(),
                'popular_searches': self.get_popular_searches(),
            })
        
        # Enregistrer la recherche
        SearchQuery.objects.create(
            query=query,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        results = self.perform_search(query, category)
        total_results = sum(len(category_results) for category_results in results.values())
        
        return render(request, self.template_name, {
            'query': query,
            'category': category,
            'results': results,
            'total_results': total_results,
            'suggestions': self.get_search_suggestions() if total_results == 0 else [],
        })
    
    def perform_search(self, query, category):
        results = {}
        
        if category in ['all', 'projects']:
            results['projects'] = self.search_projects(query)
        
        if category in ['all', 'experiences']:
            results['experiences'] = self.search_experiences(query)
        
        if category in ['all', 'skills']:
            results['skills'] = self.search_skills(query)
        
        if category in ['all', 'blog']:
            results['blog'] = self.search_blog(query)
        
        if category in ['all', 'certifications']:
            results['certifications'] = self.search_certifications(query)
        
        if category in ['all', 'testimonials']:
            results['testimonials'] = self.search_testimonials(query)
        
        if category in ['all', 'faq']:
            results['faq'] = self.search_faq(query)
        
        if category in ['all', 'resources']:
            results['resources'] = self.search_resources(query)
        
        return results
    
    def search_projects(self, query):
        projects = Project.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(technologies__icontains=query) |
            Q(client__icontains=query)
        )
        
        return [{
            'title': project.title,
            'description': project.description,
            'type': 'Projet',
            'url': project.get_absolute_url(),
            'image': project.image.url if project.image else None,
            'date': project.start_date,
            'tags': project.technologies.split(',') if project.technologies else [],
        } for project in projects]
    
    def search_experiences(self, query):
        experiences = Experience.objects.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query) |
            Q(technologies__icontains=query)
        )
        
        return [{
            'title': f"{exp.title} - {exp.company}",
            'description': exp.description,
            'type': 'Expérience',
            'url': reverse('portfolio:experience'),
            'date': exp.start_date,
            'tags': exp.technologies.split(',') if exp.technologies else [],
        } for exp in experiences]
    
    def search_skills(self, query):
        skills = Skill.objects.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query)
        )
        
        return [{
            'title': skill.name,
            'description': f"{skill.get_category_display()} - {skill.get_proficiency_display()}",
            'type': 'Compétence',
            'url': reverse('portfolio:academic'),
            'tags': [skill.category, skill.proficiency],
        } for skill in skills]
    
    def search_blog(self, query):
        posts = BlogPost.objects.filter(
            is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )
        
        return [{
            'title': post.title,
            'description': post.excerpt or post.content[:200],
            'type': 'Article',
            'url': post.get_absolute_url(),
            'image': post.featured_image.url if post.featured_image else None,
            'date': post.published_at,
            'tags': post.tags.split(',') if post.tags else [],
        } for post in posts]
    
    def search_certifications(self, query):
        certifications = Certification.objects.filter(
            Q(name__icontains=query) |
            Q(issuing_organization__icontains=query) |
            Q(credential_id__icontains=query)
        )
        
        return [{
            'title': cert.name,
            'description': f"Délivré par {cert.issuing_organization}",
            'type': 'Certification',
            'url': reverse('portfolio:certifications'),
            'date': cert.issue_date,
            'tags': [cert.issuing_organization],
        } for cert in certifications]
    
    def search_testimonials(self, query):
        testimonials = Testimonial.objects.filter(
            is_approved=True
        ).filter(
            Q(content__icontains=query) |
            Q(name__icontains=query) |
            Q(company__icontains=query)
        )
        
        return [{
            'title': f"Témoignage de {test.name if not test.is_anonymous else 'Anonyme'}",
            'description': test.content,
            'type': 'Témoignage',
            'url': reverse('portfolio:testimonials'),
            'tags': [test.company] if test.company else [],
        } for test in testimonials]
    
    def search_faq(self, query):
        faqs = FAQ.objects.filter(
            is_active=True
        ).filter(
            Q(question__icontains=query) |
            Q(answer__icontains=query)
        )
        
        return [{
            'title': faq.question,
            'description': faq.answer[:200],
            'type': 'FAQ',
            'url': reverse('portfolio:faq'),
            'tags': [faq.category],
        } for faq in faqs]
    
    def search_resources(self, query):
        resources = Resource.objects.filter(
            is_public=True
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
        
        return [{
            'title': resource.title,
            'description': resource.description,
            'type': 'Ressource',
            'url': reverse('portfolio:resource_download', kwargs={'resource_id': resource.id}),
            'tags': [resource.category, resource.file_type],
        } for resource in resources]
    
    def get_search_suggestions(self):
        # Suggestions basées sur les recherches populaires
        popular = SearchQuery.objects.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return [item['query'] for item in popular]
    
    def get_popular_searches(self):
        return SearchQuery.objects.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

class DownloadCVView(View):
    def get(self, request, *args, **kwargs):
        cv_type = request.GET.get('type', 'main')
        language = request.GET.get('lang', 'fr')
        
        # Chercher un CV correspondant
        cv = CVDocument.objects.filter(
            is_public=True,
            cv_type=cv_type,
            language=language
        ).first()
        
        if not cv:
            # Chercher le CV principal
            cv = CVDocument.objects.filter(is_primary=True, is_public=True).first()
        
        if cv and cv.file:
            # Incrémenter le compteur
            cv.download_count += 1
            cv.save(update_fields=['download_count'])
            
            # Retourner le fichier
            response = HttpResponse(cv.file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{cv.title}.pdf"'
            return response
        
        # Générer un CV automatique si aucun fichier n'est disponible
        return self.generate_auto_cv(request)
    
    def generate_auto_cv(self, request):
        profile = Profile.objects.first()
        if not profile:
            raise Http404("CV non disponible")
        
        # Créer un PDF simple
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Titre
        title = Paragraph(f"<b>{profile.name}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Sous-titre
        subtitle = Paragraph(profile.title, styles['Heading2'])
        story.append(subtitle)
        story.append(Spacer(1, 12))
        
        # Contact
        contact_info = f"""
        <b>Contact:</b><br/>
        Email: {profile.email}<br/>
        Téléphone: {profile.phone or 'Non renseigné'}<br/>
        Localisation: {profile.location or 'Non renseignée'}
        """
        story.append(Paragraph(contact_info, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Bio
        bio = Paragraph(f"<b>Profil:</b><br/>{profile.bio}", styles['Normal'])
        story.append(bio)
        
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CV_{profile.name.replace(" ", "_")}.pdf"'
        return response

class CVListView(BasePortfolioView):
    template_name = 'portfolio/cv_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'cv_documents': CVDocument.objects.filter(is_public=True),
            'cv_types': CVDocument.CV_TYPES,
            'languages': [('fr', 'Français'), ('en', 'English'), ('ar', 'العربية')],
        })
        return context

class ResourceDownloadView(View):
    def get(self, request, resource_id):
        resource = get_object_or_404(Resource, id=resource_id, is_public=True)
        
        # Incrémenter le compteur
        resource.download_count += 1
        resource.save(update_fields=['download_count'])
        
        # Retourner le fichier
        response = HttpResponse(resource.file.read())
        response['Content-Disposition'] = f'attachment; filename="{resource.title}"'
        return response

# Admin Views
class AdminDashboardView(UserPassesTestMixin, BasePortfolioView):
    template_name = 'portfolio/admin/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context.update({
            'total_projects': Project.objects.count(),
            'total_experiences': Experience.objects.count(),
            'total_skills': Skill.objects.count(),
            'published_posts': BlogPost.objects.filter(is_published=True).count(),
            'total_contacts': Contact.objects.count(),
            'unread_contacts': Contact.objects.filter(is_read=False).count(),
            'total_testimonials': Testimonial.objects.count(),
            'pending_testimonials': Testimonial.objects.filter(is_approved=False).count(),
            'recent_visits': VisitorStats.objects.filter(
                visit_date__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'unique_visitors': VisitorStats.objects.filter(
                visit_date__gte=timezone.now() - timedelta(days=30)
            ).values('ip_address').distinct().count(),
            'recent_contacts': Contact.objects.all()[:5],
            'recent_testimonials': Testimonial.objects.all()[:5],
            'popular_pages': VisitorStats.objects.values('page_visited').annotate(
                count=Count('id')
            ).order_by('-count')[:5],
        })
        return context

class AdminCustomizationView(UserPassesTestMixin, BasePortfolioView):
    template_name = 'portfolio/admin/customization.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customization = SiteCustomization.objects.filter(is_active=True).first()
        context['form'] = SiteCustomizationForm(instance=customization)
        return context
    
    def post(self, request, *args, **kwargs):
        customization = SiteCustomization.objects.filter(is_active=True).first()
        form = SiteCustomizationForm(request.POST, request.FILES, instance=customization)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Personnalisation sauvegardée avec succès !")
            return redirect('portfolio:admin_customization')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

class AdvancedAnalyticsView(UserPassesTestMixin, BasePortfolioView):
    template_name = 'portfolio/analytics.html'
    
    def test_func(self):
        return self.request.user.is_superuser

# API Views
class ContactAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            form = ContactForm(data)
            
            if form.is_valid():
                contact = form.save(commit=False)
                contact.ip_address = self.get_client_ip(request)
                contact.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Message envoyé avec succès !'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur dans le formulaire',
                    'errors': form.errors
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

class NewsletterAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name', '')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email requis'
                })
            
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            
            if created:
                # Envoyer email de notification
                self.send_newsletter_email(newsletter)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Inscription réussie à la newsletter !'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Cet email est déjà inscrit'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    def send_newsletter_email(self, newsletter):
        try:
            subject = "Nouvelle inscription newsletter"
            
            message = f"""
Nouvelle inscription à votre newsletter:

Email: {newsletter.email}
Nom: {newsletter.name or "Non renseigné"}
Date d'inscription: {newsletter.subscribed_at.strftime('%d/%m/%Y à %H:%M')}

Total d'abonnés actifs: {Newsletter.objects.filter(is_active=True).count()}

Vous pouvez gérer les abonnés dans l'admin Django.
"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email newsletter: {e}")

class NewsletterSubscribeView(View):
    def post(self, request):
        return NewsletterAPIView().post(request)

class StatsAPIView(View):
    def get(self, request):
        stats = {
            'total_projects': Project.objects.count(),
            'total_skills': Skill.objects.count(),
            'experience_years': Profile.objects.first().years_of_experience if Profile.objects.first() else 0,
            'recent_visits': VisitorStats.objects.filter(
                visit_date__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })

class SearchSuggestionsAPIView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # Rechercher dans différents modèles
        suggestions = set()
        
        # Projets
        projects = Project.objects.filter(title__icontains=query)[:3]
        suggestions.update([p.title for p in projects])
        
        # Compétences
        skills = Skill.objects.filter(name__icontains=query)[:3]
        suggestions.update([s.name for s in skills])
        
        # Technologies
        for project in Project.objects.all():
            if project.technologies:
                techs = [t.strip() for t in project.technologies.split(',')]
                for tech in techs:
                    if query.lower() in tech.lower():
                        suggestions.add(tech)
        
        return JsonResponse({
            'suggestions': list(suggestions)[:10]
        })

class TagCloudAPIView(View):
    def get(self, request):
        # Collecter tous les tags
        tags_data = []
        
        # Tags des projets
        for project in Project.objects.all():
            if project.technologies:
                techs = [t.strip() for t in project.technologies.split(',')]
                for tech in techs:
                    tags_data.append({
                        'name': tech,
                        'url': f"/search/?q={tech}",
                        'color': '#007bff',
                        'count': 1
                    })
        
        # Compter les occurrences
        from collections import Counter
        tag_names = [tag['name'] for tag in tags_data]
        tag_counts = Counter(tag_names)
        
        # Créer la réponse
        tags = []
        colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#6f42c1', '#fd7e14']
        
        for i, (name, count) in enumerate(tag_counts.most_common(20)):
            tags.append({
                'name': name,
                'count': count,
                'url': f"/search/?q={name}",
                'color': colors[i % len(colors)]
            })
        
        return JsonResponse({'tags': tags})

class CustomizationPreviewAPIView(View):
    def post(self, request):
        # API pour prévisualiser les changements de personnalisation
        return JsonResponse({'success': True})

class FAQHelpfulAPIView(View):
    def post(self, request, faq_id):
        try:
            faq = get_object_or_404(FAQ, id=faq_id)
            faq.helpful_votes += 1
            faq.save(update_fields=['helpful_votes'])
            
            return JsonResponse({
                'success': True,
                'new_count': faq.helpful_votes
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })