import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

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
    resume_summary = models.TextField(_("Résumé professionnel"), blank=True)
    availability_status = models.CharField(_("Statut de disponibilité"), max_length=20, 
                                         choices=[
                                             ('available', 'Disponible'),
                                             ('partially_available', 'Partiellement disponible'),
                                             ('busy', 'Occupé'),
                                             ('not_available', 'Non disponible')
                                         ], default='available')
    hourly_rate = models.DecimalField(_("Tarif horaire"), max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nouveaux champs avancés
    timezone = models.CharField(_("Fuseau horaire"), max_length=50, default='Europe/Paris')
    work_hours_start = models.TimeField(_("Début heures de travail"), null=True, blank=True)
    work_hours_end = models.TimeField(_("Fin heures de travail"), null=True, blank=True)
    preferred_contact_method = models.CharField(_("Méthode de contact préférée"), max_length=20,
                                              choices=[('email', 'Email'), ('phone', 'Téléphone'), ('linkedin', 'LinkedIn')],
                                              default='email')

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

class CVDocument(models.Model):
    CV_TYPES = [
        ('main', _('CV Principal')),
        ('technical', _('CV Technique')),
        ('academic', _('CV Académique')),
        ('creative', _('CV Créatif')),
        ('short', _('CV Court')),
        ('detailed', _('CV Détaillé')),
        ('english', _('CV Anglais')),
        ('french', _('CV Français')),
        ('arabic', _('CV Arabe')),
    ]
    
    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    cv_type = models.CharField(_("Type de CV"), max_length=20, choices=CV_TYPES, default='main')
    file = models.FileField(_("Fichier CV"), upload_to='cv/')
    language = models.CharField(_("Langue"), max_length=10, choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('ar', 'العربية'),
    ], default='fr')
    is_primary = models.BooleanField(_("CV Principal"), default=False)
    is_public = models.BooleanField(_("Public"), default=True, help_text="Visible pour téléchargement")
    download_count = models.PositiveIntegerField(_("Téléchargements"), default=0)
    file_size = models.PositiveIntegerField(_("Taille (bytes)"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)
    
    class Meta:
        verbose_name = _("CV")
        verbose_name_plural = _("CVs")
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"
    
    def save(self, *args, **kwargs):
        # Si c'est le CV principal, désactiver les autres
        if self.is_primary:
            CVDocument.objects.exclude(pk=self.pk).update(is_primary=False)
        
        # Calculer la taille du fichier
        if self.file:
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    @property
    def file_size_formatted(self):
        if self.file_size:
            if self.file_size < 1024:
                return f"{self.file_size} B"
            elif self.file_size < 1024 * 1024:
                return f"{self.file_size / 1024:.1f} KB"
            else:
                return f"{self.file_size / (1024 * 1024):.1f} MB"
        return "Taille inconnue"

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
        return f"{self.get_degree_display()} - {self.field_of_study}"

class Experience(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', _('Temps plein')),
        ('part_time', _('Temps partiel')),
        ('contract', _('Contrat')),
        ('internship', _('Stage')),
        ('freelance', _('Freelance')),
        ('volunteer', _('Bénévolat')),
        ('personal', _('Projet personnel')),
    ]

    EXPERIENCE_CATEGORY_CHOICES = [
        ('professional', _('Professionnel')),
        ('academic', _('Académique')),
        ('volunteer', _('Bénévolat')),
        ('personal', _('Personnel')),
        ('creative', _('Créatif')),
        ('sports', _('Sport')),
        ('other', _('Autre')),
    ]

    title = models.CharField(_("Poste/Titre"), max_length=200)
    company = models.CharField(_("Entreprise/Organisation"), max_length=200)
    location = models.CharField(_("Lieu"), max_length=100, blank=True)
    job_type = models.CharField(_("Type"), max_length=20, choices=JOB_TYPE_CHOICES)
    category = models.CharField(_("Catégorie"), max_length=20, choices=EXPERIENCE_CATEGORY_CHOICES, default='professional')
    start_date = models.DateField(_("Date de début"))
    end_date = models.DateField(_("Date de fin"), null=True, blank=True)
    is_current = models.BooleanField(_("En cours"), default=False)
    description = models.TextField(_("Description"))
    achievements = models.TextField(_("Réalisations"), blank=True)
    technologies = models.CharField(_("Technologies/Compétences utilisées"), max_length=500, blank=True)
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
        ('creative', _('Créatif')),
        ('sport', _('Sport')),
        ('hobby', _('Loisir')),
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

    PROJECT_TYPES = [
        ('web', _('Application Web')),
        ('mobile', _('Application Mobile')),
        ('desktop', _('Application Desktop')),
        ('api', _('API/Backend')),
        ('data', _('Data Science/ML')),
        ('creative', _('Projet Créatif')),
        ('research', _('Recherche')),
        ('other', _('Autre')),
    ]

    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"))
    detailed_description = models.TextField(_("Description détaillée"), blank=True)
    technologies = models.CharField(_("Technologies"), max_length=500)
    status = models.CharField(_("Statut"), max_length=20, choices=PROJECT_STATUS, default='completed')
    project_type = models.CharField(_("Type de projet"), max_length=20, choices=PROJECT_TYPES, default='other')
    start_date = models.DateField(_("Date de début"))
    end_date = models.DateField(_("Date de fin"), null=True, blank=True)
    project_url = models.URLField(_("URL du projet"), blank=True)
    github_url = models.URLField(_("GitHub"), blank=True)
    image = models.ImageField(_("Image"), upload_to='projects/', blank=True)
    is_featured = models.BooleanField(_("Projet vedette"), default=False)
    client = models.CharField(_("Client"), max_length=200, blank=True)
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

class BlogCategory(models.Model):
    name = models.CharField(_("Nom"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    color = models.CharField(_("Couleur"), max_length=7, default="#007bff", help_text="Code couleur hexadécimal")
    icon = models.CharField(_("Icône"), max_length=50, blank=True, help_text="Classe Font Awesome")
    is_active = models.BooleanField(_("Actif"), default=True)
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    
    class Meta:
        verbose_name = _("Catégorie de blog")
        verbose_name_plural = _("Catégories de blog")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogPost(models.Model):
    title = models.CharField(_("Titre"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    content = models.TextField(_("Contenu"))
    excerpt = models.TextField(_("Extrait"), blank=True, help_text="Résumé de l'article")
    featured_image = models.ImageField(_("Image vedette"), upload_to='blog/', blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Catégorie"))
    tags = models.CharField(_("Tags"), max_length=500, blank=True, help_text="Séparés par des virgules")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Auteur"))
    is_published = models.BooleanField(_("Publié"), default=False)
    is_featured = models.BooleanField(_("Article vedette"), default=False)
    views_count = models.PositiveIntegerField(_("Nombre de vues"), default=0)
    reading_time = models.PositiveIntegerField(_("Temps de lecture (min)"), default=5)
    meta_description = models.CharField(_("Meta description"), max_length=160, blank=True)
    allow_comments = models.BooleanField(_("Autoriser les commentaires"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)
    published_at = models.DateTimeField(_("Publié le"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Article de blog")
        verbose_name_plural = _("Articles de blog")
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('portfolio:blog_detail', kwargs={'slug': self.slug})

class Testimonial(models.Model):
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]
    
    name = models.CharField(_("Nom"), max_length=100)
    email = models.EmailField(_("Email"), blank=True)
    company = models.CharField(_("Entreprise"), max_length=100, blank=True)
    position = models.CharField(_("Poste"), max_length=100, blank=True)
    location = models.CharField(_("Localisation"), max_length=100, blank=True)
    website = models.URLField(_("Site web"), blank=True)
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    content = models.TextField(_("Témoignage"))
    rating = models.PositiveIntegerField(_("Note"), choices=RATING_CHOICES, default=5)
    photo = models.ImageField(_("Photo"), upload_to='testimonials/', blank=True)
    project_related = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Projet associé"))
    is_featured = models.BooleanField(_("Témoignage vedette"), default=False)
    is_anonymous = models.BooleanField(_("Anonyme"), default=False)
    is_approved = models.BooleanField(_("Approuvé"), default=False)
    ip_address = models.GenericIPAddressField(_("Adresse IP"), blank=True, null=True)
    user_agent = models.TextField(_("User Agent"), blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    approved_at = models.DateTimeField(_("Approuvé le"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Témoignage")
        verbose_name_plural = _("Témoignages")
        ordering = ['-created_at']
    
    def __str__(self):
        if self.is_anonymous:
            return f"Témoignage anonyme - {self.created_at.strftime('%d/%m/%Y')}"
        return f"{self.name} - {self.company or 'Particulier'}"

class Service(models.Model):
    name = models.CharField(_("Nom du service"), max_length=200)
    short_description = models.CharField(_("Description courte"), max_length=300)
    description = models.TextField(_("Description détaillée"))
    icon = models.CharField(_("Icône"), max_length=50, help_text="Classe Font Awesome")
    price_starting = models.DecimalField(_("Prix à partir de"), max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(_("Durée"), max_length=100, blank=True)
    deliverables = models.TextField(_("Livrables"), blank=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Achievement(models.Model):
    ACHIEVEMENT_CATEGORIES = [
        ('award', _('Prix')),
        ('recognition', _('Reconnaissance')),
        ('milestone', _('Étape importante')),
        ('publication', _('Publication')),
        ('speaking', _('Conférence')),
        ('certification', _('Certification')),
        ('other', _('Autre')),
    ]
    
    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"))
    category = models.CharField(_("Catégorie"), max_length=20, choices=ACHIEVEMENT_CATEGORIES)
    organization = models.CharField(_("Organisation"), max_length=200, blank=True)
    date_achieved = models.DateField(_("Date d'obtention"))
    url = models.URLField(_("URL"), blank=True)
    image = models.ImageField(_("Image"), upload_to='achievements/', blank=True)
    
    class Meta:
        verbose_name = _("Réalisation")
        verbose_name_plural = _("Réalisations")
        ordering = ['-date_achieved']
    
    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField(_("Nom"), max_length=100)
    email = models.EmailField(_("Email"), validators=[EmailValidator()])
    subject = models.CharField(_("Sujet"), max_length=200)
    message = models.TextField(_("Message"))
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    company = models.CharField(_("Entreprise"), max_length=100, blank=True)
    budget = models.CharField(_("Budget estimé"), max_length=50, blank=True)
    timeline = models.CharField(_("Délai souhaité"), max_length=100, blank=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    is_read = models.BooleanField(_("Lu"), default=False)
    is_replied = models.BooleanField(_("Répondu"), default=False)
    ip_address = models.GenericIPAddressField(_("Adresse IP"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Newsletter(models.Model):
    email = models.EmailField(_("Email"), unique=True)
    name = models.CharField(_("Nom"), max_length=100, blank=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    subscribed_at = models.DateTimeField(_("Inscrit le"), auto_now_add=True)
    unsubscribed_at = models.DateTimeField(_("Désinscrit le"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletter")
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email

class VisitorStats(models.Model):
    ip_address = models.GenericIPAddressField(_("Adresse IP"))
    user_agent = models.TextField(_("User Agent"))
    page_visited = models.CharField(_("Page visitée"), max_length=200)
    referrer = models.URLField(_("Référent"), blank=True)
    visit_date = models.DateTimeField(_("Date de visite"), auto_now_add=True)
    session_id = models.CharField(_("ID de session"), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _("Statistique de visite")
        verbose_name_plural = _("Statistiques de visites")
        ordering = ['-visit_date']

class SiteCustomization(models.Model):
    COLOR_SCHEMES = [
        ('blue', _('Bleu')),
        ('green', _('Vert')),
        ('purple', _('Violet')),
        ('red', _('Rouge')),
        ('orange', _('Orange')),
        ('dark', _('Sombre')),
        ('custom', _('Personnalisé')),
    ]
    
    LAYOUT_STYLES = [
        ('modern', _('Moderne')),
        ('classic', _('Classique')),
        ('minimal', _('Minimaliste')),
        ('creative', _('Créatif')),
    ]
    
    FONT_FAMILIES = [
        ('inter', 'Inter'),
        ('roboto', 'Roboto'),
        ('montserrat', 'Montserrat'),
        ('poppins', 'Poppins'),
        ('lato', 'Lato'),
        ('open-sans', 'Open Sans'),
    ]
    
    # Couleurs
    color_scheme = models.CharField(_("Schéma de couleurs"), max_length=20, choices=COLOR_SCHEMES, default='blue')
    primary_color = models.CharField(_("Couleur primaire"), max_length=7, default="#007bff")
    secondary_color = models.CharField(_("Couleur secondaire"), max_length=7, default="#6c757d")
    accent_color = models.CharField(_("Couleur d'accent"), max_length=7, default="#28a745")
    background_color = models.CharField(_("Couleur de fond"), max_length=7, default="#ffffff")
    text_color = models.CharField(_("Couleur du texte"), max_length=7, default="#333333")
    
    # Typography
    font_family = models.CharField(_("Police"), max_length=20, choices=FONT_FAMILIES, default='inter')
    heading_font_size = models.PositiveIntegerField(_("Taille des titres"), default=32)
    body_font_size = models.PositiveIntegerField(_("Taille du texte"), default=16)
    line_height = models.DecimalField(_("Hauteur de ligne"), max_digits=3, decimal_places=1, default=1.6)
    
    # Layout
    layout_style = models.CharField(_("Style de mise en page"), max_length=20, choices=LAYOUT_STYLES, default='modern')
    container_width = models.PositiveIntegerField(_("Largeur du conteneur"), default=1200)
    border_radius = models.PositiveIntegerField(_("Rayon des bordures"), default=8)
    spacing_unit = models.PositiveIntegerField(_("Unité d'espacement"), default=16)
    
    # Header/Navigation
    header_style = models.CharField(_("Style d'en-tête"), max_length=20, 
                                   choices=[
                                       ('fixed', _('Fixe')),
                                       ('static', _('Statique')),
                                       ('transparent', _('Transparent')),
                                   ], default='fixed')
    show_logo = models.BooleanField(_("Afficher le logo"), default=True)
    logo_image = models.ImageField(_("Logo"), upload_to='customization/', blank=True)
    
    # Footer
    footer_text = models.CharField(_("Texte du footer"), max_length=200, blank=True)
    show_social_links = models.BooleanField(_("Afficher les liens sociaux"), default=True)
    
    # Advanced
    custom_css = models.TextField(_("CSS personnalisé"), blank=True)
    custom_js = models.TextField(_("JavaScript personnalisé"), blank=True)
    
    # Meta
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Personnalisation du site")
        verbose_name_plural = _("Personnalisations du site")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Personnalisation - {self.color_scheme} - {self.layout_style}"

class SiteSettings(models.Model):
    site_title = models.CharField(_("Titre du site"), max_length=100, default="Portfolio")
    site_description = models.TextField(_("Description du site"), blank=True)
    site_keywords = models.CharField(_("Mots-clés"), max_length=500, blank=True)
    footer_text = models.CharField(_("Texte du footer"), max_length=200, blank=True)
    google_analytics_id = models.CharField(_("Google Analytics ID"), max_length=50, blank=True)
    maintenance_mode = models.BooleanField(_("Mode maintenance"), default=False)
    allow_testimonials = models.BooleanField(_("Autoriser les témoignages"), default=True)
    moderate_testimonials = models.BooleanField(_("Modérer les témoignages"), default=True)
    allow_anonymous_testimonials = models.BooleanField(_("Autoriser les témoignages anonymes"), default=True)
    contact_email = models.EmailField(_("Email de contact"), blank=True)
    
    class Meta:
        verbose_name = _("Paramètres du site")
        verbose_name_plural = _("Paramètres du site")
    
    def __str__(self):
        return self.site_title

class Tag(models.Model):
    """Système de tags universel pour tous les contenus"""
    name = models.CharField(_("Nom"), max_length=50, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    color = models.CharField(_("Couleur"), max_length=7, default="#007bff")
    description = models.TextField(_("Description"), blank=True)
    usage_count = models.PositiveIntegerField(_("Nombre d'utilisations"), default=0)
    is_featured = models.BooleanField(_("Tag vedette"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class SearchQuery(models.Model):
    """Historique des recherches pour améliorer les suggestions"""
    query = models.CharField(_("Requête"), max_length=200)
    results_count = models.PositiveIntegerField(_("Nombre de résultats"), default=0)
    ip_address = models.GenericIPAddressField(_("Adresse IP"), null=True, blank=True)
    user_agent = models.TextField(_("User Agent"), blank=True)
    search_date = models.DateTimeField(auto_now_add=True)
    clicked_result = models.CharField(_("Résultat cliqué"), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _("Requête de recherche")
        verbose_name_plural = _("Requêtes de recherche")
        ordering = ['-search_date']

class FAQ(models.Model):
    """Questions fréquemment posées"""
    question = models.CharField(_("Question"), max_length=300)
    answer = models.TextField(_("Réponse"))
    category = models.CharField(_("Catégorie"), max_length=50, choices=[
        ('general', _('Général')),
        ('services', _('Services')),
        ('pricing', _('Tarifs')),
        ('technical', _('Technique')),
        ('process', _('Processus')),
    ], default='general')
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    views_count = models.PositiveIntegerField(_("Nombre de vues"), default=0)
    helpful_votes = models.PositiveIntegerField(_("Votes utiles"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQ")
        ordering = ['category', 'order']
    
    def __str__(self):
        return self.question[:100]

class Timeline(models.Model):
    """Timeline des événements importants"""
    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"))
    date = models.DateField(_("Date"))
    category = models.CharField(_("Catégorie"), max_length=50, choices=[
        ('education', _('Formation')),
        ('career', _('Carrière')),
        ('project', _('Projet')),
        ('achievement', _('Réalisation')),
        ('personal', _('Personnel')),
    ])
    icon = models.CharField(_("Icône"), max_length=50, default="fas fa-calendar")
    color = models.CharField(_("Couleur"), max_length=7, default="#007bff")
    is_milestone = models.BooleanField(_("Étape importante"), default=False)
    image = models.ImageField(_("Image"), upload_to='timeline/', blank=True)
    link = models.URLField(_("Lien"), blank=True)
    
    class Meta:
        verbose_name = _("Événement Timeline")
        verbose_name_plural = _("Timeline")
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date.year} - {self.title}"

class Collaboration(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Terminé'),
        ('ongoing', 'En cours'),
        ('planned', 'Planifié'),
    )
    
    CATEGORY_CHOICES = (
        ('web', 'Développement Web'),
        ('mobile', 'Application Mobile'),
        ('ai', 'Intelligence Artificielle'),
        ('data', 'Data Science'),
        ('design', 'Design UI/UX'),
        ('consulting', 'Consulting'),
        ('other', 'Autre'),
    )
    
    title = models.CharField(_('Titre'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    description = models.TextField(_('Description'))
    detailed_description = models.TextField(_('Description détaillée'), blank=True)
    image = models.ImageField(_('Image'), upload_to='collaborations/', blank=True, null=True)
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='completed')
    category = models.CharField(_('Catégorie'), max_length=20, choices=CATEGORY_CHOICES, default='web')
    client = models.CharField(_('Client'), max_length=200, blank=True)
    technologies = models.CharField(_('Technologies'), max_length=500, help_text=_('Séparées par des virgules'))
    
    start_date = models.DateField(_('Date de début'))
    end_date = models.DateField(_('Date de fin'), blank=True, null=True)
    is_featured = models.BooleanField(_('En vedette'), default=False)
    is_active = models.BooleanField(_('Actif'), default=True)
    
    project_url = models.URLField(_('URL du projet'), blank=True)
    github_url = models.URLField(_('URL GitHub'), blank=True)
    demo_url = models.URLField(_('URL de démo'), blank=True)
    
    budget = models.DecimalField(_('Budget'), max_digits=10, decimal_places=2, blank=True, null=True)
    team_size = models.PositiveIntegerField(_('Taille de l\'équipe'), blank=True, null=True)
    challenges_faced = models.TextField(_('Défis rencontrés'), blank=True)
    results_achieved = models.TextField(_('Résultats obtenus'), blank=True)
    
    order = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)

    class Meta:
        verbose_name = _('Collaboration')
        verbose_name_plural = _('Collaborations')
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_duration(self):
        if self.end_date:
            delta = self.end_date - self.start_date
            return f"{delta.days // 30} mois"
        return "En cours"

    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(',')]

class Resource(models.Model):
    """Ressources téléchargeables"""
    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"))
    file = models.FileField(_("Fichier"), upload_to='resources/')
    file_type = models.CharField(_("Type de fichier"), max_length=20, choices=[
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('code', 'Code'),
        ('other', 'Autre'),
    ])
    category = models.CharField(_("Catégorie"), max_length=50, choices=[
        ('cv', _('CV/Résumé')),
        ('portfolio', _('Portfolio')),
        ('template', _('Template')),
        ('guide', _('Guide')),
        ('presentation', _('Présentation')),
        ('other', _('Autre')),
    ])
    is_public = models.BooleanField(_("Public"), default=True)
    download_count = models.PositiveIntegerField(_("Nombre de téléchargements"), default=0)
    file_size = models.PositiveIntegerField(_("Taille du fichier (bytes)"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Ressource")
        verbose_name_plural = _("Ressources")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Analytics(models.Model):
    """Analytics avancées du site"""
    date = models.DateField(_("Date"))
    page_views = models.PositiveIntegerField(_("Vues de page"), default=0)
    unique_visitors = models.PositiveIntegerField(_("Visiteurs uniques"), default=0)
    bounce_rate = models.DecimalField(_("Taux de rebond"), max_digits=5, decimal_places=2, default=0)
    avg_session_duration = models.DurationField(_("Durée moyenne de session"), null=True, blank=True)
    top_pages = models.JSONField(_("Pages populaires"), default=dict)
    referrers = models.JSONField(_("Référents"), default=dict)
    devices = models.JSONField(_("Appareils"), default=dict)
    countries = models.JSONField(_("Pays"), default=dict)
    
    class Meta:
        verbose_name = _("Analytics")
        verbose_name_plural = _("Analytics")
        ordering = ['-date']
        unique_together = ['date']
    
    def __str__(self):
        return f"Analytics - {self.date}"