from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project
from datetime import datetime

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return [
            'portfolio:home',
            'portfolio:academic', 
            'portfolio:experience',
            'portfolio:certifications',
            'portfolio:projects',
            'portfolio:contact'
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime.now()

class ProjectSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return Project.objects.all()
    
    def lastmod(self, obj):
        return obj.start_date