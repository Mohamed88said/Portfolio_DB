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
    Service, Achievement, Newsletter, VisitorStats, SiteCustomization,
    Tag, SearchQuery, FAQ, Timeline, Collaboration, Resource, Analytics,
    CVDocument
)

@admin.register(Profile)
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
            'fields': ('resume_summary', 'languages_spoken')
        }),
        (_('Métadonnées'), {
            'fields': ('age', 'years_of_experience', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CVDocument)
class CVDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'cv_type', 'language', 'is_primary', 'is_public', 'download_count', 'file_size_display', 'created_at')
    list_filter = ('cv_type', 'language', 'is_primary', 'is_public', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'file_size', 'file_size_formatted', 'created_at', 'updated_at')
    list_editable = ('is_primary', 'is_public')
    ordering = ['-is_primary', '-created_at']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('title', 'description', 'cv_type', 'language')
        }),
        (_('Fichier'), {
            'fields': ('file', 'file_size_formatted')
        }),
        (_('Paramètres'), {
            'fields': ('is_primary', 'is_public')
        }),
        (_('Statistiques'), {
            'fields': ('download_count', 'file_size', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_primary', 'make_public', 'make_private', 'reset_download_count']
    
    def file_size_display(self, obj):
        return obj.file_size_formatted
    file_size_display.short_description = _('Taille')
    
    def make_primary(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "Vous ne pouvez sélectionner qu'un seul CV comme principal.", level='error')
            return
        
        # Désactiver tous les autres CV principaux
        CVDocument.objects.update(is_primary=False)
        updated = queryset.update(is_primary=True)
        self.message_user(request, f"{updated} CV défini comme principal.")
    make_primary.short_description = _("Définir comme CV principal")
    
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f"{updated} CV rendu(s) public(s).")
    make_public.short_description = _("Rendre public")
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f"{updated} CV rendu(s) privé(s).")
    make_private.short_description = _("Rendre privé")
    
    def reset_download_count(self, request, queryset):
        updated = queryset.update(download_count=0)
        self.message_user(request, f"{updated} compteur(s) de téléchargement réinitialisé(s).")
    reset_download_count.short_description = _("Réinitialiser les téléchargements")

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'field_of_study', 'institution', 'start_date', 'is_current', 'grade')
    list_filter = ('degree', 'is_current', 'start_date')
    search_fields = ('field_of_study', 'institution', 'description')
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'job_type', 'start_date', 'is_current')
    list_filter = ('category', 'job_type', 'is_current', 'start_date')
    search_fields = ('title', 'company', 'description')
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'years_of_experience', 'is_featured', 'projects_count')
    list_filter = ('category', 'proficiency', 'is_featured')
    search_fields = ('name',)
    list_editable = ('is_featured',)
    ordering = ['category', 'name']

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'issue_date', 'expiration_date', 'renewal_required')
    list_filter = ('issuing_organization', 'renewal_required', 'issue_date')
    search_fields = ('name', 'issuing_organization')
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_type', 'status', 'start_date', 'is_featured', 'client')
    list_filter = ('project_type', 'status', 'is_featured', 'start_date')
    search_fields = ('title', 'description', 'technologies', 'client')
    date_hierarchy = 'start_date'
    list_editable = ('is_featured',)
    ordering = ['-start_date']

@admin.register(BlogCategory)
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

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'is_featured', 'views_count', 'published_at')
    list_filter = ('category', 'is_published', 'is_featured', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'published_at'
    ordering = ['-published_at', '-created_at']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'company', 'rating', 'is_featured', 'is_approved', 'is_anonymous', 'created_at')
    list_filter = ('rating', 'is_featured', 'is_approved', 'is_anonymous', 'created_at')
    search_fields = ('name', 'company', 'content')
    readonly_fields = ('ip_address', 'user_agent', 'created_at')
    list_editable = ('is_featured', 'is_approved')
    ordering = ['-created_at']
    
    def display_name(self, obj):
        if obj.is_anonymous:
            return _("Anonyme")
        return obj.name
    display_name.short_description = _('Nom')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_starting', 'duration', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    ordering = ['order', 'name']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organization', 'date_achieved')
    list_filter = ('category', 'date_achieved')
    search_fields = ('title', 'description', 'organization')
    date_hierarchy = 'date_achieved'
    ordering = ['-date_achieved']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'company', 'budget', 'created_at', 'is_read', 'is_replied')
    list_filter = ('is_read', 'is_replied', 'budget', 'timeline', 'created_at')
    search_fields = ('name', 'email', 'subject', 'company')
    readonly_fields = ('created_at', 'ip_address')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    ordering = ['-subscribed_at']

@admin.register(VisitorStats)
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

@admin.register(SiteCustomization)
class SiteCustomizationAdmin(admin.ModelAdmin):
    list_display = ('color_scheme', 'layout_style', 'font_family', 'is_active', 'updated_at')
    list_filter = ('color_scheme', 'layout_style', 'font_family', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    ordering = ['-updated_at']

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'maintenance_mode', 'allow_testimonials', 'moderate_testimonials')
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'usage_count', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured',)
    readonly_fields = ('usage_count', 'created_at')
    ordering = ['-usage_count', 'name']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = _('Couleur')

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'results_count', 'search_date', 'clicked_result')
    list_filter = ('search_date', 'results_count')
    search_fields = ('query', 'clicked_result')
    readonly_fields = ('query', 'results_count', 'ip_address', 'user_agent', 'search_date', 'clicked_result')
    date_hierarchy = 'search_date'
    ordering = ['-search_date']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_short', 'category', 'order', 'is_active', 'views_count', 'helpful_votes')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')
    readonly_fields = ('views_count', 'helpful_votes', 'created_at', 'updated_at')
    ordering = ['category', 'order']
    
    def question_short(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_short.short_description = _('Question')

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'is_milestone', 'color_preview')
    list_filter = ('category', 'is_milestone', 'date')
    search_fields = ('title', 'description')
    list_editable = ('is_milestone',)
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = _('Couleur')

@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'client', 'start_date', 'is_featured', 'is_active', 'order')
    list_filter = ('category', 'status', 'is_featured', 'is_active', 'start_date')
    search_fields = ('title', 'description', 'client', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_active', 'order')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    ordering = ['order', '-created_at']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'file_type', 'download_count', 'is_public', 'created_at')
    list_filter = ('category', 'file_type', 'is_public', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'file_size', 'created_at')
    list_editable = ('is_public',)
    ordering = ['-created_at']

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'page_views', 'unique_visitors', 'bounce_rate', 'avg_session_duration')
    list_filter = ('date',)
    readonly_fields = ('date', 'page_views', 'unique_visitors', 'bounce_rate', 'avg_session_duration', 'top_pages', 'referrers', 'devices', 'countries')
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False