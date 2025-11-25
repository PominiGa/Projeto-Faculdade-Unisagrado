import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard COVID-19 Brasil", layout="wide")
st.title("📊 Dashboard COVID-19 Brasil - Brasil (Brasil.io)")

url = "https://data.brasil.io/dataset/covid19/caso_full.csv.gz"

df = pd.read_csv(url, compression="gzip")

df = df[df["place_type"] == "state"]

df.rename (columns={
    "Estado": "Estado",
    "date": "data",
    "last_available_confirmed": "casos_confirmados",
    "last_available_deaths": "óbitos_confirmados",
}, inplace=True)

df["data"] = pd.to_datetime(df["data"])

latest_date = df["data"].max()
df_latest = df[df["data"] == latest_date]

st.markdown(f"### Dados mais recentes: {latest_date.date()}**")

col1, col2, col3 = st.columns(3)

col1.metric("Total de casos", f"{int(df_latest["casos_confirmados"].sum()):,}".replace(",", "."))
col2.metric("Total de óbitos", f"{int(df_latest["óbitos_confirmados"].sum()):,}".replace(",", "."))
col3.metric("Estados Registrados", len(df_latest))

st.divider()

estados = sorted(df_latest["state"].unique())
estado_selecionado = st.selectbox("Selecione o Estado", estados)

filtro = df[df["state"] == estado_selecionado]

fig1 = px.line(filtro, x="data", y="casos_confirmados", title=f"Evolução de Casos - {estado_selecionado}")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(filtro, x="data", y="óbitos_confirmados", title=f"Óbitos Acumulados - {estado_selecionado}")
st.plotly_chart(fig2, use_container_width=True)

st.divider()