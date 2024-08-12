from features.dataImport import data_import
import streamlit as st
import pandas as pd

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
    recap = pd.DataFrame(index=[1, 2, 3, 4], columns=data['type'].unique())
    # Arrondir le nombre de rotations aux valeurs entières
    data['rotations'] = data['rotations'].round()
    for jump_type in data['type'].unique():
        for rotations in [1, 2, 3, 4]:
            # Calcul du pourcentage de réussite
            success_rate = data[(data['type'] == jump_type) & (data['rotations'] == rotations)]['success'].mean()
            # Laisser la case vide si aucune donnée n'est disponible
            if pd.isna(success_rate):
                success_rate = ""
            # Remplir la case du DataFrame récapitulatif en pourcentage (bien ecrire le signe %)
            recap.loc[rotations, jump_type] = f"{success_rate:.0%}" if success_rate != "" else ""
    # Affichage du DataFrame récapitulatif
    styled_recap = recap.style.applymap(color_background)

    st.markdown("### Pourcentage de réussite par type de saut et par nombre de rotations")
    st.write(styled_recap)

data = data_import()
create_recap_frame(data)