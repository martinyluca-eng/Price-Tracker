import hashlib
import secrets
from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"


# ============================================================
# Partie 1 : HASH du mot de passe utilisateur (login app)
# ============================================================

def hash_mdp(mdp, sel=None):
    """Hash un mot de passe avec un sel aléatoire."""
    if sel is None:
        sel = secrets.token_hex(16)
    mdp_sel = (mdp + sel).encode()
    hash_resultat = hashlib.sha256(mdp_sel).hexdigest()
    return f"{sel}${hash_resultat}"


def verifier_mdp(mdp, hash_stocke):
    """Vérifie qu'un mot de passe correspond au hash stocké."""
    try:
        sel, _ = hash_stocke.split("$")
        nouveau_hash = hash_mdp(mdp, sel)
        return nouveau_hash == hash_stocke
    except ValueError:
        return False


# ============================================================
# Partie 2 : CHIFFREMENT du mot de passe Gmail
# ============================================================

def _charger_cle():
    """Charge la clé de chiffrement (la crée si elle n'existe pas)."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        cle = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(cle)
        return cle


def chiffrer(texte):
    """Chiffre un texte."""
    cle = _charger_cle()
    f = Fernet(cle)
    return f.encrypt(texte.encode()).decode()


def dechiffrer(texte_chiffre):
    """Déchiffre un texte."""
    cle = _charger_cle()
    f = Fernet(cle)
    return f.decrypt(texte_chiffre.encode()).decode()