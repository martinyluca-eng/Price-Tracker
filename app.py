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
import webbrowser
import security

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
    def __init__(self, user_id, email, mdp_gmail):
        super().__init__()
        self.title(f"Price Tracker - {email}")
        self.geometry("800x700")
        self.minsize(800, 700)
        self.resizable(True, True)
    # Infos de l'utilisateur connecté
        self.user_id = user_id
        self.user_email = email
        self.user_mdp_gmail = mdp_gmail

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

        ctk.CTkButton(frame_form, text="+ Ajouter le produit", command=self._ajouter_produit).grid(row=4, column=0, columnspan=2, pady=15)

        frame_liste = ctk.CTkFrame(self)
        frame_liste.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(frame_liste, text="Produits surveilles", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.liste_frame = ctk.CTkScrollableFrame(frame_liste, height=200)
        self.liste_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.bouton_surveillance = ctk.CTkButton(self, text="Demarrer la surveillance", fg_color="green", hover_color="darkgreen", command=self._toggle_surveillance)
        self.bouton_surveillance.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, height=100, state="disabled")
        self.log_box.pack(padx=20, pady=5, fill="x")

    def _charger_produits(self):
        """Charge les produits de l'utilisateur connecté."""
        self.produits = database.lister_produits(self.user_id)
        self._rafraichir_liste()
        if self.produits:
            self._log(f"{len(self.produits)} produit(s) chargé(s).")

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

        if not nom or not url or not prix:
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
        }

        produit["id"] = database.ajouter_produit(self.user_id, nom, url, prix)
        self.produits.append(produit)
        self._rafraichir_liste()
        self._log(f"{nom} ajoute a la surveillance.")

        self.input_nom.delete(0, "end")
        self.input_url.delete(0, "end")
        self.input_prix.delete(0, "end")

    def _rafraichir_liste(self):
        for widget in self.liste_frame.winfo_children():
            widget.destroy()

        for i, p in enumerate(self.produits, 1):
            carte = ctk.CTkFrame(self.liste_frame)
            carte.pack(fill="x", padx=5, pady=5)

            info = f"{i}. {p['nom']} — cible : {p['prix_cible']:.2f} euros"
            ctk.CTkLabel(carte, text=info, anchor="w").pack(side="left", padx=10, pady=5, fill="x", expand=True)
            
            bouton_suppr = ctk.CTkButton(
                 carte,
                 text="Supprimer",
                 width=100,
                 fg_color="red",
                 hover_color="darkred",
                 command=lambda p=p: self._supprimer_produit(p)
                 )
            bouton_suppr.pack(side="right", padx=5, pady=5)

            bouton_modif = ctk.CTkButton(
                carte,
                text="Modifier",
                width=100,
                fg_color="orange",
                hover_color="darkorange",
                command=lambda p=p: self._ouvrir_modification(p)
                )
            bouton_modif.pack(side="right", padx=5, pady=5)

            bouton = ctk.CTkButton(
                carte,
                text="Voir sur Amazon",
                width=140,
                command=lambda url=p["url"]: webbrowser.open(url)
                )
            bouton.pack(side="right", padx=10, pady=5)

    def _ouvrir_modification(self, produit):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Modifier : {produit['nom']}")
        popup.geometry("500x400")
        popup.transient(self)        
        popup.grab_set()              
        
        ctk.CTkLabel(popup, text="Modifier le produit", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ctk.CTkLabel(popup, text="Nom du produit").pack(pady=(10, 0))
        input_nom = ctk.CTkEntry(popup, width=400)
        input_nom.insert(0, produit["nom"])
        input_nom.pack(pady=5)

    
        ctk.CTkLabel(popup, text="Prix cible (euros)").pack(pady=(10, 0))
        input_prix = ctk.CTkEntry(popup, width=400)
        input_prix.insert(0, str(produit["prix_cible"]))
        input_prix.pack(pady=5)

    
        def sauvegarder():
            nouveau_nom = input_nom.get().strip()
            nouveau_prix = input_prix.get().strip()

            if not nouveau_nom or not nouveau_prix:
                return
            
            try:
                nouveau_prix = float(nouveau_prix)
            except ValueError:
                self._log("Le prix doit etre un nombre !")
                return
            
            produit["nom"] = nouveau_nom
            produit["prix_cible"] = nouveau_prix
            
            database.ajouter_produit(nouveau_nom, produit["url"], nouveau_prix)
            
            self._rafraichir_liste()
            self._log(f"{nouveau_nom} mis a jour")
            popup.destroy()
        
        ctk.CTkButton(popup, text="Enregistrer", command=sauvegarder).pack(pady=20)

    def _supprimer_produit(self, produit):
        if "id" in produit:
            database.supprimer_produit(produit["id"])
            self.produits.remove(produit)
            self._rafraichir_liste()
            self._log(f"{produit['nom']} supprime")

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
            msg["From"] = self.user_email
            msg["To"] = self.user_email
            msg.set_content(f"{produit['nom']} est a {prix:.2f} euros !\nPrix cible : {produit['prix_cible']:.2f} euros\n\n{produit['url']}")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.user_email, self.user_mdp_gmail)
                smtp.send_message(msg)
            self._log("Email envoye !")
        except Exception as e:
            self._log(f"Erreur email : {e}")

if __name__ == "__main__":
    import database
    from login_window import LoginWindow

    # Initialiser la base AVANT l'écran de login
    database.init_db()

    # Afficher la fenêtre de login
    login = LoginWindow()
    login.mainloop()

    # Si l'utilisateur s'est connecté avec succès, lancer l'app principale
    if login.user_id is not None:
        app = TrackerApp(login.user_id, login.email, login.mdp_gmail)
        app.mainloop()