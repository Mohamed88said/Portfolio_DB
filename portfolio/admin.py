from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Profile, Education, Experience, Skill, 
    Certification, Project, Contact, SiteSettings
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

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False