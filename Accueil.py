import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from database.DatabaseManager import DatabaseManager
import hashlib
import re

st.set_page_config(
    page_title="Inscription/Connexion",
    page_icon=":lock:",
)

st.title("Welcome to SynergieViz")

# Initialisation de Firebase Admin
db = DatabaseManager()

# Fonction pour vérifier les identifiants
def login(email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = db.get_user_by_email(email)
    if user and user.get("password") == hashed_password:
        return user
    else:
        return False

# Fonction pour vérifier le format de l'email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# Fonction pour vérifier la validité du mot de passe
def is_valid_password(password):
    return len(password) >= 6

# Initialiser les variables de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Si l'utilisateur est connecté, afficher la page de profil
if st.session_state.logged_in:
    st.title("Profil")
    st.write(f"Bienvenue {st.session_state.user['name']} !")
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()
    if st.session_state.user['role'] == 'COACH':
        if st.session_state.user['access']:
            st.write(f"Vos athlètes : {st.session_state.user['access']}")
        else:
            st.write("Vous n'avez pas d'athlète attitrés. Faites-leur créer un compte !")
    elif st.session_state.user['role'] == 'ATHLETE':
        if st.session_state.user['coaches']:
            st.write(f"Vos coachs : {st.session_state.user['coaches']}")
        else:
            st.write("Vous n'avez pas de coach attitré. Ajoutez en un !")

        updated_coaches = st.multiselect("Ajouter ou supprimer un coach", db.get_all_coaches_name(), default=st.session_state.user['coaches'])
        if st.button("Enregistrer"):
            db.update_coaches(updated_coaches, st.session_state.user['name'])
            st.session_state.user['coaches'] = updated_coaches
            st.experimental_rerun()

else:
    # Formulaire de sélection entre inscription et connexion
    mode = st.selectbox("Que souhaitez-vous faire ?", ["Inscription", "Connexion"])

    if mode == "Inscription":
        # Formulaire d'inscription
        st.title("Inscription")

        role = st.selectbox("Rôle", ["COACH", "ATHLETE"])
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")   
        name = st.text_input("Nom")

        if role == "ATHLETE":
            # Récupérer la liste des coachs
            all_coaches = db.get_all_coaches_name()
            # Multi-select pour choisir les coachs
            coaches = st.multiselect("Choisir les coachs", all_coaches)
            access = name
        else:
            access = ''
            coaches = []
        
        if st.button("Enregistrer"):
            # Vérifier le format de l'email
            if not is_valid_email(email):
                st.error("Veuillez entrer un email valide.")
            # Vérifier la validité du mot de passe
            elif not is_valid_password(password):
                st.error("Le mot de passe doit faire au moins 6 caractères.")
            # Vérifier si l'email est déjà utilisé
            elif db.check_if_user_exists_by_email(email):
                st.error("Cet email est déjà utilisé.")
            else:
                # Créer un nouveau document dans la collection "users"
                db.create_user(email, password, role, name, access, coaches)
                for coach in coaches:
                    db.add_athlete_to_coach_access(coach, name)
                st.success("Compte enregistré avec succès !")

    elif mode == "Connexion":
        # Formulaire de connexion
        st.title("Connexion")

        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            user = login(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Connexion réussie !")
                st.experimental_rerun()
            else:
                st.error("Email ou mot de passe incorrect.")