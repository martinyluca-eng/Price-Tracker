# 🛒 Amazon Price Tracker

Application Windows multi-utilisateurs de surveillance automatique des prix sur Amazon avec alertes email.

## 📋 Description

Application desktop sécurisée en Python qui permet à plusieurs utilisateurs de surveiller leurs propres listes de produits Amazon. Chaque compte est isolé, les mots de passe sont hashés et les identifiants Gmail chiffrés. Interface graphique moderne avec authentification, gestion CRUD complète et alertes email automatiques.

## ✨ Fonctionnalités

- 🔐 **Système d'authentification** : création de compte et connexion sécurisée
- 👥 **Multi-utilisateurs** : chaque compte a ses propres produits, isolés des autres
- 🔍 Surveillance simultanée de plusieurs produits Amazon
- 📧 Alertes email automatiques quand le prix cible est atteint
- 💾 Base de données SQLite structurée avec relations
- ✏️ Édition et suppression des produits via interface
- 🔗 Lien cliquable vers chaque produit Amazon
- 🖥️ Interface graphique moderne (CustomTkinter)
- ⏱️ Vérification automatique à intervalles réguliers
- 🛡️ Gestion des blocages anti-bot d'Amazon

## 🔐 Sécurité

- Mots de passe utilisateurs **hashés** avec sel aléatoire (SHA-256)
- Mots de passe Gmail **chiffrés** avec Fernet (cryptography)
- Isolation des données entre utilisateurs (clés étrangères SQL)
- Clé de chiffrement stockée localement (`secret.key`), ignorée par Git

## 🛠️ Technologies

- **Python 3.14** — langage principal
- **CustomTkinter** — interface graphique
- **SQLite3** — base de données
- **BeautifulSoup4** — parsing HTML
- **Requests** — requêtes HTTP
- **smtplib** — envoi d'emails
- **cryptography** — chiffrement Fernet
- **hashlib** — hash sécurisé des mots de passe
- **PyInstaller** — création de l'exécutable Windows

## 🏗️ Architecture

tracker-prix/
app.py              # Interface principale
login_window.py     # Fenêtre d'authentification
database.py         # Gestion de la base SQLite
auth.py             # Logique d'authentification
security.py         # Hash et chiffrement
README.md
.gitignore

## 📦 Installation

### Option 1 — Utiliser l'exécutable (utilisateurs)

Téléchargez la dernière version du `.exe` depuis la page [Releases](https://github.com/martinyluca-eng/Price-Tracker/releases) et lancez-la directement.

### Option 2 — Lancer depuis le code source (développeurs)

```bash
git clone https://github.com/martinyluca-eng/Price-Tracker.git
cd Price-Tracker

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install requests beautifulsoup4 customtkinter cryptography

python app.py
```

## 🚀 Utilisation

1. Au premier lancement, créer un compte avec son email Gmail et un mot de passe d'application Gmail
2. Se connecter pour accéder à l'interface principale
3. Ajouter des produits Amazon (nom, URL, prix cible)
4. Démarrer la surveillance
5. Recevoir un email dès qu'un prix cible est atteint

## ⚙️ Configuration requise

- Windows 10 ou supérieur
- Compte Gmail avec [mot de passe d'application](https://myaccount.google.com/apppasswords) activé

## 👤 Auteur

**Luca Martiny**
- GitHub : [@martinyluca-eng](https://github.com/martinyluca-eng)

---

*Projet réalisé dans le cadre de mon apprentissage Python avec un focus sur l'automatisation et la sécurité.*