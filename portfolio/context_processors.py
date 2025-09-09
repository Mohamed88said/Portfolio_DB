from .models import SiteSettings, Profile

def site_context(request):
    """Add site-wide context variables"""
    try:
        site_settings = SiteSettings.objects.first()
        profile = Profile.objects.first()
    except:
        site_settings = None
        profile = None
    
    return {
        'site_settings': site_settings,
        'profile': profile,
    }