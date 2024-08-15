import streamlit as st
import pandas as pd
from database.DatabaseManager import DatabaseManager
from datetime import datetime

db_manager = DatabaseManager()

def color_background(val):
    if val == "":
        return ''
    val = float(val.strip('%'))  # Convertir le pourcentage en nombre flottant
    if val >= 85:
        color = 'green'
    elif val >= 60:
        color = 'yellow'
    else:
        color = 'red'
    return f'background-color: {color}'

def create_recap_frame(data):
    # Création du DataFrame récapitulatif : une colonne par type de saut, une ligne par nombre de rotations (1, 2, 3 et 4). Dans les cases, le pourcentage de réussite d'un tel saut (type + rotations)
    recap = pd.DataFrame(index=[1, 2, 3, 4], columns=data['jump_type'].unique())
    # Arrondir le nombre de rotations aux valeurs entières
    data['jump_rotations'] = data['jump_rotations'].round()
    for jump_type in data['jump_type'].unique():
        for rotations in [1, 2, 3, 4]:
            # Calcul du pourcentage de réussite
            success_rate = data[(data['jump_type'] == jump_type) & (data['jump_rotations'] == rotations)]['jump_success'].mean()
            # Laisser la case vide si aucune donnée n'est disponible
            if pd.isna(success_rate):
                success_rate = ""
            # Remplir la case du DataFrame récapitulatif en pourcentage (bien ecrire le signe %)
            recap.loc[rotations, jump_type] = f"{success_rate:.0%}" if success_rate != "" else ""
    # Affichage du DataFrame récapitulatif
    styled_recap = recap.style.applymap(color_background)

    st.markdown("### Pourcentage de réussite par type de saut et par nombre de rotations")
    st.write(styled_recap)

if st.session_state.logged_in:
    access = st.session_state.user['access']
    role = st.session_state.user['role']

    if role == 'COACH':
        selected_athlete = st.sidebar.selectbox("Sélectionner un athlète", access)
        if selected_athlete:
            trainings = db_manager.get_all_trainings_for_skater(selected_athlete)
        else:
            st.error("Aucun athlète sélectionné.")
            st.stop()

    elif role == 'ATHLETE':
        trainings = db_manager.get_all_trainings_for_skater(access)

    training_dates = [datetime.fromtimestamp(training.training_date) for training in trainings]
    # Faire un slider pour sélectionner tous les entrainements entre deux dates
    selected_dates = st.sidebar.slider("Sélectionner une période", min_value=min(training_dates), max_value=max(training_dates), value=(min(training_dates), max(training_dates)))
    # Filtrer les entrainements entre les deux dates sélectionnées
    trainings = [training for training in trainings if selected_dates[0] <= datetime.fromtimestamp(training.training_date) <= selected_dates[1]]
    # Récupérer les données de ces entrainements
    all_data = []
    for training in trainings:
        training_data = db_manager.load_training_data(training.training_id)
        all_data.extend([jump.to_dict() for jump in training_data])
    df = pd.DataFrame(all_data)
    # Si jump_rotations est ,5 on arrondit à l'entier inférieur (pour les AXEL)
    df['jump_rotations'] = df['jump_rotations'].apply(lambda x: int(x) if x.is_integer() else int(x-0.5))
    create_recap_frame(df)
else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()