from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from .models import Contact, Testimonial, SiteCustomization

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'company', 'subject', 'message', 'budget', 'timeline']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre nom complet'),
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('votre.email@exemple.com'),
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre numéro de téléphone')
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nom de votre entreprise')
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Sujet de votre message'),
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Décrivez votre projet ou votre demande...'),
                'rows': 5,
                'required': True
            }),
            'budget': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', _('Sélectionnez votre budget')),
                ('< 1000€', _('Moins de 1 000€')),
                ('1000-5000€', _('1 000€ - 5 000€')),
                ('5000-10000€', _('5 000€ - 10 000€')),
                ('10000-25000€', _('10 000€ - 25 000€')),
                ('> 25000€', _('Plus de 25 000€')),
                ('À discuter', _('À discuter')),
            ]),
            'timeline': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', _('Délai souhaité')),
                ('Urgent (< 1 mois)', _('Urgent (moins d\'un mois)')),
                ('1-3 mois', _('1 à 3 mois')),
                ('3-6 mois', _('3 à 6 mois')),
                ('6+ mois', _('Plus de 6 mois')),
                ('Flexible', _('Flexible')),
            ]),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs.update({'class': 'form-control'})

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'email', 'company', 'position', 'location', 'website', 'phone', 
                 'content', 'rating', 'photo', 'project_related', 'is_anonymous']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre nom complet')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('votre.email@exemple.com')
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nom de votre entreprise')
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre poste')
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre localisation')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://votre-site.com')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre téléphone')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Partagez votre expérience...'),
                'rows': 5,
                'required': True
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'project_related': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs optionnels si anonyme
        self.fields['email'].required = False
        self.fields['name'].required = False
        
        # JavaScript pour gérer l'anonymat
        self.fields['is_anonymous'].help_text = _(
            "Cochez cette case si vous souhaitez rester anonyme"
        )

class SiteCustomizationForm(forms.ModelForm):
    class Meta:
        model = SiteCustomization
        fields = [
            'color_scheme', 'primary_color', 'secondary_color', 'accent_color',
            'background_color', 'text_color', 'font_family', 'heading_font_size',
            'body_font_size', 'line_height', 'layout_style', 'container_width',
            'border_radius', 'spacing_unit', 'header_style', 'show_logo',
            'logo_image', 'footer_text', 'show_social_links', 'custom_css',
            'custom_js'
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color'
            }),
            'secondary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color'
            }),
            'accent_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color'
            }),
            'background_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color'
            }),
            'text_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color'
            }),
            'heading_font_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '12',
                'max': '72'
            }),
            'body_font_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '10',
                'max': '24'
            }),
            'line_height': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1.0',
                'max': '3.0',
                'step': '0.1'
            }),
            'container_width': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '800',
                'max': '1920'
            }),
            'border_radius': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'spacing_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '4',
                'max': '32'
            }),
            'footer_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Texte personnalisé pour le footer')
            }),
            'custom_css': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('/* Votre CSS personnalisé */'),
                'style': 'font-family: monospace;'
            }),
            'custom_js': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('// Votre JavaScript personnalisé'),
                'style': 'font-family: monospace;'
            }),
            'logo_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['show_logo', 'show_social_links', 'logo_image']:
                if not field.widget.attrs.get('class'):
                    field.widget.attrs.update({'class': 'form-control'})

class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('votre.email@exemple.com'),
            'required': True
        })
    )
    name = forms.CharField(
        label=_("Nom"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre nom (optionnel)')
        })
    )