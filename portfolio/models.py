from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.urls import reverse

class Profile(models.Model):
    name = models.CharField(_("Nom"), max_length=100)
    title = models.CharField(_("Titre"), max_length=200)
    bio = models.TextField(_("Biographie"))
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    location = models.CharField(_("Localisation"), max_length=100, blank=True)
    linkedin = models.URLField(_("LinkedIn"), blank=True)
    github = models.URLField(_("GitHub"), blank=True)
    website = models.URLField(_("Site Web"), blank=True)
    profile_image = models.ImageField(_("Photo de profil"), upload_to='profile/', blank=True)
    cv_file = models.FileField(_("CV"), upload_to='cv/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profil")
        verbose_name_plural = _("Profils")

    def __str__(self):
        return self.name

class Education(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', _('Licence')),
        ('master', _('Master')),
        ('phd', _('Doctorat')),
        ('diploma', _('Diplôme')),
        ('certificate', _('Certificat')),
    ]

    degree = models.CharField(_("Diplôme"), max_length=20, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(_("Domaine d'étude"), max_length=200)
    institution = models.CharField(_("Institution"), max_length=200)
    location = models.CharField(_("Lieu"), max_length=100, blank=True)
    start_date = models.DateField(_("Date de début"))
    end_date = models.DateField(_("Date de fin"), null=True, blank=True)
    is_current = models.BooleanField(_("En cours"), default=False)
    description = models.TextField(_("Description"), blank=True)
    grade = models.CharField(_("Note/Mention"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Formation")
        verbose_name_plural = _("Formations")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} - {self.field_of_study}"

class Experience(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', _('Temps plein')),
        ('part_time', _('Temps partiel')),
        ('contract', _('Contrat')),
        ('internship', _('Stage')),
        ('freelance', _('Freelance')),
    ]

    title = models.CharField(_("Poste"), max_length=200)
    company = models.CharField(_("Entreprise"), max_length=200)
    location = models.CharField(_("Lieu"), max_length=100, blank=True)
    job_type = models.CharField(_("Type d'emploi"), max_length=20, choices=JOB_TYPE_CHOICES)
    start_date = models.DateField(_("Date de début"))
    end_date = models.DateField(_("Date de fin"), null=True, blank=True)
    is_current = models.BooleanField(_("Poste actuel"), default=False)
    description = models.TextField(_("Description"))
    achievements = models.TextField(_("Réalisations"), blank=True)
    technologies = models.CharField(_("Technologies utilisées"), max_length=500, blank=True)
    
    class Meta:
        verbose_name = _("Expérience")
        verbose_name_plural = _("Expériences")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} - {self.company}"

class Skill(models.Model):
    SKILL_CATEGORIES = [
        ('technical', _('Technique')),
        ('soft', _('Soft Skills')),
        ('language', _('Langue')),
        ('tool', _('Outil')),
    ]

    PROFICIENCY_LEVELS = [
        ('beginner', _('Débutant')),
        ('intermediate', _('Intermédiaire')),
        ('advanced', _('Avancé')),
        ('expert', _('Expert')),
    ]

    name = models.CharField(_("Nom"), max_length=100)
    category = models.CharField(_("Catégorie"), max_length=20, choices=SKILL_CATEGORIES)
    proficiency = models.CharField(_("Niveau"), max_length=20, choices=PROFICIENCY_LEVELS)
    years_of_experience = models.PositiveIntegerField(_("Années d'expérience"), default=0)
    is_featured = models.BooleanField(_("Compétence principale"), default=False)
    
    class Meta:
        verbose_name = _("Compétence")
        verbose_name_plural = _("Compétences")
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

class Certification(models.Model):
    name = models.CharField(_("Nom"), max_length=200)
    issuing_organization = models.CharField(_("Organisme"), max_length=200)
    issue_date = models.DateField(_("Date d'obtention"))
    expiration_date = models.DateField(_("Date d'expiration"), null=True, blank=True)
    credential_id = models.CharField(_("ID de certification"), max_length=100, blank=True)
    credential_url = models.URLField(_("URL de vérification"), blank=True)
    certificate_file = models.FileField(_("Fichier certificat"), upload_to='certificates/', blank=True)
    
    class Meta:
        verbose_name = _("Certification")
        verbose_name_plural = _("Certifications")
        ordering = ['-issue_date']

    def __str__(self):
        return self.name

class Project(models.Model):
    PROJECT_STATUS = [
        ('completed', _('Terminé')),
        ('in_progress', _('En cours')),
        ('planned', _('Planifié')),
    ]

    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"))
    detailed_description = models.TextField(_("Description détaillée"), blank=True)
    technologies = models.CharField(_("Technologies"), max_length=500)
    status = models.CharField(_("Statut"), max_length=20, choices=PROJECT_STATUS, default='completed')
    start_date = models.DateField(_("Date de début"))
    end_date = models.DateField(_("Date de fin"), null=True, blank=True)
    project_url = models.URLField(_("URL du projet"), blank=True)
    github_url = models.URLField(_("GitHub"), blank=True)
    image = models.ImageField(_("Image"), upload_to='projects/', blank=True)
    is_featured = models.BooleanField(_("Projet vedette"), default=False)
    
    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('portfolio:project_detail', kwargs={'pk': self.pk})

class Contact(models.Model):
    name = models.CharField(_("Nom"), max_length=100)
    email = models.EmailField(_("Email"), validators=[EmailValidator()])
    subject = models.CharField(_("Sujet"), max_length=200)
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    is_read = models.BooleanField(_("Lu"), default=False)
    is_replied = models.BooleanField(_("Répondu"), default=False)
    
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class SiteSettings(models.Model):
    site_title = models.CharField(_("Titre du site"), max_length=100, default="Portfolio")
    site_description = models.TextField(_("Description du site"), blank=True)
    footer_text = models.CharField(_("Texte du footer"), max_length=200, blank=True)
    google_analytics_id = models.CharField(_("Google Analytics ID"), max_length=50, blank=True)
    maintenance_mode = models.BooleanField(_("Mode maintenance"), default=False)
    
    class Meta:
        verbose_name = _("Paramètres du site")
        verbose_name_plural = _("Paramètres du site")

    def __str__(self):
        return "Paramètres du site"

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Il ne peut y avoir qu\'une seule instance de SiteSettings')
        return super().save(*args, **kwargs)