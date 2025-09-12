from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import AdminSite
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import (
    Profile, Education, Experience, Skill, Certification, Project, 
    Contact, SiteSettings, BlogPost, BlogCategory, Testimonial, 
    Service, Achievement, Newsletter, VisitorStats, SiteCustomization
)
from .models import Collaboration  # Import the Collaboration model
from .models import Resource  # Import the Resource model


# Custom Admin Site
class PortfolioAdminSite(AdminSite):
    site_header = _("Administration Portfolio")
    site_title = _("Portfolio Admin")
    index_title = _("Tableau de bord")
    
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

# Create custom admin site instance
admin_site = PortfolioAdminSite(name='portfolio_admin')

@admin.register(Profile, site=admin_site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'email', 'availability_status', 'updated_at')
    search_fields = ('name', 'title', 'email')
    readonly_fields = ('created_at', 'updated_at', 'age', 'years_of_experience')
    list_filter = ('availability_status', 'updated_at')
    
    fieldsets = (
        (_('Informations personnelles'), {
            'fields': ('name', 'title', 'bio', 'short_bio', 'profile_image', 'birth_date', 'nationality')
        }),
        (_('Contact'), {
            'fields': ('email', 'phone', 'location', 'availability_status', 'hourly_rate')
        }),
        (_('Réseaux sociaux'), {
            'fields': ('linkedin', 'github', 'twitter', 'instagram', 'youtube', 'website')
        }),
        (_('Professionnel'), {
            'fields': ('resume_summary', 'languages_spoken', 'cv_file')
        }),
        (_('Métadonnées'), {
            'fields': ('age', 'years_of_experience', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Education, site=admin_site)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'field_of_study', 'institution', 'start_date', 'is_current', 'grade')
    list_filter = ('degree', 'is_current', 'start_date')
    search_fields = ('field_of_study', 'institution', 'description')
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

@admin.register(Experience, site=admin_site)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'job_type', 'start_date', 'is_current')
    list_filter = ('category', 'job_type', 'is_current', 'start_date')
    search_fields = ('title', 'company', 'description')
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('title', 'company', 'location', 'category', 'job_type')
        }),
        (_('Période'), {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        (_('Description'), {
            'fields': ('description', 'achievements', 'technologies')
        }),
        (_('Détails'), {
            'fields': ('team_size', 'budget_managed', 'key_metrics', 'references'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Skill, site=admin_site)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'years_of_experience', 'is_featured', 'projects_count')
    list_filter = ('category', 'proficiency', 'is_featured')
    search_fields = ('name',)
    list_editable = ('is_featured',)
    ordering = ['category', 'name']

@admin.register(Certification, site=admin_site)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'issue_date', 'expiration_date', 'renewal_required')
    list_filter = ('issuing_organization', 'renewal_required', 'issue_date')
    search_fields = ('name', 'issuing_organization')
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']

@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_type', 'status', 'start_date', 'is_featured', 'client')
    list_filter = ('project_type', 'status', 'is_featured', 'start_date')
    search_fields = ('title', 'description', 'technologies', 'client')
    date_hierarchy = 'start_date'
    list_editable = ('is_featured',)
    ordering = ['-start_date']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('title', 'description', 'detailed_description', 'image')
        }),
        (_('Classification'), {
            'fields': ('project_type', 'status', 'is_featured', 'client')
        }),
        (_('Technique'), {
            'fields': ('technologies', 'project_url', 'github_url')
        }),
        (_('Période et équipe'), {
            'fields': ('start_date', 'end_date', 'duration_months', 'team_members')
        }),
        (_('Gestion'), {
            'fields': ('budget', 'challenges_faced', 'lessons_learned', 'metrics', 'awards'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BlogCategory, site=admin_site)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    ordering = ['order', 'name']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = _('Couleur')

@admin.register(BlogPost, site=admin_site)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'is_featured', 'views_count', 'published_at')
    list_filter = ('category', 'is_published', 'is_featured', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'published_at'
    ordering = ['-published_at', '-created_at']
    
    fieldsets = (
        (_('Contenu'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Classification'), {
            'fields': ('category', 'tags', 'author')
        }),
        (_('Publication'), {
            'fields': ('is_published', 'is_featured', 'published_at', 'allow_comments')
        }),
        (_('SEO'), {
            'fields': ('meta_description', 'reading_time'),
            'classes': ('collapse',)
        }),
        (_('Statistiques'), {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est un nouvel objet
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Testimonial, site=admin_site)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'company', 'rating', 'is_featured', 'is_approved', 'is_anonymous', 'created_at')
    list_filter = ('rating', 'is_featured', 'is_approved', 'is_anonymous', 'created_at')
    search_fields = ('name', 'company', 'content')
    readonly_fields = ('ip_address', 'user_agent', 'created_at')
    list_editable = ('is_featured', 'is_approved')
    ordering = ['-created_at']
    
    actions = ['approve_testimonials', 'feature_testimonials']
    
    def display_name(self, obj):
        if obj.is_anonymous:
            return _("Anonyme")
        return obj.name
    display_name.short_description = _('Nom')
    
    def approve_testimonials(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_approved=True, approved_at=timezone.now())
        self.message_user(request, f"{updated} témoignage(s) approuvé(s).")
    approve_testimonials.short_description = _("Approuver les témoignages sélectionnés")
    
    def feature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} témoignage(s) mis en vedette.")
    feature_testimonials.short_description = _("Mettre en vedette")

@admin.register(Service, site=admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_starting', 'duration', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    ordering = ['order', 'name']

@admin.register(Achievement, site=admin_site)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organization', 'date_achieved')
    list_filter = ('category', 'date_achieved')
    search_fields = ('title', 'description', 'organization')
    date_hierarchy = 'date_achieved'
    ordering = ['-date_achieved']

@admin.register(Contact, site=admin_site)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'company', 'budget', 'created_at', 'is_read', 'is_replied')
    list_filter = ('is_read', 'is_replied', 'budget', 'timeline', 'created_at')
    search_fields = ('name', 'email', 'subject', 'company')
    readonly_fields = ('created_at', 'ip_address')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} message(s) marqué(s) comme lu(s).")
    mark_as_read.short_description = _("Marquer comme lu")
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(is_replied=True)
        self.message_user(request, f"{updated} message(s) marqué(s) comme répondu(s).")
    mark_as_replied.short_description = _("Marquer comme répondu")

@admin.register(Newsletter, site=admin_site)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    ordering = ['-subscribed_at']

@admin.register(VisitorStats, site=admin_site)
class VisitorStatsAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'page_visited', 'visit_date', 'referrer_domain')
    list_filter = ('visit_date', 'page_visited')
    search_fields = ('ip_address', 'page_visited')
    readonly_fields = ('ip_address', 'user_agent', 'page_visited', 'referrer', 'visit_date', 'session_id')
    date_hierarchy = 'visit_date'
    ordering = ['-visit_date']
    
    def has_add_permission(self, request):
        return False
    
    def referrer_domain(self, obj):
        if obj.referrer:
            from urllib.parse import urlparse
            return urlparse(obj.referrer).netloc
        return '-'
    referrer_domain.short_description = _('Domaine référent')

@admin.register(SiteCustomization, site=admin_site)
class SiteCustomizationAdmin(admin.ModelAdmin):
    list_display = ('color_scheme', 'layout_style', 'font_family', 'is_active', 'updated_at')
    list_filter = ('color_scheme', 'layout_style', 'font_family', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    ordering = ['-updated_at']
    
    fieldsets = (
        (_('Schéma de couleurs'), {
            'fields': ('color_scheme', 'primary_color', 'secondary_color', 'accent_color', 'background_color', 'text_color')
        }),
        (_('Typographie'), {
            'fields': ('font_family', 'heading_font_size', 'body_font_size', 'line_height')
        }),
        (_('Mise en page'), {
            'fields': ('layout_style', 'container_width', 'border_radius', 'spacing_unit')
        }),
        (_('En-tête'), {
            'fields': ('header_style', 'show_logo', 'logo_image')
        }),
        (_('Pied de page'), {
            'fields': ('footer_text', 'show_social_links')
        }),
        (_('Personnalisation avancée'), {
            'fields': ('custom_css', 'custom_js'),
            'classes': ('collapse',)
        }),
        (_('Statut'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Désactiver les autres personnalisations si celle-ci est activée
        if obj.is_active:
            SiteCustomization.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

@admin.register(SiteSettings, site=admin_site)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'maintenance_mode', 'allow_testimonials', 'moderate_testimonials')
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('site_title', 'site_description', 'site_keywords', 'contact_email')
        }),
        (_('Apparence'), {
            'fields': ('footer_text',)
        }),
        (_('Témoignages'), {
            'fields': ('allow_testimonials', 'moderate_testimonials', 'allow_anonymous_testimonials')
        }),
        (_('Maintenance et Analytics'), {
            'fields': ('maintenance_mode', 'google_analytics_id')
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

# Register the default admin site models for fallback
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(VisitorStats, VisitorStatsAdmin)
admin.site.register(SiteCustomization, SiteCustomizationAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)


# admin.py - Ajoutez cette classe
@admin.register(Collaboration, site=admin_site)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'client', 'start_date', 'is_featured', 'is_active', 'order')
    list_filter = ('category', 'status', 'is_featured', 'is_active', 'start_date')
    search_fields = ('title', 'description', 'client', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_active', 'order')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    ordering = ['order', '-created_at']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('title', 'slug', 'description', 'detailed_description', 'image')
        }),
        (_('Classification'), {
            'fields': ('category', 'status', 'is_featured', 'is_active', 'client', 'order')
        }),
        (_('Technologie et liens'), {
            'fields': ('technologies', 'project_url', 'github_url', 'demo_url')
        }),
        (_('Période et équipe'), {
            'fields': ('start_date', 'end_date', 'team_size', 'budget')
        }),
        (_('Détails du projet'), {
            'fields': ('challenges_faced', 'results_achieved'),
            'classes': ('collapse',)
        }),
        (_('Métadonnées'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_active', 'mark_as_completed']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} collaboration(s) mise(s) en vedette.")
    mark_as_featured.short_description = _("Mettre en vedette")
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} collaboration(s) activée(s).")
    mark_as_active.short_description = _("Activer")
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} collaboration(s) marquée(s) comme terminée(s).")
    mark_as_completed.short_description = _("Marquer comme terminé")




# admin.py - Ajoutez cette classe
@admin.register(Resource, site=admin_site)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'file_type', 'download_count', 'is_public', 'created_at')
    list_filter = ('category', 'file_type', 'is_public', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'file_size', 'created_at')
    list_editable = ('is_public',)
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('title', 'description', 'file')
        }),
        (_('Classification'), {
            'fields': ('category', 'file_type', 'is_public')
        }),
        (_('Statistiques'), {
            'fields': ('download_count', 'file_size', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_public', 'make_private', 'reset_download_count']
    
    def save_model(self, request, obj, form, change):
        # Calculer la taille du fichier
        if obj.file:
            obj.file_size = obj.file.size
        super().save_model(request, obj, form, change)
    
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f"{updated} ressource(s) rendue(s) publique(s).")
    make_public.short_description = _("Rendre public")
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f"{updated} ressource(s) rendue(s) privée(s).")
    make_private.short_description = _("Rendre privé")
    
    def reset_download_count(self, request, queryset):
        updated = queryset.update(download_count=0)
        self.message_user(request, f"{updated} compteur(s) de téléchargement(s) réinitialisé(s).")
    reset_download_count.short_description = _("Réinitialiser les compteurs")

admin.site.register(Resource, ResourceAdmin)
