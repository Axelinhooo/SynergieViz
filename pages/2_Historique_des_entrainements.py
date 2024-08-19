import streamlit as st
import pandas as pd
from database.DatabaseManager import DatabaseManager
from datetime import datetime
import math

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
    # arrondir les jump_rotations à l'entier inférieur (pour les jump_type == AXEL)
    data['jump_rotations'] = data.apply(lambda row: 
                                   math.floor(row['jump_rotations']) 
                                   if row['jump_type'] == 'AXEL' and str(row['jump_rotations']).endswith('.5') 
                                   else row['jump_rotations'], 
                                   axis=1)
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
    if st.session_state.user['role'] == 'COACH':
        # Create the Streamlit selectbox
        selected_skater = st.sidebar.selectbox("Select a skater", st.session_state.skater_names)
        if selected_skater:
            # Find the corresponding skater ID based on the selected name
            selected_skater_id = st.session_state.skater_ids[st.session_state.skater_names.index(selected_skater)]
        else:
            st.error("Aucun athlète sélectionné.")
            st.stop()
        
        skater_index = st.session_state.skater_ids.index(selected_skater_id)
        
    elif st.session_state.user['role'] == 'ATHLETE':
        skater_index = 0
    
    trainings = st.session_state.trainings[skater_index]
    trainings["training_date"] = pd.to_datetime(trainings["training_date"], unit="s")

    jumps = st.session_state.jumps[skater_index]
    create_recap_frame(jumps)



else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()