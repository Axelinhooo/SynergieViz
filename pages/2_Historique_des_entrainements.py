import math
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from streamlit_date_picker import date_range_picker, date_picker, PickerType

from database.DatabaseManager import DatabaseManager

db_manager = DatabaseManager()


def color_background(val):
    if val == "":
        return ""
    val = float(val.strip("%"))  # Convertir le pourcentage en nombre flottant
    # Dégradé : 100% -> #00d900, 0% -> #d90000, 50% -> #d9d900 : faire le dégradé entre les couleurs
    r = int(217 - (217 * val) / 100)
    g = int(217 * val / 100)
    b = 0
    return f"background-color: #{r:02x}{g:02x}{b:02x}"

def test_color_background():
    # Faire un tableau avec des valeurs de 0 à 100 par pas de 10
    test_df = pd.DataFrame(
        {
            "0": [f"{i}%" for i in range(0, 101, 10)],
            "1": [f"{i}%" for i in range(0, 101, 10)],
            "2": [f"{i}%" for i in range(0, 101, 10)],
            "3": [f"{i}%" for i in range(0, 101, 10)],
        }
    )
    # Appliquer la fonction color_background à chaque cellule du DataFrame
    styled_test_df = test_df.style.applymap(color_background)
    return styled_test_df


def create_recap_frame(data):
    # Création du DataFrame récapitulatif : une colonne par type de saut, une ligne par nombre de rotations (Simple, Double, Triple, Quad)
    recap = pd.DataFrame(index=["Simple", "Double", "Triple", "Quad"], columns=data["jump_type"].unique())
    
    # Arrondir les jump_rotations à l'entier inférieur (pour les jump_type == AXEL)
    data["jump_rotations"] = data.apply(
        lambda row: (
            math.floor(row["jump_rotations"])
            if row["jump_type"] == "AXEL" and str(row["jump_rotations"]).endswith(".5")
            else row["jump_rotations"]
        ),
        axis=1,
    )
    
    # Dictionnaire pour mapper les noms des rotations
    rotation_mapping = {1: "Simple", 2: "Double", 3: "Triple", 4: "Quad"}

    for jump_type in data["jump_type"].unique():
        for rotations in [1, 2, 3, 4]:
            # Calcul du pourcentage de réussite
            success_rate = data[
                (data["jump_type"] == jump_type) & (data["jump_rotations"] == rotations)
            ]["jump_success"].mean()
            # Laisser la case vide si aucune donnée n'est disponible
            if pd.isna(success_rate):
                success_rate = ""
            # Remplir la case du DataFrame récapitulatif en pourcentage (bien écrire le signe %)
            recap.loc[rotation_mapping[rotations], jump_type] = (
                f"{success_rate:.0%}" if success_rate != "" else ""
            )

    # Classer les colonnes : Axel, Salchow, Toe Loop, Loop, Flip, Lutz
    recap = recap[
        [
            "AXEL",
            "SALCHOW",
            "TOE_LOOP",
            "LOOP",
            "FLIP",
            "LUTZ",
        ]
    ]
    
    # Affichage du DataFrame récapitulatif
    styled_recap = recap.style.applymap(color_background)

    st.markdown(
        "### Pourcentage de réussite par type de saut et par nombre de rotations"
    )
    st.write(styled_recap)

def create_recap_total(data):
    # Creer un tableau qui contient le nombre de sauts par type et par nombre de rotations
    recap = pd.DataFrame(index=["Simple", "Double", "Triple", "Quad"], columns=data["jump_type"].unique())

    # Arrondir les jump_rotations à l'entier inférieur (pour les jump_type == AXEL)
    data["jump_rotations"] = data.apply(
        lambda row: (
            math.floor(row["jump_rotations"])
            if row["jump_type"] == "AXEL" and str(row["jump_rotations"]).endswith(".5")
            else row["jump_rotations"]
        ),
        axis=1,
    )

    # Dictionnaire pour mapper les noms des rotations
    rotation_mapping = {1: "Simple", 2: "Double", 3: "Triple", 4: "Quad"}

    for jump_type in data["jump_type"].unique():
        for rotations in [1, 2, 3, 4]:
            # Calcul du nombre de sauts
            count = data[
                (data["jump_type"] == jump_type) & (data["jump_rotations"] == rotations)
            ].shape[0]
            # Laisser la case vide si aucune donnée n'est disponible
            if pd.isna(count):
                count = ""
            # Remplir la case du DataFrame récapitulatif en pourcentage (bien écrire le signe %)
            recap.loc[rotation_mapping[rotations], jump_type] = count

    # Classer les colonnes : Axel, Salchow, Toe Loop, Loop, Flip, Lutz
    recap = recap[
        [
            "AXEL",
            "SALCHOW",
            "TOE_LOOP",
            "LOOP",
            "FLIP",
            "LUTZ",
        ]
    ]


    st.markdown(
        "### Nombre de sauts par type de saut et par nombre de rotations"
    )
    st.write(recap)


if "logged_in" in st.session_state:
    if st.session_state.logged_in:
        if st.session_state.user["role"] == "COACH":
            selected_skater = st.sidebar.selectbox(
                "Sélectionner un athlète", st.session_state.skater_names
            )
            if not selected_skater:
                st.error("Aucun athlète sélectionné.")
                st.stop()

        elif st.session_state.user["role"] == "ATHLETE":
            selected_skater = st.session_state.user["name"]

        for i in st.session_state.jumps:
            if selected_skater == i["skater_name"][0]:
                jumps = i
                break

        default_start, default_end = datetime.now() - timedelta(days=365), datetime.now()
        refresh_value = timedelta(days=365)
        st.markdown("### Sélectionner une période")
        date_range_string = date_range_picker(picker_type=PickerType.date,
                                            start=default_start, end=default_end,
                                            key='date_range_picker',
                                            refresh_button={'is_show': True, 'button_name': 'Sélectionner la dernière année',
                                                            'refresh_value': refresh_value})
        if date_range_string:
            start, end = date_range_string

        jumps    
        # Filtrer les sauts par date
        jumps_filtered = jumps[(jumps["training_date"] >= start) & (jumps["training_date"] <= end)]
        
        if jumps_filtered.empty:
            st.error("Aucun saut n'a été enregistré pour cette période.")
        else:
            create_recap_frame(jumps_filtered)
            create_recap_total(jumps_filtered)
        
    
        
    else:
        st.error("Vous devez être connecté pour accéder à cette page.")
        st.stop()
else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()
