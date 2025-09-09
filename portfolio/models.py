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
    is_replied = models.BooleanField(_("Répondu"), default=False)
    priority = models.CharField(_("Priorité"), max_length=10,
                              choices=[
                                  ('low', 'Basse'),
                                  ('medium', 'Moyenne'),
                                  ('high', 'Haute'),
                                  ('urgent', 'Urgente')
                              ], default='medium')
    category = models.CharField(_("Catégorie"), max_length=50,
                              choices=[
                                  ('general', 'Général'),
                                  ('project', 'Projet'),
                                  ('collaboration', 'Collaboration'),
                                  ('job', 'Opportunité d\'emploi'),
                                  ('consultation', 'Consultation')
                              ], default='general')
    response = models.TextField(_("Réponse"), blank=True)
    response_date = models.DateTimeField(_("Date de réponse"), null=True, blank=True)
    
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
    show_visitor_counter = models.BooleanField(_("Afficher compteur de visiteurs"), default=True)
    allow_comments = models.BooleanField(_("Autoriser les commentaires"), default=True)
    social_sharing = models.BooleanField(_("Partage social"), default=True)
    newsletter_signup = models.BooleanField(_("Inscription newsletter"), default=False)
    custom_css = models.TextField(_("CSS personnalisé"), blank=True)
    custom_js = models.TextField(_("JavaScript personnalisé"), blank=True)
    
    class Meta:
        verbose_name = _("Paramètres du site")
        verbose_name_plural = _("Paramètres du site")

    def __str__(self):
        return "Paramètres du site"

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Il ne peut y avoir qu\'une seule instance de SiteSettings')
        return super().save(*args, **kwargs)

class BlogPost(models.Model):
    title = models.CharField(_("Titre"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    content = models.TextField(_("Contenu"))
    excerpt = models.TextField(_("Extrait"), max_length=300, blank=True)
    featured_image = models.ImageField(_("Image à la une"), upload_to='blog/', blank=True)
    tags = models.CharField(_("Tags"), max_length=500, blank=True, help_text="Séparés par des virgules")
    is_published = models.BooleanField(_("Publié"), default=False)
    is_featured = models.BooleanField(_("Article vedette"), default=False)
    views_count = models.PositiveIntegerField(_("Nombre de vues"), default=0)
    reading_time = models.PositiveIntegerField(_("Temps de lecture (min)"), default=5)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de modification"), auto_now=True)
    published_at = models.DateTimeField(_("Date de publication"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Article de blog")
        verbose_name_plural = _("Articles de blog")
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('portfolio:blog_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class Testimonial(models.Model):
    name = models.CharField(_("Nom"), max_length=100)
    position = models.CharField(_("Poste"), max_length=200)
    company = models.CharField(_("Entreprise"), max_length=200)
    content = models.TextField(_("Témoignage"))
    rating = models.PositiveIntegerField(_("Note"), choices=[(i, i) for i in range(1, 6)], default=5)
    photo = models.ImageField(_("Photo"), upload_to='testimonials/', blank=True)
    is_featured = models.BooleanField(_("Témoignage vedette"), default=False)
    project_related = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Projet associé"))
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Témoignage")
        verbose_name_plural = _("Témoignages")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company}"

class Service(models.Model):
    name = models.CharField(_("Nom du service"), max_length=200)
    description = models.TextField(_("Description"))
    short_description = models.CharField(_("Description courte"), max_length=300)
    icon = models.CharField(_("Icône FontAwesome"), max_length=50, default="fas fa-cog")
    price_starting = models.DecimalField(_("Prix à partir de"), max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(_("Durée typique"), max_length=100, blank=True)
    deliverables = models.TextField(_("Livrables"), blank=True)
    is_active = models.BooleanField(_("Service actif"), default=True)
    order = models.PositiveIntegerField(_("Ordre d'affichage"), default=0)
    
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Achievement(models.Model):
    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"))
    date_achieved = models.DateField(_("Date d'obtention"))
    category = models.CharField(_("Catégorie"), max_length=50,
                              choices=[
                                  ('award', 'Prix'),
                                  ('recognition', 'Reconnaissance'),
                                  ('milestone', 'Étape importante'),
                                  ('publication', 'Publication'),
                                  ('speaking', 'Conférence')
                              ])
    organization = models.CharField(_("Organisation"), max_length=200, blank=True)
    url = models.URLField(_("URL"), blank=True)
    image = models.ImageField(_("Image"), upload_to='achievements/', blank=True)
    
    class Meta:
        verbose_name = _("Réalisation")
        verbose_name_plural = _("Réalisations")
        ordering = ['-date_achieved']
    
    def __str__(self):
        return self.title

class Newsletter(models.Model):
    email = models.EmailField(_("Email"), unique=True)
    name = models.CharField(_("Nom"), max_length=100, blank=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    subscribed_at = models.DateTimeField(_("Date d'inscription"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Abonné newsletter")
        verbose_name_plural = _("Abonnés newsletter")
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email

class VisitorStats(models.Model):
    ip_address = models.GenericIPAddressField(_("Adresse IP"))
    user_agent = models.TextField(_("User Agent"))
    page_visited = models.CharField(_("Page visitée"), max_length=500)
    referrer = models.URLField(_("Référent"), blank=True)
    visit_date = models.DateTimeField(_("Date de visite"), auto_now_add=True)
    session_id = models.CharField(_("ID de session"), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _("Statistique de visiteur")
        verbose_name_plural = _("Statistiques de visiteurs")
        ordering = ['-visit_date']