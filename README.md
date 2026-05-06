# 🛒 Amazon Price Tracker

Application Windows de surveillance automatique des prix sur Amazon avec alertes email.

## 📋 Description

Application desktop en Python qui surveille en continu le prix de produits Amazon et envoie une alerte email dès que le prix cible est atteint. Interface graphique intuitive permettant d'ajouter, surveiller et gérer plusieurs produits simultanément.

## ✨ Fonctionnalités

- 🔍 Surveillance simultanée de plusieurs produits Amazon
- 📧 Alertes email automatiques quand le prix cible est atteint
- 💾 Historique des prix sauvegardé en CSV
- 🖥️ Interface graphique moderne (CustomTkinter)
- ⏱️ Vérification automatique à intervalles réguliers
- 🛡️ Gestion des blocages anti-bot d'Amazon

## 🛠️ Technologies

- **Python 3.14** — langage principal
- **CustomTkinter** — interface graphique
- **BeautifulSoup4** — parsing HTML
- **Requests** — requêtes HTTP
- **smtplib** — envoi d'emails
- **PyInstaller** — création de l'exécutable Windows
- **SQLite** — Persistance des données

## 📦 Installation

### Option 1 — Utiliser l'exécutable (utilisateurs)

Téléchargez la dernière version du `.exe` depuis la page [Releases](https://github.com/martinyluca-eng/Price-Tracker/releases) et lancez-la directement. Aucune installation nécessaire.

### Option 2 — Lancer depuis le code source (développeurs)

Prérequis : Python 3.10 ou supérieur

```bash
# Cloner le dépôt
git clone https://github.com/martinyluca-eng/Price-Tracker.git
cd Price-Tracker

# Créer un environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install requests beautifulsoup4 customtkinter

# Lancer l'application
python app.py
```

## 🚀 Utilisation

1. Lancer l'application
2. Renseigner le nom du produit, l'URL Amazon, le prix cible
3. Saisir son email Gmail et son mot de passe d'application
4. Cliquer sur **Ajouter le produit**
5. Cliquer sur **Démarrer la surveillance**

L'application vérifiera automatiquement les prix et enverra un email dès qu'un prix cible est atteint.

## 👤 Auteur

**Luca Martiny**
- GitHub : [@martinyluca-eng](https://github.com/martinyluca-eng)

---

*Projet réalisé dans le cadre de mon apprentissage Python avec un focus sur l'automatisation.*
