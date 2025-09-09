from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('academic/', views.AcademicView.as_view(), name='academic'),
    path('experience/', views.ExperienceView.as_view(), name='experience'),
    path('certifications/', views.CertificationView.as_view(), name='certifications'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('api/contact/', views.ContactAPIView.as_view(), name='contact_api'),
]