import sqlite3
from datetime import datetime

DB_NAME = "tracker.db"

def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table des utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            mdp_hash TEXT NOT NULL,
            mdp_gmail_chiffre TEXT,
            date_creation TEXT NOT NULL
        )
    """)

    # Table des produits — liée à un user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nom TEXT NOT NULL,
            url TEXT NOT NULL,
            prix_cible REAL NOT NULL,
            date_ajout TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Table de l'historique des prix
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            prix REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()

def ajouter_produit(user_id, nom, url, prix_cible):
    """Ajoute ou met à jour un produit pour un utilisateur donné."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    date_ajout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Vérifier si ce user a déjà ce produit
    cursor.execute(
        "SELECT id FROM products WHERE user_id = ? AND url = ?",
        (user_id, url)
    )
    existant = cursor.fetchone()

    if existant:
        cursor.execute("""
            UPDATE products
            SET nom = ?, prix_cible = ?
            WHERE id = ?
        """, (nom, prix_cible, existant[0]))
        product_id = existant[0]
    else:
        cursor.execute("""
            INSERT INTO products (user_id, nom, url, prix_cible, date_ajout)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, nom, url, prix_cible, date_ajout))
        product_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return product_id


def lister_produits(user_id):
    """Renvoie les produits d'un utilisateur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nom, url, prix_cible FROM products WHERE user_id = ?",
        (user_id,)
    )
    lignes = cursor.fetchall()

    conn.close()

    produits = []
    for ligne in lignes:
        produits.append({
            "id": ligne[0],
            "nom": ligne[1],
            "url": ligne[2],
            "prix_cible": ligne[3],
        })
    return produits


def supprimer_produit(product_id):
    """Supprime un produit et tout son historique."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()

def enregistrer_prix(product_id, prix):
    """Enregistre un prix dans l'historique."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO price_history (product_id, prix, timestamp)
        VALUES (?, ?, ?)
    """, (product_id, prix, timestamp))

    conn.commit()
    conn.close()