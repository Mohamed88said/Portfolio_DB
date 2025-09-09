from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.urls import reverse

class Profile(models.Model):
    name = models.CharField(_("Nom"), max_length=100)
    title = models.CharField(_("Titre"), max_length=200)
    bio = models.TextField(_("Biographie"))
    short_bio = models.CharField(_("Bio courte"), max_length=300, blank=True, help_text="Résumé en une phrase")
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    location = models.CharField(_("Localisation"), max_length=100, blank=True)
    birth_date = models.DateField(_("Date de naissance"), null=True, blank=True)
    nationality = models.CharField(_("Nationalité"), max_length=50, blank=True)
    languages_spoken = models.TextField(_("Langues parlées"), blank=True, help_text="Séparées par des virgules")
    linkedin = models.URLField(_("LinkedIn"), blank=True)
    github = models.URLField(_("GitHub"), blank=True)
    twitter = models.URLField(_("Twitter"), blank=True)
    instagram = models.URLField(_("Instagram"), blank=True)
    youtube = models.URLField(_("YouTube"), blank=True)
    website = models.URLField(_("Site Web"), blank=True)
    profile_image = models.ImageField(_("Photo de profil"), upload_to='profile/', blank=True)
    cv_file = models.FileField(_("CV"), upload_to='cv/', blank=True)
    resume_summary = models.TextField(_("Résumé professionnel"), blank=True)
    availability_status = models.CharField(_("Statut de disponibilité"), max_length=20, 
                                         choices=[
                                             ('available', 'Disponible'),
                                             ('busy', 'Occupé'),
                                             ('not_available', 'Non disponible')
                                         ], default='available')
    hourly_rate = models.DecimalField(_("Tarif horaire"), max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profil")
        verbose_name_plural = _("Profils")

    def __str__(self):
        return self.name
    
    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    @property
    def years_of_experience(self):
        from datetime import date
        experiences = Experience.objects.filter(start_date__isnull=False)
        if experiences.exists():
            first_job = experiences.order_by('start_date').first()
            return date.today().year - first_job.start_date.year
        return 0

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
    gpa = models.DecimalField(_("GPA/Note"), max_digits=4, decimal_places=2, null=True, blank=True)
    honors = models.CharField(_("Distinctions"), max_length=200, blank=True)
    relevant_coursework = models.TextField(_("Cours pertinents"), blank=True)
    thesis_title = models.CharField(_("Titre du mémoire/thèse"), max_length=300, blank=True)
    
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
    team_size = models.PositiveIntegerField(_("Taille de l'équipe"), null=True, blank=True)
    budget_managed = models.DecimalField(_("Budget géré"), max_digits=12, decimal_places=2, null=True, blank=True)
    key_metrics = models.TextField(_("Métriques clés"), blank=True, help_text="Résultats quantifiables")
    references = models.TextField(_("Références"), blank=True)
    
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
    last_used = models.DateField(_("Dernière utilisation"), null=True, blank=True)
    certification_level = models.CharField(_("Niveau de certification"), max_length=100, blank=True)
    projects_count = models.PositiveIntegerField(_("Nombre de projets"), default=0)
    
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
    score = models.CharField(_("Score obtenu"), max_length=50, blank=True)
    continuing_education_units = models.DecimalField(_("Unités de formation continue"), max_digits=5, decimal_places=1, null=True, blank=True)
    renewal_required = models.BooleanField(_("Renouvellement requis"), default=False)
    
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
    client = models.CharField(_("Client"), max_length=200, blank=True)
    project_type = models.CharField(_("Type de projet"), max_length=50, 
                                  choices=[
                                      ('web', 'Application Web'),
                                      ('mobile', 'Application Mobile'),
                                      ('desktop', 'Application Desktop'),
                                      ('api', 'API/Backend'),
                                      ('data', 'Data Science/ML'),
                                      ('other', 'Autre')
                                  ], default='web')
    team_members = models.TextField(_("Membres de l'équipe"), blank=True)
    budget = models.DecimalField(_("Budget"), max_digits=12, decimal_places=2, null=True, blank=True)
    duration_months = models.PositiveIntegerField(_("Durée (mois)"), null=True, blank=True)
    challenges_faced = models.TextField(_("Défis rencontrés"), blank=True)
    lessons_learned = models.TextField(_("Leçons apprises"), blank=True)
    metrics = models.TextField(_("Métriques de succès"), blank=True)
    awards = models.TextField(_("Prix/Reconnaissances"), blank=True)
    
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
    is_replied = models.BooleanField(_("Répondu"),