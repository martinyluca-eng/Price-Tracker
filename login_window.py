# -*- coding: utf-8 -*-
import customtkinter as ctk
import auth


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Price Tracker - Connexion")
        self.geometry("450x550")
        self.resizable(False, False)

        self.user_id = None
        self.email = None
        self.mdp_gmail = None
        self.mode = "login"   # "login" ou "register"

        self._construire_interface()

    def _construire_interface(self):
        # Titre
        ctk.CTkLabel(
            self,
            text="Price Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)

        self.label_mode = ctk.CTkLabel(self, text="Connexion", font=ctk.CTkFont(size=16))
        self.label_mode.pack(pady=5)

        # Champ email
        ctk.CTkLabel(self, text="Email").pack(pady=(15, 0))
        self.input_email = ctk.CTkEntry(self, width=300, placeholder_text="ton_email@gmail.com")
        self.input_email.pack(pady=5)

        # Champ mot de passe
        ctk.CTkLabel(self, text="Mot de passe de l'application").pack(pady=(15, 0))
        self.input_mdp = ctk.CTkEntry(self, width=300, show="*")
        self.input_mdp.pack(pady=5)

        # Champ mdp Gmail (visible uniquement en mode register)
        self.label_gmail = ctk.CTkLabel(self, text="Mot de passe d'application Gmail")
        self.input_mdp_gmail = ctk.CTkEntry(self, width=300, show="*", placeholder_text="xxxx xxxx xxxx xxxx")

        # Bouton principal (connexion/création)
        self.bouton_action = ctk.CTkButton(
            self,
            text="Se connecter",
            width=200,
            command=self._action_principale
        )
        self.bouton_action.pack(pady=20)

        # Bouton pour basculer entre les deux modes
        self.bouton_basculer = ctk.CTkButton(
            self,
            text="Pas de compte ? Créer un compte",
            width=300,
            fg_color="transparent",
            border_width=1,
            command=self._basculer_mode
        )
        self.bouton_basculer.pack(pady=5)

        # Message d'info/erreur
        self.label_message = ctk.CTkLabel(self, text="", text_color="orange")
        self.label_message.pack(pady=10)

    def _basculer_mode(self):
        if self.mode == "login":
            # Passer en mode création de compte
            self.mode = "register"
            self.label_mode.configure(text="Création de compte")
            self.bouton_action.configure(text="Créer le compte")
            self.bouton_basculer.configure(text="Déjà un compte ? Se connecter")
            # Afficher le champ mdp Gmail
            self.label_gmail.pack(pady=(15, 0), before=self.bouton_action)
            self.input_mdp_gmail.pack(pady=5, before=self.bouton_action)
        else:
            # Passer en mode login
            self.mode = "login"
            self.label_mode.configure(text="Connexion")
            self.bouton_action.configure(text="Se connecter")
            self.bouton_basculer.configure(text="Pas de compte ? Créer un compte")
            self.label_gmail.pack_forget()
            self.input_mdp_gmail.pack_forget()

        self.label_message.configure(text="")

    def _action_principale(self):
        email = self.input_email.get().strip()
        mdp = self.input_mdp.get().strip()

        if not email or not mdp:
            self.label_message.configure(text="Remplis tous les champs.", text_color="orange")
            return

        if self.mode == "register":
            mdp_gmail = self.input_mdp_gmail.get().strip()
            if not mdp_gmail:
                self.label_message.configure(text="Mot de passe Gmail requis.", text_color="orange")
                return

            succes, info = auth.creer_compte(email, mdp, mdp_gmail)
            if succes:
                self.user_id = info
                self.email = email
                self.mdp_gmail = mdp_gmail
                self.destroy()
            else:
                self.label_message.configure(text=info, text_color="red")
        else:
            succes, info, mdp_gmail = auth.se_connecter(email, mdp)
            if succes:
                self.user_id = info
                self.email = email
                self.mdp_gmail = mdp_gmail
                self.destroy()
            else:
                self.label_message.configure(text=info, text_color="red")