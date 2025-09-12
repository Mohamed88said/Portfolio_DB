from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Public pages
    path('', views.HomeView.as_view(), name='home'),
    path('academic/', views.AcademicView.as_view(), name='academic'),
    path('experience/', views.ExperienceView.as_view(), name='experience'),
    path('certifications/', views.CertificationView.as_view(), name='certifications'),
    path('search/', views.UniversalSearchView.as_view(), name='universal_search'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('testimonials/add/', views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/success/', views.TestimonialSuccessView.as_view(), name='testimonial_success'),
    path('blog/', views.BlogListView.as_view(), name='blog'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('collaborations/', views.CollaborationsView.as_view(), name='collaborations'),
    path('resources/', views.ResourcesView.as_view(), name='resources'),
    path('resources/<int:resource_id>/download/', views.ResourceDownloadView.as_view(), name='resource_download'),
    path('analytics/', views.AdvancedAnalyticsView.as_view(), name='advanced_analytics'),
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
    
    # Admin pages (protected)
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-customization/', views.AdminCustomizationView.as_view(), name='admin_customization'),
    
    # API endpoints
    path('api/contact/', views.ContactAPIView.as_view(), name='contact_api'),
    path('api/newsletter/', views.NewsletterAPIView.as_view(), name='newsletter_api'),
    path('api/stats/', views.StatsAPIView.as_view(), name='stats_api'),
    path('api/search-suggestions/', views.SearchSuggestionsAPIView.as_view(), name='search_suggestions_api'),
    path('api/tag-cloud/', views.TagCloudAPIView.as_view(), name='tag_cloud_api'),
    path('api/customization/preview/', views.CustomizationPreviewAPIView.as_view(), name='customization_preview_api'),
    path('api/faq/<int:faq_id>/helpful/', views.FAQHelpfulAPIView.as_view(), name='faq_helpful_api'),
    path('api/newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe_api'),
    
    # Downloads
    path('download-cv/', views.DownloadCVView.as_view(), name='download_cv'),
]