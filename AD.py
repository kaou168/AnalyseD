import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

@st.cache_data
def load_data():
    return pd.read_csv("dataset_fin.csv")

df = load_data()

# 1. Titre de l'application

st.title("📊 Explorateur du Dataset Assurance & Climat")
st.write(f"Nombre de lignes : {df.shape[0]}")
st.write(f"Nombre de colonnes : {df.shape[1]}")


# 2. Sélection de colonnes à afficher

colonnes_selectionnees = st.multiselect(
    "Sélectionnez les colonnes à afficher :", df.columns.tolist(), default=["claim_nb", "claim_amount", "TX", "RR"], key="colonnes_affichage"
)

if colonnes_selectionnees:
    st.dataframe(df[colonnes_selectionnees].head(100))


# 3. Statistiques descriptives


if st.checkbox("Afficher les statistiques descriptives"):
    st.write(df[colonnes_selectionnees].describe())


# 4. Filtrage par variable numérique

st.subheader("Filtrer par une variable numérique")
col_num = st.selectbox("Choisissez une variable numérique :", df.select_dtypes(include=["float64", "int64"]).columns, key="variable_num")

min_val = float(df[col_num].min())
max_val = float(df[col_num].max())

if min_val < max_val:
    val_range = st.slider("Plage de valeurs :", min_value=min_val, max_value=max_val, value=(min_val, max_val), key="plage_valeurs")
    df_filtré = df[df[col_num].between(val_range[0], val_range[1])]
    st.write(f"Nombre d'observations après filtrage : {df_filtré.shape[0]}")
    st.dataframe(df_filtré.head(50))
    st.download_button("📅 Télécharger les données filtrées",
                       data=df_filtré.to_csv(index=False).encode("utf-8"),
                       file_name="donnees_filtrees.csv",
                       mime="text/csv")
else:
    st.warning("⚠ La variable sélectionnée contient une seule valeur. Le filtrage est désactivé.")




# 5. Carte géographique des sinistres

st.subheader("🗺️ Répartition géographique des sinistres")
if set(["LAT", "LON", "claim_nb"]).issubset(df.columns):
    df_geo = df.dropna(subset=["LAT", "LON", "claim_nb"])
    fig_map = px.scatter_mapbox(
        df_geo, lat="LAT", lon="LON", size="claim_nb", color="claim_nb",
        color_continuous_scale="OrRd", zoom=5,
        mapbox_style="carto-positron",
        hover_name="pol_insee_code",
        title="Nombre de sinistres par localisation"
    )
    st.plotly_chart(fig_map)
else:
    st.warning("⚠ Les colonnes LAT, LON ou claim_nb sont manquantes pour générer la carte.")


# 6. Graphiques d'analyse descriptive

st.subheader("📈 Analyse Graphique Descriptive")

# Histogramme
st.write("### Histogramme d'une variable")
var_hist = st.selectbox("Choisissez une variable pour l'histogramme :", df.select_dtypes(include=["float64", "int64"]).columns, key="histogramme")
fig_hist = px.histogram(df, x=var_hist, nbins=30, title=f"Histogramme de {var_hist}")
st.plotly_chart(fig_hist)

# Boxplot
st.write("### Boxplot d'une variable")
var_box = st.selectbox("Choisissez une variable pour le boxplot :", df.select_dtypes(include=["float64", "int64"]).columns, key="boxplot")
fig_box = px.box(df, y=var_box, title=f"Boxplot de {var_box}")
st.plotly_chart(fig_box)

# Heatmap de corrélation
st.write("### Heatmap de Corrélation")
if st.button("Afficher la Heatmap de corrélation"):
    corr = df.select_dtypes(include=["float64", "int64"]).corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# Pairplot (optionnel car peut être lourd si beaucoup de variables)
st.write("### Matrice de scatterplots (Pairplot)")
colonnes_pairplot = st.multiselect("Sélectionnez quelques variables :", df.select_dtypes(include=["float64", "int64"]).columns.tolist(), key="pairplot")

if colonnes_pairplot:
    st.info("⚡ Attention : le Pairplot peut être lent si trop de variables sont sélectionnées.")
    fig = sns.pairplot(df[colonnes_pairplot])
    st.pyplot(fig)
