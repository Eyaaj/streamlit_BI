import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
from PIL import Image
import urllib.request
import plotly.graph_objects as go
import json
import requests
import geopandas as gpd
image = Image.open('34921.jpg')
st.image(image)

# Ajout du paragraphe "Présentation" dans le corps de la page
st.subheader("Présentation")
st.write("*Vous souhaitez connaître la consommation d’énergie et/ou de gaz sur différents périmètres géographiques en France ?*")
st.write("L'utilisation de cette datavisualisation vous permettera une meilleure visualisation  de la consommation de gaz et/ou d'électricité ainsi que le nombre de points de livraison par secteur d'activités (industrie, tertiaire, résidentiel, agriculture) sur le périmètre géographique sélectionné.")


# Chargement du tableau
url = "https://www.data.gouv.fr/fr/datasets/r/d33eabc9-e2fd-4787-83e5-a5fcfb5af66d"

try:
    # Vérifier si l'URL est disponible
    urllib.request.urlopen(url)
    # Si l'URL est disponible, charger le contenu du fichier csv
    df = pd.read_csv(url)
except:
    # Si l'URL n'est pas disponible, charger le contenu du fichier local
    df = pd.read_csv("conso-elec-gaz-annuelle-par-naf-agregee-region.csv",sep=";", encoding='latin-1')


df['libelle_categorie_consommation'] = df['libelle_categorie_consommation'].replace('0', 'categorie inconnu')
# Convertir les valeurs de la colonne 'annee' en format 'YYYY'
df['annee'] = df['annee'].astype(str).str[:4]

# Convertir la colonne 'annee' en type datetime
df['annee'] = pd.to_datetime(df['annee'], format='%Y')

# Changer le format de la colonne 'annee' en année (YYYY)
df['annee'] = df['annee'].dt.strftime('%Y')
st.dataframe(df)


# Création d'un sous-dataframe pour le nombre d'opérateurs par filière
df_operateurs = df.groupby(['filiere'])['operateur'].nunique().reset_index()


# Création du graphique camembert
fig2 = go.Figure(data=[go.Pie(labels=df_operateurs['filiere'], values=df_operateurs['operateur'])])
fig2.update_layout(title='Nombre d\'opérateurs par filière')

# Regroupement des données par région et calcul de la consommation totale
df_conso_region = df.groupby("libelle_region")["conso"].sum()

# Obtenir les cinq régions les plus consommatrices
top_regions = df_conso_region.nlargest(5).index.tolist()

# Filtrer le DataFrame pour inclure uniquement les cinq régions les plus consommatrices
df_top_regions = df[df["libelle_region"].isin(top_regions)]

# Calculer la consommation totale par région pour les cinq régions les plus consommatrices
df_conso_top_regions = df_top_regions.groupby("libelle_region")["conso"].sum()

# Créer l'histogramme avec des couleurs différentes pour chaque barre
fig3, ax = plt.subplots()
ax.bar(df_conso_top_regions.index, df_conso_top_regions.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])

# Espacer l'axe des abscisses
plt.subplots_adjust(bottom=0.2)

# Ajouter des étiquettes et des titres
plt.title("Consommation totale par région (Top 5)")
plt.xlabel("Région")
plt.ylabel("Consommation totale (kWh)")
# Faire pivoter les noms des axes des abscisses
plt.xticks(rotation=90)

# Afficher le graphique camembert avec un titre distinct
st.subheader("Graphique Camembert : Nombre d'opérateurs par filière")
st.plotly_chart(fig2)

# Afficher l'histogramme avec un titre distinct
st.subheader("Graphique Histogramme : Consommation totale par région (Top 5)")
st.pyplot(fig3)



# Options de visualisation
options = ["Histogramme", "Camembert"]
selected_option = st.selectbox("Choisissez une option de visualisation", options)

if selected_option == "Histogramme":
    # Filtrer les données pour l'énergie et le gaz
    df_energie = df[df["filiere"] == "Electricité"]
    df_gaz = df[df["filiere"] == "Gaz"]

    # Couleurs
    couleur_energie = "orange"
    couleur_gaz = "blue"

    # Créer la figure
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_energie["annee"], y=df_energie["conso"], name="Électricité", marker=dict(color=couleur_energie)))
    fig.add_trace(go.Bar(x=df_gaz["annee"], y=df_gaz["conso"], name="Gaz", marker=dict(color=couleur_gaz)))
    fig.update_layout(title="Consommation d'énergie et de gaz au fil des années - Histogramme", xaxis_title="Année", yaxis_title="Consommation")

elif selected_option == "Camembert":
    # Filtrer les données pour l'énergie et le gaz
    df_energie = df[df["filiere"] == "Electricité"]
    df_gaz = df[df["filiere"] == "Gaz"]

    # Couleurs
    couleur_energie = "orange"
    couleur_gaz = "blue"

    total_energie = df_energie["conso"].sum()
    total_gaz = df_gaz["conso"].sum()

    fig = go.Figure(data=[go.Pie(labels=["Électricité", "Gaz"], values=[total_energie, total_gaz],
                                marker=dict(colors=[couleur_energie, couleur_gaz]))])
    fig.update_layout(title="Répartition de la consommation d'énergie et de gaz", showlegend=False)
st.plotly_chart(fig)



import streamlit.components.v1 as components

# Ajouter la question pour approfondir l'analyse dans la barre latérale
approfondir_analyse = st.radio("Souhaitez-vous approfondir l'analyse en vous focalisant sur les différentes régions de la France ?", ("Oui", "Non"), index=1)

if approfondir_analyse == "Oui":
    # Ajout du titre dans le menu de gauche
    st.sidebar.title("Consommations locales d’Energie et de Gaz 💡 ")

    # Filtrer les données
    selected_annee = st.sidebar.selectbox("Filtrer par année", df['annee'].unique())
    filtered_df = df[df['annee'] == selected_annee]
    selected_filiere = st.sidebar.selectbox("Filtrer par filière", df['filiere'].unique())
    selected_grand_secteur = st.sidebar.selectbox("Filtrer par grand secteur", df['libelle_grand_secteur'].unique())
    selected_region = st.sidebar.selectbox("Filtrer par région", df['libelle_region'].unique())

    # Croisement entre "libelle_grand_secteur" et "pdl"
    sector_pdl_counts = filtered_df.groupby("libelle_grand_secteur")['pdl'].count().reset_index()
    sector_pdl_counts = sector_pdl_counts.rename(columns={'pdl': 'Nombre de points de livraison'})

    # Identifier les secteurs d'activité avec le plus grand nombre de points de livraison
    top_sectors = sector_pdl_counts.nlargest(5, 'Nombre de points de livraison')

    # Affichage du tableau récapitulatif des secteurs avec le plus grand nombre de points de livraison
    st.write("Secteurs d'activité avec le plus grand nombre de points de livraison :")
    st.table(top_sectors)

    # Création du graphique à barres pour la répartition des points de livraison par grand secteur d'activité
    fig_bar = px.bar(sector_pdl_counts, x='libelle_grand_secteur', y='Nombre de points de livraison',
                     labels={'libelle_grand_secteur': 'Grand secteur d\'activité',
                             'Nombre de points de livraison': 'Nombre de points de livraison'},
                     title='Répartition des points de livraison par grand secteur d\'activité')

    # Affichage du graphique à barres dans Streamlit
    st.plotly_chart(fig_bar)

   # Croisement entre "filiere" et "conso"
    filiere_conso_mean = filtered_df[filtered_df['libelle_grand_secteur'] == selected_grand_secteur].groupby("filiere")['conso'].mean().reset_index()
    filiere_conso_mean = filiere_conso_mean.rename(columns={'conso': 'Consommation moyenne'})
# Affichage en gras de la phrase
    st.markdown("**Comparaison des niveaux de consommation entre les différentes filières :**")

# Création des images pour les filières
    electricite_img = Image.open("bulb.png")
    gaz_img = Image.open("gas.png")

# Affichage des moyennes de consommation et des images pour les filières
    col1, col2 = st.columns(2)
    with col1:
       st.image(electricite_img, caption="Electricité", width=50, use_column_width=True)
       st.write("**Consommation moyenne :**", round(filiere_conso_mean[filiere_conso_mean['filiere'] == "Electricité"]['Consommation moyenne'].values[0], 2))
    with col2:
       st.image(gaz_img, caption="Gaz", width=50, use_column_width=True)
       st.write("**Consommation moyenne :**", round(filiere_conso_mean[filiere_conso_mean['filiere'] == "Gaz"]['Consommation moyenne'].values[0], 2))

else:
    # Afficher un message de remerciement
    st.write("Merci d'avoir utilisé l'application. A Bientot!")


# Lien vers LinkedIn
linkedin_url = 'https://www.linkedin.com/in/eya-jamoussi-98b3371b1'

# Lien vers GitHub
github_url = 'https://github.com/Eyaaj'

# Afficher les liens
st.markdown('### Liens utiles')
st.markdown(f'- [LinkedIn]({linkedin_url})')
st.markdown(f'- [GitHub]({github_url})')

container = st.container()
with container:

        # Contenu de la page de la carte
        st.write("Carte des prix des loyers par région :")

        # Charger le fichier GeoJSON des régions
        geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/regions.geojson'

        # Créer une carte interactive avec Plotly Express
        fig = px.choropleth_mapbox(df_conso_region, geojson=geojson_url, color="loypredm2",
                           locations="REG", featureidkey="properties.code",
                           center={"lat": 46.2276, "lon": 2.2137}, zoom=5,
                           mapbox_style="carto-positron",
                           color_continuous_scale="Reds")
        # Afficher la carte
        st.plotly_chart(fig, use_container_width=True)
