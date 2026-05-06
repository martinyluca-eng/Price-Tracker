# -*- coding: utf-8 -*-
import customtkinter as ctk
import threading
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import smtplib
from email.message import EmailMessage
import database

# Application

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
}

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Price Tracker")
        self.geometry("800x700")
        self.minsize(800, 700)
        self.resizable(True, True)
        self.produits = []
        self.surveillance_active = False
        self.thread_surveillance = None
        database.init_db()
        self._construire_interface()
        self._charger_produits()

    def _construire_interface(self):
        ctk.CTkLabel(self, text="Price Tracker", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        frame_form = ctk.CTkFrame(self)
        frame_form.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(frame_form, text="Ajouter un produit", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ctk.CTkLabel(frame_form, text="Nom du produit").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.input_nom = ctk.CTkEntry(frame_form, width=400, placeholder_text="Ex: RTX 5070 MSI")
        self.input_nom.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(frame_form, text="URL Amazon").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.input_url = ctk.CTkEntry(frame_form, width=400, placeholder_text="https://www.amazon.fr/dp/...")
        self.input_url.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(frame_form, text="Prix cible (euros)").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.input_prix = ctk.CTkEntry(frame_form, width=400, placeholder_text="Ex: 650")
        self.input_prix.grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkLabel(frame_form, text="Email").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.input_email = ctk.CTkEntry(frame_form, width=400, placeholder_text="ton_email@gmail.com")
        self.input_email.grid(row=4, column=1, padx=10, pady=5)

        ctk.CTkLabel(frame_form, text="Mot de passe app Gmail").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.input_mdp = ctk.CTkEntry(frame_form, width=400, placeholder_text="xxxx xxxx xxxx xxxx", show="*")
        self.input_mdp.grid(row=5, column=1, padx=10, pady=5)

        ctk.CTkButton(frame_form, text="+ Ajouter le produit", command=self._ajouter_produit).grid(row=6, column=0, columnspan=2, pady=15)

        frame_liste = ctk.CTkFrame(self)
        frame_liste.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(frame_liste, text="Produits surveilles", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.liste_texte = ctk.CTkTextbox(frame_liste, height=150, state="disabled")
        self.liste_texte.pack(padx=10, pady=5, fill="both", expand=True)

        self.bouton_surveillance = ctk.CTkButton(self, text="Demarrer la surveillance", fg_color="green", hover_color="darkgreen", command=self._toggle_surveillance)
        self.bouton_surveillance.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, height=100, state="disabled")
        self.log_box.pack(padx=20, pady=5, fill="x")

    def _charger_produits(self):
        """Charge les produits depuis la base au démarrage."""
        self.produits = database.lister_produits()
        for produit in self.produits:
            produit["email"] = ""
            produit["mdp"] = ""
            self._rafraichir_liste()
            if self.produits:
                self._log(f"{len(self.produits)} produit(s) chargé(s) depuis la base")

    def _log(self, message):
        self.log_box.configure(state="normal")
        maintenant = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{maintenant}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update()

    def _ajouter_produit(self):
        nom = self.input_nom.get().strip()
        url = self.input_url.get().strip()
        prix = self.input_prix.get().strip()
        email = self.input_email.get().strip()
        mdp = self.input_mdp.get().strip()

        if not nom or not url or not prix or not email or not mdp:
            self._log("Remplis tous les champs !")
            return

        try:
            prix = float(prix)
        except ValueError:
            self._log("Le prix doit etre un nombre !")
            return

        produit = {
            "nom": nom,
            "url": url,
            "prix_cible": prix,
            "email": email,
            "mdp": mdp,
        }
        self.produits.append(produit)
        self._rafraichir_liste()
        self._log(f"{nom} ajoute a la surveillance.")
        produit["id"] = database.ajouter_produit(nom, url, prix)
        self.input_nom.delete(0, "end")
        self.input_url.delete(0, "end")
        self.input_prix.delete(0, "end")

    def _rafraichir_liste(self):
        self.liste_texte.configure(state="normal")
        self.liste_texte.delete("1.0", "end")
        for i, p in enumerate(self.produits, 1):
            self.liste_texte.insert("end", f"{i}. {p['nom']} — cible : {p['prix_cible']:.2f} euros\n")
        self.liste_texte.configure(state="disabled")

    def _toggle_surveillance(self):
        if not self.surveillance_active:
            if not self.produits:
                self._log("Ajoute au moins un produit !")
                return
            self.surveillance_active = True
            self.bouton_surveillance.configure(text="Arreter la surveillance", fg_color="red", hover_color="darkred")
            self._log("Surveillance demarree !")
            self.thread_surveillance = threading.Thread(target=self._boucle_surveillance, daemon=True)
            self.thread_surveillance.start()
        else:
            self.surveillance_active = False
            self.bouton_surveillance.configure(text="Demarrer la surveillance", fg_color="green", hover_color="darkgreen")
            self._log("Surveillance arretee.")

    def _boucle_surveillance(self):
        while self.surveillance_active:
            for produit in self.produits:
                if not self.surveillance_active:
                    break
                prix, prix_brut = self._recuperer_prix(produit["url"])
                if prix is not None:
                    database.enregistrer_prix(produit["id"], prix)
                    if prix <= produit["prix_cible"]:
                        self._log(f"{produit['nom']} : {prix:.2f} euros - Prix cible atteint !")
                        self._envoyer_alerte(produit, prix)
                    else:
                        self._log(f"{produit['nom']} : {prix:.2f} euros - cible : {produit['prix_cible']:.2f} euros")
                else:
                    self._log(f"{produit['nom']} : prix non trouve")
                time.sleep(3)
            if self.surveillance_active:
                self._log("Prochaine verification dans 1 heure...")
                time.sleep(3600)

    def _recuperer_prix(self, url):
        try:
            session = requests.Session()
            session.headers.update(HEADERS)
            reponse = session.get(url)
            reponse.encoding = "utf-8"
            soup = BeautifulSoup(reponse.text, "html.parser")
            prix_brut = soup.find("span", class_="a-price-whole")
            if prix_brut is None:
                return None, None
            prix = float(prix_brut.text.replace(",", "").strip())
            return prix, prix_brut.text.strip()
        except Exception as e:
            self._log(f"Erreur : {e}")
            return None, None

    def _envoyer_alerte(self, produit, prix):
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Prix cible atteint : {produit['nom']}"
            msg["From"] = produit["email"]
            msg["To"] = produit["email"]
            msg.set_content(f"{produit['nom']} est a {prix:.2f} euros !\nPrix cible : {produit['prix_cible']:.2f} euros\n\n{produit['url']}")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(produit["email"], produit["mdp"])
                smtp.send_message(msg)
            self._log("Email envoye !")
        except Exception as e:
            self._log(f"Erreur email : {e}")

if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()