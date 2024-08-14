import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
from datetime import datetime
from database.DatabaseManager import DatabaseManager


def create_histogram(data):
    # Vérifier la présence des colonnes 'jump_type' et 'jump_success' (tableau incomplet)
    if 'jump_type' not in data.columns or 'jump_success' not in data.columns:
        st.error("Cet entraînement ne contient pas les informations nécessaires.")
        return
    
    # Compter le nombre de réussites et d'échecs par type de saut (réussite : jump_success = 'true', échec : jump_success = 'false')
    jump_stats = data.groupby(['jump_type', 'jump_success']).size().unstack(fill_value=0)

    # Vérifier la présence des colonnes True et False
    if True not in jump_stats.columns:
        jump_stats[True] = 0
    if False not in jump_stats.columns:
        jump_stats[False] = 0

    # Préparer les données pour le graphique
    x_axis = jump_stats.index.tolist()
    success_data = jump_stats[True].tolist()
    fail_data = jump_stats[False].tolist()


    options = {
        "title": {"text": "Répartition des sauts par type"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "category", "data": x_axis},
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "Réussi",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": success_data,
                "color": "green"
            },
            {
                "name": "Chute",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": fail_data,
                "color": "red"
            }
        ]
    }
    # add an on click event to the chart
    options["events"] = [{"click": "function(params) {alert('You clicked on ' + params.value)}"}]

    st_echarts(options, height="500px")
    


        
def create_timeline(df):
    # Conversion des timestamps en objets datetime
    df['jump_time'] = df['jump_time'].apply(lambda x: datetime.strptime(x, '%M:%S'))

    # Création du graphique Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['jump_time'],
        y=df['jump_rotations'],
        mode='markers',
        marker=dict(
            color=df['jump_success'].map({False: 'red', True: 'green'}),
            size=10
        ),
        text=df.apply(lambda row: f"Type de saut: {row['jump_type']}<br>Réussi: {row['jump_success']}<br>Rotations: {row['jump_rotations']}<br>Timestamp: {row['jump_time']}", axis=1),
        hoverinfo='text'
    ))

    # Conversion de l'axe des abscisses en format de temps
    fig.update_xaxes(tickformat="%M:%S")

    fig.update_layout(
        xaxis_title='Timestamp (min:sec)',
        yaxis_title='Rotations',
        title='Timeline de l\'entrainement'
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig)

# Initialisation de la base de données
db_manager = DatabaseManager()

if st.session_state.logged_in:
    # récupérer les access de l'utilisateur
    access = st.session_state.user['access']
    role = st.session_state.user['role']

    if role == 'COACH':
        # Afficher une liste déroulante pour sélectionner un athlète
        selected_athlete = st.sidebar.selectbox("Sélectionner un athlète", access)
        if selected_athlete:
            # Récupérer les entraînements de l'athlète sélectionné
            trainings = db_manager.get_all_trainings_for_skater(selected_athlete)
        else:
            st.error("Aucun athlète sélectionné.")
            st.stop()
    elif role == 'ATHLETE':
        # Récupérer les entraînements de l'utilisateur (athlète)
        trainings = db_manager.get_all_trainings_for_skater(access)

    # Récupérer la date qui est en format secondes depuis 1970 et la convertir en format date
    training_dates = [datetime.fromtimestamp(training.training_date) for training in trainings]
    # Afficher la selectbox avec les dates des entraînements
    selected_date = st.sidebar.selectbox("Date de l'entraînement", training_dates)
    # Récupérer les données de l'entraînement sélectionné
    selected_date_timestamp = int(selected_date.timestamp())
    training_id = trainings[training_dates.index(selected_date)].training_id
    training_data = db_manager.load_training_data(training_id)
    # Faire de ces données un DataFrame
    df = pd.DataFrame([jump.to_dict() for jump in training_data])
    # Ajouter un filtre sur les rotations dans la sidebar
    selected_rotations = st.sidebar.slider("Nombre de rotations", 0, 4, (0, 4))
    df_hist = df[(df['jump_rotations'] >= selected_rotations[0]) & (df['jump_rotations'] <= selected_rotations[1])]
    # Créer le graphique histogramme
    create_histogram(df_hist)
    # Créer le graphique timeline
    create_timeline(df)
else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()