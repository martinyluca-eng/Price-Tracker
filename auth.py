import sqlite3
from datetime import datetime
import security

DB_NAME = "tracker.db"


def creer_compte(email, mdp, mdp_gmail):
    """Crée un nouveau compte utilisateur.
    Renvoie (True, user_id) en cas de succès, (False, message) sinon.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Vérifier si l'email existe déjà
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False, "Un compte existe déjà avec cet email."

    # Créer le compte
    mdp_hashe = security.hash_mdp(mdp)
    mdp_gmail_chiffre = security.chiffrer(mdp_gmail)
    date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO users (email, mdp_hash, mdp_gmail_chiffre, date_creation)
        VALUES (?, ?, ?, ?)
    """, (email, mdp_hashe, mdp_gmail_chiffre, date_creation))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return True, user_id


def se_connecter(email, mdp):
    """Tente de connecter un utilisateur.
    Renvoie (True, user_id, mdp_gmail) en cas de succès, (False, message, None) sinon.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, mdp_hash, mdp_gmail_chiffre FROM users WHERE email = ?",
        (email,)
    )
    ligne = cursor.fetchone()
    conn.close()

    if not ligne:
        return False, "Aucun compte avec cet email.", None

    user_id, mdp_hash, mdp_gmail_chiffre = ligne

    if not security.verifier_mdp(mdp, mdp_hash):
        return False, "Mot de passe incorrect.", None

    # Déchiffrer le mdp Gmail
    mdp_gmail = security.dechiffrer(mdp_gmail_chiffre)
    return True, user_id, mdp_gmail