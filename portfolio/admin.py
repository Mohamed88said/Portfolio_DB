from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Profile, Education, Experience, Skill, 
    Certification, Project, Contact, SiteSettings,
    BlogPost, Testimonial, Service, Achievement, Newsletter, VisitorStats
    BlogPost, Testimonial, Service, Achievement, Newsletter, VisitorStats
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'email', 'updated_at')
    search_fields = ('name', 'title', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Informations personnelles'), {
            'fields': ('name', 'title', 'bio', 'profile_image')
        }),
        (_('Contact'), {
            'fields': ('email', 'phone', 'location')
        }),
        (_('Réseaux sociaux'), {
            'fields': ('linkedin', 'github', 'website')
        }),
        (_('Documents'), {
            'fields': ('cv_file',)
        }),
        (_('Métadonnées'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'field_of_study', 'institution', 'start_date', 'is_current')
    list_filter = ('degree', 'is_current', 'start_date')
    search_fields = ('field_of_study', 'institution')
    date_hierarchy = 'start_date'

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'start_date', 'is_current')
    list_filter = ('job_type', 'is_current', 'start_date')
    search_fields = ('title', 'company', 'description')
    date_hierarchy = 'start_date'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'years_of_experience', 'is_featured')
    list_filter = ('category', 'proficiency', 'is_featured')
    search_fields = ('name',)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'issue_date', 'expiration_date')
    list_filter = ('issuing_organization', 'issue_date')
    search_fields = ('name', 'issuing_organization')
    date_hierarchy = 'issue_date'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'is_featured')
    list_filter = ('status', 'is_featured', 'start_date')
    search_fields = ('title', 'description', 'technologies')
    date_hierarchy = 'start_date'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'is_replied')
    list_filter = ('is_read', 'is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = _("Marquer comme lu")
    
    def mark_as_replied(self, request, queryset):
        queryset.update(is_replied=True)
    mark_as_replied.short_description = _("Marquer comme répondu")

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'is_featured', 'views_count', 'published_at')
    list_filter = ('is_published', 'is_featured', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Contenu'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Métadonnées'), {
            'fields': ('tags', 'reading_time', 'is_published', 'is_featured')
        }),
        (_('Statistiques'), {
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'is_featured', 'views_count', 'published_at')
    list_filter = ('is_published', 'is_featured', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Contenu'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Métadonnées'), {
            'fields': ('tags', 'reading_time', 'is_published', 'is_featured')
        }),
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured', 'created_at')
    search_fields = ('name', 'company', 'content')
        (_('Statistiques'), {
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_starting', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at'),
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_achieved', 'organization')
    list_filter = ('category', 'date_achieved')
    search_fields = ('title', 'description', 'organization')
    date_hierarchy = 'date_achieved'
            'classes': ('collapse',)
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at',)
        }),
@admin.register(VisitorStats)
class VisitorStatsAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'page_visited', 'visit_date')
    list_filter = ('visit_date', 'page_visited')
    search_fields = ('ip_address', 'page_visited')
    readonly_fields = ('ip_address', 'user_agent', 'page_visited', 'referrer', 'visit_date', 'session_id')
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured', 'created_at')
    search_fields = ('name', 'company', 'content')
    date_hierarchy = 'visit_date'
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_starting', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_achieved', 'organization')
    list_filter = ('category', 'date_achieved')
    search_fields = ('title', 'description', 'organization')
    date_hierarchy = 'date_achieved'
    def has_add_permission(self, request):
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at',)
        return False
@admin.register(VisitorStats)
class VisitorStatsAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'page_visited', 'visit_date')
    list_filter = ('visit_date', 'page_visited')
    search_fields = ('ip_address', 'page_visited')
    readonly_fields = ('ip_address', 'user_agent', 'page_visited', 'referrer', 'visit_date', 'session_id')
    date_hierarchy = 'visit_date'
    
    def has_add_permission(self, request):
        return False
    )
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False