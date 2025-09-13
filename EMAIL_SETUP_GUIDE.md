# 📧 Guide de Configuration Email pour Portfolio

## 🎯 Configuration Email pour Recevoir les Messages de Contact

### **1. Configuration Gmail (Recommandée)**

#### **Étape 1 : Activer l'authentification à 2 facteurs**
1. Allez sur [myaccount.google.com](https://myaccount.google.com)
2. Cliquez sur "Sécurité"
3. Activez "Validation en 2 étapes"

#### **Étape 2 : Créer un mot de passe d'application**
1. Dans "Sécurité" → "Validation en 2 étapes"
2. Cliquez sur "Mots de passe des applications"
3. Sélectionnez "Autre (nom personnalisé)"
4. Tapez "Portfolio Django"
5. **Copiez le mot de passe généré** (16 caractères)

#### **Étape 3 : Configuration dans .env**
```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=le-mot-de-passe-dapplication-16-caracteres
DEFAULT_FROM_EMAIL=votre-email@gmail.com
```

### **2. Configuration Outlook/Hotmail**

```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@outlook.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=votre-email@outlook.com
```

### **3. Configuration Yahoo Mail**

```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@yahoo.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-dapplication
DEFAULT_FROM_EMAIL=votre-email@yahoo.com
```

## 📬 Configuration Newsletter

### **Option 1 : Email Simple (Inclus)**
La newsletter utilise le même système email que les contacts. Aucune configuration supplémentaire nécessaire.

### **Option 2 : Mailchimp (Professionnel)**
1. Créez un compte sur [mailchimp.com](https://mailchimp.com)
2. Créez une liste d'audience
3. Obtenez votre API Key et List ID
4. Ajoutez dans .env :
```env
MAILCHIMP_API_KEY=votre-api-key
MAILCHIMP_LIST_ID=votre-list-id
```

### **Option 3 : SendGrid (Professionnel)**
1. Créez un compte sur [sendgrid.com](https://sendgrid.com)
2. Créez une API Key
3. Ajoutez dans .env :
```env
SENDGRID_API_KEY=votre-sendgrid-api-key
```

## 🔧 Test de Configuration

### **Tester l'envoi d'email :**
```python
# Dans le shell Django (python manage.py shell)
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Portfolio',
    'Ceci est un test de configuration email.',
    settings.EMAIL_HOST_USER,
    [settings.EMAIL_HOST_USER],
    fail_silently=False,
)
```

## 📋 Informations Reçues par Email

### **Email de Contact :**
```
Sujet: Nouveau message de [Nom]: [Sujet]

Informations du contact:
- Nom: [Nom complet]
- Email: [Email]
- Téléphone: [Téléphone ou "Non renseigné"]
- Entreprise: [Entreprise ou "Non renseignée"]
- Budget: [Budget ou "Non renseigné"]
- Délai: [Délai ou "Non renseigné"]

Sujet: [Sujet du message]

Message:
[Contenu du message]

---
Envoyé le [Date et heure]
IP: [Adresse IP du visiteur]
```

### **Email de Témoignage :**
```
Sujet: Nouveau témoignage de [Nom]

Témoignage reçu:
- Nom: [Nom ou "Anonyme"]
- Email: [Email]
- Entreprise: [Entreprise]
- Poste: [Poste]
- Note: [1-5 étoiles]

Contenu:
[Témoignage complet]

Projet associé: [Nom du projet si sélectionné]

---
Statut: [En attente de modération / Publié automatiquement]
Reçu le [Date et heure]
```

### **Email Newsletter :**
```
Sujet: Nouvelle inscription newsletter

Nouvelle inscription:
- Email: [Email]
- Nom: [Nom si fourni]
- Date d'inscription: [Date et heure]

Total d'abonnés: [Nombre total]
```

## 🚨 Dépannage

### **Erreurs courantes :**

1. **"Authentication failed"**
   - Vérifiez que l'authentification 2FA est activée
   - Utilisez un mot de passe d'application, pas votre mot de passe normal

2. **"Connection refused"**
   - Vérifiez les paramètres SMTP (host, port)
   - Vérifiez votre connexion internet

3. **"Permission denied"**
   - Vérifiez que "Accès aux applications moins sécurisées" est activé (Gmail)
   - Ou utilisez un mot de passe d'application

### **Test rapide :**
Allez sur `/contact/` et envoyez-vous un message de test pour vérifier que tout fonctionne.

## 📱 Fonctionnement de la Newsletter

1. **Inscription** : Les visiteurs s'inscrivent via les formulaires
2. **Stockage** : Les emails sont stockés dans la base de données
3. **Notification** : Vous recevez un email à chaque nouvelle inscription
4. **Gestion** : Vous pouvez voir tous les abonnés dans l'admin Django
5. **Envoi** : Utilisez l'admin pour exporter les emails ou intégrer avec un service professionnel

La newsletter fonctionne immédiatement avec votre configuration email. Pour des fonctionnalités avancées (templates, automatisation), vous pouvez intégrer Mailchimp ou SendGrid plus tard.