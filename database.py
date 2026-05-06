import sqlite3
from datetime import datetime

DB_NAME = "tracker.db"

def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            prix_cible REAL NOT NULL,
            date_ajout TEXT NOT NULL
        )
    """)

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

def ajouter_produit(nom, url, prix_cible):
    """Ajoute un nouveau produit, ou met à jour s'il existe déjà."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    date_ajout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Vérifier si le produit existe déjà
    cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
    existant = cursor.fetchone()

    if existant:
        # Mettre à jour le prix cible
        cursor.execute("""
            UPDATE products
            SET nom = ?, prix_cible = ?
            WHERE url = ?
        """, (nom, prix_cible, url))
        product_id = existant[0]
    else:
        # Nouveau produit
        cursor.execute("""
            INSERT INTO products (nom, url, prix_cible, date_ajout)
            VALUES (?, ?, ?, ?)
        """, (nom, url, prix_cible, date_ajout))
        product_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return product_id


def lister_produits():
    """Renvoie tous les produits sous forme de liste de dictionnaires."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, url, prix_cible FROM products")
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


def supprimer_produit(product_id):
    """Supprime un produit et tout son historique."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Supprimer d'abord l'historique (à cause de la clé étrangère)
    cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()