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

import streamlit as st
import pandas as pd

@st.cache_data
def load_data(skater_id):
    # Charger les trainings de l'athlète sélectionné
    trainings = db.get_all_trainings_for_skater(skater_id)
    
    # Créer un dataframe pour les trainings
    training_df = pd.DataFrame([vars(t) for t in trainings])
    
    # Charger les jumps liés à ces trainings
    jump_data = []
    for training in trainings:
        jump_ids = training.training_jumps
        for jump_id in jump_ids:
            jump = db.get_jump_by_id(jump_id)
            jump_data.append({
                "jump_length": jump.jump_length,
                "jump_max_speed": jump.jump_max_speed,
                "jump_rotations": jump.jump_rotations,
                "jump_success": jump.jump_success,
                "jump_time": jump.jump_time,
                "jump_type": jump.jump_type,
                "training_id": jump.training_id
            })
    
    # Créer un dataframe pour les jumps
    jump_df = pd.DataFrame(jump_data)
    
    return training_df, jump_df


# Initialiser les variables de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'trainings' not in st.session_state:
    st.session_state.trainings = None
if 'jumps' not in st.session_state:
    st.session_state.jumps = None
if 'skater_names' not in st.session_state:
    st.session_state.skater_names = None
if 'skater_ids' not in st.session_state:
    st.session_state.skater_ids = None


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
            all_training_data = []
            all_jump_data = []
            for athlete in st.session_state.user['access']:
                training_df, jump_df = load_data(athlete)
                all_training_data.append(training_df)
                all_jump_data.append(jump_df)
            st.session_state.trainings = all_training_data
            st.session_state.jumps = all_jump_data
            all_skaters = db.get_all_skaters_from_access(st.session_state.user['access'])
            # Extract the skater names and IDs from the SkaterData objects
            st.session_state.skater_names = [skater.skater_name for skater in all_skaters]
            st.session_state.skater_ids = [skater.skater_id for skater in all_skaters]
        else:
            st.write("Vous n'avez pas d'athlète attitrés. Faites-leur créer un compte !")
    elif st.session_state.user['role'] == 'ATHLETE':
        training_df, jump_df = load_data(st.session_state.user['access'])
        st.session_state.trainings = [training_df]
        st.session_state.jumps = [jump_df]
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
        access = ''

        if role == "ATHLETE":
            # Récupérer la liste des coachs
            all_coaches = db.get_all_coaches_name()
            # Multi-select pour choisir les coachs
            coaches = st.multiselect("Choisir les coachs", all_coaches)
        else:
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
                new_ref = db.create_user(email, password, role, name, access, coaches)
                if role == "ATHLETE":
                    db.give_self_access(name)
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